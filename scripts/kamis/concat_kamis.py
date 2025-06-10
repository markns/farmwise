import glob
import os

import pandas as pd


def load_all_excels_to_dataframe(folder="."):
    """Load and concatenate all kamis_*.xlsx files into a single DataFrame."""
    all_files = sorted(glob.glob(os.path.join(folder, "kamis_*.xlsx")))
    df_list = []

    for file in all_files:
        try:
            df = pd.read_excel(file)
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


if __name__ == "__main__":
    # Example usage:
    df = load_all_excels_to_dataframe(folder="data/kamis/market_prices")
    # Save to CSV (optional)
    df.to_csv("kamis_market_prices.csv", index=False)
