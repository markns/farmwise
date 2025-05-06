from typing import Any

import pandas as pd
from fastapi import APIRouter

from farmbase.data.crops.models import CropVarietiesResponse, CropVarietyResponse

router = APIRouter()

# Load the region lookup GeoDataFrame
# region_gdf = pd.read_pickle("farmbase/data/kalro/regions.pkl")

# Load the crop variety suitability data
# crops_df = pd.read_csv("farmbase/data/kalro/crops.csv")
# suitability_df = pd.read_pickle("farmbase/data/kalro/suitability.pkl")

maize_df = pd.read_csv("apps/farmbase/data/maize/maize_varieties.csv")


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


@router.get("/maize", response_model=CropVarietiesResponse)
def get_maize_varieties(altitude: float, growing_period: int) -> Any:
    maturity_category = maize_maturity_category(growing_period)

    suitable = maize_df[
        (maize_df["min_altitude_masl"] <= altitude)
        & (maize_df["max_altitude_masl"] >= altitude)
        & (maize_df["maturity_category"] >= maturity_category)
    ]
    varieties = [
        CropVarietyResponse(variety=row["variety"], description=row["description"], max_yield=row["yield_tons_ha"])
        for _, row in suitable.iterrows()
    ]
    return CropVarietiesResponse(crop="maize", varieties=varieties)


#
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
