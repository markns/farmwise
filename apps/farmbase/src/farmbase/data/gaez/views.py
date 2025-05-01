import os

import xarray as xr
from fastapi import APIRouter
from rioxarray import rioxarray

router = APIRouter()


def _read_clr(filepath):
    colormap = {}
    with open(filepath, "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                parts = line.split(maxsplit=5)
                if len(parts) >= 4:
                    value = int(parts[0])
                    label = parts[5].strip()
                    colormap[value] = label
    return colormap


clr_path = "apps/farmbase/data/gaez/GAEZ4_symbology_files/clr_files/AEZ_33classes.clr"
class_map = _read_clr(clr_path)

aez_raster = rioxarray.open_rasterio("apps/farmbase/data/gaez/LR/aez/aez_v9v2red_ENSEMBLE_rcp4p5_2020s.tif")
growing_period_raster = rioxarray.open_rasterio(
    "apps/farmbase/data/gaez/res01/ENSEMBLE/rcp4p5/ld1_ENSEMBLE_rcp4p5_2020s.tif"
)


@router.get("/aez_classification", response_model=str)
def aez_classification(latitude: float, longitude: float):
    # Ensure coordinates are named correctly and use the nearest match
    value = aez_raster.sel(x=longitude, y=latitude, method="nearest").item()
    return class_map[value]


@router.get("/growing_period", response_model=int)
def growing_period(latitude: float, longitude: float):
    # Ensure coordinates are named correctly and use the nearest match
    return growing_period_raster.sel(x=longitude, y=latitude, method="nearest").item()


crop_codes = {
    "alf": "Alfalfa",
    "ban": "Banana",
    "brl": "Barley",
    "cit": "Citrus",
    "coc": "Cocoa",
    "cof": "Coffee",
    "con": "Coconut",
    "cot": "Cotton",
    "csv": "Cassava",
    "flx": "Flax",
    "grd": "Groundnut",
    "jtr": "Jatropha",
    "mze": "Maize",
    "mis": "Miscanthus",
    "nap": "Napier grass",
    "olp": "Oil palm",
    "olv": "Olive",
    "rcg": "Reed canary grass",
    "rsd": "Rapeseed",
    "rub": "Rubber",
    "sfl": "Sunflower",
    "soy": "Soybean",
    "spo": "Sweet potato",
    "sub": "Sugarbeet",
    "suc": "Sugarcane",
    "swg": "Switchgrass",
    "tea": "Tea",
    "tob": "Tobacco",
    "whe": "Wheat",
    "wpo": "White potato",
    "yam": "Yam",
}


@router.get("/suitability_index", response_model=dict[str, int])
def suitability_index(latitude: float, longitude: float):
    file_path = "farmbase/data/gaez/res05/HadGEM2-ES/rcp4p5/2020sH"
    # variables = dict(zip(sdf.name, sdf.crop))
    # # variables
    rasters = [rioxarray.open_rasterio(os.path.join(file_path, f"suHr0_{v}.tif")) for v in crop_codes.keys()]
    # Align rasters to ensure they have the same spatial resolution and extents
    rasters = xr.align(*rasters, join="exact")
    # Stack rasters along the band dimension
    raster = xr.concat(rasters, dim="band")
    # Assign meaningful labels to the band dimension
    raster = raster.assign_coords(band=list(crop_codes.keys()))
    # suitability_index
    suitability_point = raster.sel(x=longitude, y=latitude, method="nearest")

    crops = [crop_codes[c] for c in suitability_point.band.values]
    return dict(zip(crops, suitability_point.values))
