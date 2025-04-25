from fastapi import APIRouter
from rioxarray import rioxarray

router = APIRouter(prefix="/gaez", tags=["gaez"])


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


clr_path = "farmbase/data/gaez/GAEZ4_symbology_files/clr_files/AEZ_33classes.clr"
class_map = _read_clr(clr_path)

aez_raster = rioxarray.open_rasterio("farmbase/data/gaez/LR/aez/aez_v9v2red_ENSEMBLE_rcp4p5_2020s.tif")
growing_period_raster = rioxarray.open_rasterio(
    "farmbase/data/gaez/res01/ENSEMBLE/rcp4p5/ld1_ENSEMBLE_rcp4p5_2020s.tif"
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
