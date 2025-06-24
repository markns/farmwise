import os
from functools import lru_cache
from typing import Annotated

import gcsfs
from fastapi import APIRouter, Query
from loguru import logger

from farmbase.data.gaez.models import SuitabilityIndexResponse

router = APIRouter()

# --- GCS and Path Constants ---
# The GCS filesystem object is lightweight and can be initialized globally.
fs = gcsfs.GCSFileSystem()

# Define paths as constants for clarity
CLASS_MAP_PATH = "gs://farmbase_data/gaez/GAEZ4_symbology_files/clr_files/AEZ_33classes.clr"
AEZ_RASTER_PATH = "gs://farmbase_data/gaez/LR/aez/aez_v9v2red_ENSEMBLE_rcp4p5_2020s.tif"
GROWING_PERIOD_RASTER_PATH = "gs://farmbase_data/gaez/res01/ENSEMBLE/rcp4p5/ld1_ENSEMBLE_rcp4p5_2020s.tif"
SUITABILITY_RASTER_DIR = "gs://farmbase_data/gaez/res05/HadGEM2-ES/rcp4p5/2020sH"


# --- Helper and Caching Functions ---

def _read_clr(gcs_path):
    """Helper function to read a GAEZ .clr file."""
    colormap = {}
    with fs.open(gcs_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                parts = line.split(maxsplit=5)
                if len(parts) >= 5:  # Ensure we have enough parts for label
                    value = int(parts[0])
                    # The label is the 6th part (index 5)
                    label = parts[5].strip() if len(parts) > 5 else "Unknown"
                    colormap[value] = label
    return colormap


@lru_cache(maxsize=None)
def get_class_map():
    """
    Loads the AEZ class map from GCS.
    This function is cached, so it only runs once.
    """
    logger.info(f"Loading and caching class map from: {CLASS_MAP_PATH}")
    return _read_clr(CLASS_MAP_PATH)


def open_raster_from_gcs(path):
    # Although rioxarray can read gs:// paths, it doesn't seem to handle the ambient credentials
    # when running in Google Cloud Run. Therefore, use GCSFileSystem to memory
    import rioxarray
    from rasterio import MemoryFile

    with fs.open(path, 'rb') as f:
        logger.debug(f"opened file {f}")
        with MemoryFile(f.read()) as memfile:
            logger.debug(f"read file {f} into {memfile}")
            with memfile.open() as dataset:
                logger.debug(f"opened memfile {memfile}")
                return rioxarray.open_rasterio(dataset)


@lru_cache(maxsize=None)
def get_aez_raster():
    """
    Loads the AEZ raster from GCS.
    This function is cached, so it only runs once.
    """
    logger.info(f"Loading and caching AEZ raster from: {AEZ_RASTER_PATH}")
    return open_raster_from_gcs(AEZ_RASTER_PATH)


@lru_cache(maxsize=None)
def get_growing_period_raster():
    """
    Loads the growing period raster from GCS.
    This function is cached, so it only runs once.
    """
    logger.info(f"Loading and caching growing period raster from: {GROWING_PERIOD_RASTER_PATH}")
    return open_raster_from_gcs(GROWING_PERIOD_RASTER_PATH)


@lru_cache(maxsize=None)
def get_suitability_raster():
    """
    Loads, aligns, and stacks all crop suitability rasters.
    This is a heavy operation and is cached to run only once.
    """
    import xarray as xr

    logger.info(f"Loading and caching all suitability rasters from: {SUITABILITY_RASTER_DIR}")
    # Note: Using fs.glob() to find files is more robust
    raster_paths = fs.glob(os.path.join(SUITABILITY_RASTER_DIR, "suHr0_*.tif"))

    # Prepend 'gs://' to make them valid URLs for rioxarray
    full_raster_paths = [f"gs://{path}" for path in raster_paths]
    rasters = [open_raster_from_gcs(path) for path in full_raster_paths]

    # Align rasters to ensure they have the same spatial resolution and extents
    aligned_rasters = xr.align(*rasters, join="exact")

    # Extract crop codes from filenames for coordinates
    raster_crop_codes = [os.path.basename(p).split('.')[0].split('_')[1] for p in full_raster_paths]

    # Stack rasters along a new 'crop' dimension
    stacked_raster = xr.concat(aligned_rasters, dim="crop")

    # Assign meaningful labels to the new dimension
    stacked_raster = stacked_raster.assign_coords(crop=raster_crop_codes)
    return stacked_raster


# --- API Endpoints ---

@router.get("/aez_classification", response_model=str)
def aez_classification(
        latitude: Annotated[float, Query(description="The latitude coordinate")],
        longitude: Annotated[float, Query(description="The longitude coordinate")],
):
    """Get the AEZ (Agro-Ecological Zone) classification for a given geographical coordinate."""
    # Call the cached getter functions
    raster = get_aez_raster()
    class_map = get_class_map()

    value = raster.sel(x=longitude, y=latitude, method="nearest").item()
    logger.debug(f"aez classification for lon:{longitude} lat:{latitude} is {value}")
    return class_map.get(value, "Unknown Classification")


@router.get("/growing_period", response_model=int)
def growing_period(
        latitude: Annotated[float, Query(description="The latitude coordinate")],
        longitude: Annotated[float, Query(description="The longitude coordinate")],
):
    """Get the growing period length in days for a given geographical coordinate."""
    # Call the cached getter function
    raster = get_growing_period_raster()
    logger.debug(f"loaded growing period raster shape {raster.shape}")
    days =  raster.sel(x=longitude, y=latitude, method="nearest").item()
    logger.debug(f"growing period for lon:{longitude} lat:{latitude} is {days} days")
    return days


# This can remain global as it's just a static dictionary
crop_codes = {
    "alf": "Alfalfa", "ban": "Banana", "brl": "Barley", "cit": "Citrus", "coc": "Cocoa",
    "cof": "Coffee", "con": "Coconut", "cot": "Cotton", "csv": "Cassava", "flx": "Flax",
    "grd": "Groundnut", "jtr": "Jatropha", "mze": "Maize", "mis": "Miscanthus",
    "nap": "Napier grass", "olp": "Oil palm", "olv": "Olive", "rcg": "Reed canary grass",
    "rsd": "Rapeseed", "rub": "Rubber", "sfl": "Sunflower", "soy": "Soybean",
    "spo": "Sweet potato", "sub": "Sugarbeet", "suc": "Sugarcane", "swg": "Switchgrass",
    "tea": "Tea", "tob": "Tobacco", "whe": "Wheat", "wpo": "White potato", "yam": "Yam",
}


@router.get("/suitability_index", response_model=SuitabilityIndexResponse)
def suitability_index(
        latitude: Annotated[float, Query(description="The latitude coordinate")],
        longitude: Annotated[float, Query(description="The longitude coordinate")],
):
    """Get the crop suitability index values for a given geographical coordinate."""
    # Call the cached getter function for the combined suitability raster
    stacked_raster = get_suitability_raster()

    # Select the data for the given point
    suitability_point = stacked_raster.sel(x=longitude, y=latitude, method="nearest")

    # Create the response dictionary
    response_data = {
        crop_codes.get(crop_code.item(), "Unknown Crop"): value.item()
        for crop_code, value in zip(suitability_point.crop, suitability_point.values)
    }

    return SuitabilityIndexResponse(suitability_index=response_data)
