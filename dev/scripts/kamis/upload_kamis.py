import asyncio
import math
import os
from datetime import date, datetime

import pandas as pd
from geoalchemy2 import WKTElement
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from farmbase import MarketPrice, Market, Commodity
from farmbase.config import settings

# from farmwise.settings import settings

# Create async DB engine and session
# DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/dbname"  # replace with actual
engine = create_async_engine(settings.sqlalchemy_database_uri)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def load_market_prices(df: pd.DataFrame):
    """
    Loads market price data from a pandas DataFrame into the database.
    Skips duplicates using ON CONFLICT DO NOTHING on (market_id, commodity_id, date).
    """
    async with AsyncSessionLocal() as session:
        try:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date

            print("Pre-loading existing Markets...")
            result = await session.execute(select(Market))
            market_lookup = {market.name: market for market in result.scalars().all()}
            print(f"Found {len(market_lookup)} existing markets.")

            print("Pre-loading existing Commodities...")
            commodity_lookup = {}
            result = await session.execute(select(Commodity))
            for commodity in result.scalars().all():
                sex_value = commodity.sex.value if commodity.sex else None
                commodity_lookup[(commodity.name, commodity.classification, commodity.grade, sex_value)] = commodity
            print(f"Found {len(commodity_lookup)} existing commodities.")

            rows_to_insert = []

            for _, row in df.iterrows():
                market_name = row["Market"]
                market_obj = market_lookup.get(market_name)
                if not market_obj:
                    print(f"Skipping: no market named '{market_name}'")
                    continue

                commodity_name = row["Commodity"]
                if pd.isna(commodity_name):
                    print(f"Skipping: no commodity name in row {row}")
                    continue

                classification = row["Classification"] if pd.notna(row["Classification"]) else None
                grade = row["Grade"] if pd.notna(row["Grade"]) else None
                sex_str = None if pd.isna(row["Sex"]) else row["Sex"].lower()
                commodity_key = (commodity_name, classification, grade, sex_str)
                commodity_obj = commodity_lookup.get(commodity_key)

                if not commodity_obj:
                    print(f"Skipping: no commodity with key {commodity_key}")
                    continue

                rows_to_insert.append({
                    "market_id": market_obj.id,
                    "commodity_id": commodity_obj.id,
                    "date": row["Date"],
                    "supply_volume": row["Supply Volume"] if pd.notna(row["Supply Volume"]) else None,
                    "wholesale_price": row["wholesale_price"] if pd.notna(row["wholesale_price"]) else None,
                    "wholesale_unit": row["wholesale_unit"] if pd.notna(row["wholesale_unit"]) else None,
                    "wholesale_ccy": row["wholesale_ccy"] if pd.notna(row["wholesale_ccy"]) else None,
                    "retail_price": row["retail_price"] if pd.notna(row["retail_price"]) else None,
                    "retail_unit": row["retail_unit"] if pd.notna(row["retail_unit"]) else None,
                    "retail_ccy": row["retail_ccy"] if pd.notna(row["retail_ccy"]) else None,
                })

            if rows_to_insert:
                stmt = insert(MarketPrice).values(rows_to_insert)
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=["market_id", "commodity_id", "date"]
                )
                await session.execute(stmt)

            await session.commit()
            print("✅ Successfully loaded all market prices (duplicates skipped).")

        except Exception as e:
            await session.rollback()
            print(f"❌ An error occurred: {e}. Rolled back transaction.")

async def batch_load_market_prices(df: pd.DataFrame, batch_size: int = 5000):
    """
    Splits the input DataFrame into smaller batches and loads them via load_market_prices().
    This avoids exceeding PostgreSQL's 32767 parameter limit.
    """
    total_rows = len(df)
    num_batches = math.ceil(total_rows / batch_size)

    print(f"Loading {total_rows} market prices in {num_batches} batches of {batch_size}...")

    for i in range(0, total_rows, batch_size):
        batch_df = df.iloc[i:i + batch_size]
        print(f"📦 Batch {i // batch_size + 1}/{num_batches}...")
        await load_market_prices(batch_df)


