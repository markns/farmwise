from functools import lru_cache
from typing import Any

import pandas as pd
from fastapi import APIRouter
from loguru import logger

from farmbase.data.crops.models import CropVarietiesResponse, CropVarietyResponse

router = APIRouter()


# Load the region lookup GeoDataFrame
# region_gdf = pd.read_pickle("farmbase/data/kalro/regions.pkl")

# Load the crop variety suitability data
# crops_df = pd.read_csv("farmbase/data/kalro/crops.csv")
# suitability_df = pd.read_pickle("farmbase/data/kalro/suitability.pkl")


@lru_cache(maxsize=None)
def get_maize_data():
    """
    Loads the growing period raster from GCS.
    This function is cached, so it only runs once.
    """
    logger.info("Loading and caching maize variety data")
    maize_df = pd.read_csv("gs://farmbase_data/maize/maize_varieties.csv")
    return maize_df


@router.get("/maize", response_model=CropVarietiesResponse)
def get_maize_varieties(altitude: float = None, growing_period: int = None) -> Any:
    """
    Filters and returns maize varieties based on optional altitude and growing period criteria.
    """
    maize_df = get_maize_data()

    # Start with the full dataframe, which will be progressively filtered.
    suitable_df = maize_df.copy()

    # 1. Conditionally filter by altitude if a value is provided.
    if altitude is not None:
        suitable_df = suitable_df[
            (suitable_df["min_altitude_masl"] <= altitude) & (suitable_df["max_altitude_masl"] >= altitude)
        ]

    # 2. Conditionally filter by growing period if a value is provided.
    if growing_period is not None:
        maturity_category = maize_maturity_category(growing_period)

        if maturity_category is not None:
            # To correctly filter for varieties with a "greater or equal" maturity period,
            # we define an explicit order for the categories.
            category_order = ["Extremely early", "Early", "Intermediate", "Late", "Very late"]

            try:
                # Find the position of the requested maturity category in the ordered list.
                user_category_index = category_order.index(maturity_category)

                # Identify all categories that are suitable (the requested one and all that take longer).
                suitable_categories = category_order[user_category_index:]

                # Filter the dataframe to include only varieties in the suitable categories.
                suitable_df = suitable_df[suitable_df["maturity_category"].isin(suitable_categories)]
            except ValueError:
                # This handles cases where the calculated maturity_category is not in our defined order.
                # In this scenario, we do not apply a maturity filter.
                pass

    varieties = [CropVarietyResponse(**row) for _, row in suitable_df.iterrows()]

    return CropVarietiesResponse(crop="maize", varieties=varieties)


def maize_maturity_category(growing_season_days: float | int | None) -> str | None:
    """
    Return the maturity category for a maize variety, given its growing-season
    length in days.

    Categories & thresholds (inclusive):
        •  76–85  → “Extremely early”
        •  86–112 → “Early”
        • 113–129 → “Intermediate”
        • 130–145 → “Late”
        • ≥150    → “Very late”

    Parameters
    ----------
    growing_season_days : float | int | None
        Mean number of days from planting to physiological maturity.

    Returns
    -------
    str | None
        The matching category, or `None` if the input is missing or out of range.
    """
    if growing_season_days is None:
        return None

    d = float(growing_season_days)

    if 76 <= d <= 85:
        return "Extremely early"
    elif 86 <= d <= 112:
        return "Early"
    elif 113 <= d <= 129:
        return "Intermediate"
    elif 130 <= d <= 145:
        return "Late"
    elif d >= 150:
        return "Very late"
    else:
        # catches values < 76 or any negative / nonsensical input
        return None


#
# @router.get("/suitability", response_model=CropVarietiesResponse)
# def get_suitable_crop_varieties(session: SessionDep, crop_type: str, latitude: float, longitude: float) -> Any:
#     """
#     Get suitable crop varieties for a given location and crop type.
#     """
#     print("-----")
#     # Create a point from the input coordinates
#     point = gpd.points_from_xy([longitude], [latitude])[0]
#
#     # Find the region that contains the point
#     region = region_gdf[region_gdf.geometry.contains(point)]
#
#     if region.empty:
#         raise HTTPException(status_code=404, detail="No region found for the given coordinates")
#
#     region_code = region.iloc[0]["dhis2_id"]
#
#     matching_crops = crops_df[crops_df["crop"].str.lower() == crop_type.lower()]
#     print(matching_crops)
#     if matching_crops.empty:
#         # Suggest close matches for the provided crop_type
#         crop_list = crops_df["crop"].dropna().unique().tolist()
#         suggestions = difflib.get_close_matches(crop_type, crop_list, n=5, cutoff=0.6)
#         if len(suggestions) == 1:
#             detail = f"No crops found matching '{crop_type}'. Did you mean: {suggestions[0]}?"
#         elif suggestions:
#             suggestion_text = ", ".join(suggestions)
#             detail = f"No crops found matching '{crop_type}'. Did you mean one of these: {suggestion_text}?"
#         else:
#             detail = f"No crops found matching '{crop_type}'."
#         raise HTTPException(status_code=404, detail=detail)
#
#     # Filter for the given crop type and region (case-insensitive crop match)
#     suitable_varieties = suitability_df[
#         (suitability_df["crop"].isin(matching_crops["crop"].tolist()))
#         & (suitability_df["dhis2_id"] == region_code)
#         & (suitability_df["suitability"])
#     ]
#     print(suitable_varieties)
#     if suitable_varieties.empty:
#         raise HTTPException(
#             status_code=404, detail=f"No suitable varieties found for crop type {crop_type} in region {region_code}"
#         )
#
#     # Convert to response format
#     varieties = [CropVarietyResponse(variety=row["variety"]) for _, row in suitable_varieties.iterrows()]
#
#     return CropVarietiesResponse(crop=crop_type, varieties=varieties)
