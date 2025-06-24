from enum import Enum


class GetSoilDataIsdasoilV2SoilpropertyGetPropertyType0(str, Enum):
    ALUMINIUM_EXTRACTABLE = "aluminium_extractable"
    BEDROCK_DEPTH = "bedrock_depth"
    BULK_DENSITY = "bulk_density"
    CALCIUM_EXTRACTABLE = "calcium_extractable"
    CARBON_ORGANIC = "carbon_organic"
    CARBON_TOTAL = "carbon_total"
    CATION_EXCHANGE_CAPACITY = "cation_exchange_capacity"
    CLAY_CONTENT = "clay_content"
    CROP_COVER_2015 = "crop_cover_2015"
    CROP_COVER_2016 = "crop_cover_2016"
    CROP_COVER_2017 = "crop_cover_2017"
    CROP_COVER_2018 = "crop_cover_2018"
    CROP_COVER_2019 = "crop_cover_2019"
    FCC = "fcc"
    IRON_EXTRACTABLE = "iron_extractable"
    LAND_COVER_2015 = "land_cover_2015"
    LAND_COVER_2016 = "land_cover_2016"
    LAND_COVER_2017 = "land_cover_2017"
    LAND_COVER_2018 = "land_cover_2018"
    LAND_COVER_2019 = "land_cover_2019"
    MAGNESIUM_EXTRACTABLE = "magnesium_extractable"
    NITROGEN_TOTAL = "nitrogen_total"
    PH = "ph"
    PHOSPHOROUS_EXTRACTABLE = "phosphorous_extractable"
    POTASSIUM_EXTRACTABLE = "potassium_extractable"
    SAND_CONTENT = "sand_content"
    SILT_CONTENT = "silt_content"
    SLOPE_ANGLE = "slope_angle"
    STONE_CONTENT = "stone_content"
    SULPHUR_EXTRACTABLE = "sulphur_extractable"
    TEXTURE_CLASS = "texture_class"
    ZINC_EXTRACTABLE = "zinc_extractable"

    def __str__(self) -> str:
        return str(self.value)