async def populate_commodities(_com):
    rows_to_insert = []

    for _, row in tqdm(_com.iterrows(), total=len(_com), desc="Preparing Commodities"):
        grade_value = None if pd.isna(row.Grade) else row.Grade
        classificatio_value = None if pd.isna(row.Classification) else row.Classification
        sex_value = None if pd.isna(row.Sex) else row.Sex.upper()

        rows_to_insert.append({
            "name": row.Commodity,
            "classification": classificatio_value,
            "grade": grade_value,
            "sex": sex_value,
        })

    async with AsyncSessionLocal() as session:
        stmt = insert(Commodity).values(rows_to_insert)
        stmt = stmt.on_conflict_do_nothing(
            index_elements=["name", "classification", "grade", "sex"]
        )
        await session.execute(stmt)
        await session.commit()
        print("✅ Finished populating commodities (duplicates skipped).")


async def populate_markets(_markets):
    rows_to_insert = []

    for _, row in tqdm(_markets.iterrows(), total=len(_markets), desc="Preparing Markets"):
        location_wkt = WKTElement(f"POINT({row.lon} {row.lat})", srid=4326)

        rows_to_insert.append({
            "name": row.market,
            "location": location_wkt
        })

    async with AsyncSessionLocal() as session:
        stmt = insert(Market).values(rows_to_insert)
        stmt = stmt.on_conflict_do_nothing(index_elements=["name"])

        await session.execute(stmt)
        await session.commit()

        print("✅ Finished populating markets (duplicates skipped).")


def load_all_excels_to_dataframe(from_date, directory_path="."):
    # Get all files in the directory
    files = os.listdir(directory_path)

    # Filter files that match the pattern and date
    matched_files = []
    for filename in files:
        if filename.startswith("kamis_") and filename.endswith(".xlsx"):
            try:
                date_str = filename[len("kamis_"):-len(".xlsx")]
                file_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if file_date >= from_date:
                    matched_files.append(filename)
            except ValueError:
                continue  # Skip files that don't have a valid date format

    # Sort the result if needed
    matched_files.sort()

    """Load and concatenate all kamis_*.xlsx files into a single DataFrame."""
    df_list = []

    for file in matched_files:
        try:
            df = pd.read_excel(os.path.join(directory_path, file))
            df["source_date"] = os.path.basename(file).split("_")[1].replace(".xlsx", "")
            df_list.append(df)
        except Exception as e:
            print(f"❌ Failed to read {file}: {e}")

    if df_list:
        combined_df = pd.concat(df_list, ignore_index=True)
        print(f"✅ Combined {len(df_list)} files into a DataFrame with {len(combined_df)} rows.")
        return combined_df
    else:
        print("⚠️ No valid Excel files found.")
        return pd.DataFrame()


async def load():
    df = load_all_excels_to_dataframe(
        from_date=date(2025, 6, 9),
        directory_path="/Users/markns/workspace/farmwise_data/kamis/market_prices/")

    # Replace all cells that contain only "-" (with or without surrounding whitespace) with None
    df.replace(r"^\s*-\s*$", pd.NA, regex=True, inplace=True)

    df2 = df[["Commodity", "Classification", "Grade", "Sex"]].drop_duplicates()
    df2 = df2[~df2.Commodity.isna()]

    await populate_commodities(df2)
    await populate_markets(pd.read_csv("markets.csv"))

    def split_price_column(df, column, prefix):
        """Split a 'price/unit' column into price, unit, and currency."""
        split_cols = df[column].str.split("/", expand=True)
        df[f"{prefix}_price"] = pd.to_numeric(split_cols[0], errors="coerce")
        df[f"{prefix}_unit"] = split_cols[1]
        df[f"{prefix}_ccy"] = "KES"
        return df

    # Apply transformations
    df = split_price_column(df, "Wholesale", "wholesale")
    df = split_price_column(df, "Retail", "retail")

    # Drop the original columns
    df.drop(columns=["Wholesale", "Retail", "source_date"], inplace=True)

    await batch_load_market_prices(
        df.drop_duplicates(subset=["Market", "Commodity", "Classification", "Grade", "Sex", "Date"], keep="first")
    )


if __name__ == '__main__':
    asyncio.run(load())
