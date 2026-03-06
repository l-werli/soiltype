import geopandas as gpd
import pandas as pd


def fix_text_encoding(value):
    """
    Fix mojibake text like:
    'Cambissolo HÃ¡plico Tb DistrÃ³fico'
    -> 'Cambissolo Háplico Tb Distrófico'
    """
    if pd.isna(value):
        return value
    try:
        return value.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError, AttributeError):
        return value


def split_soil_legend(legend_value):
    """
    Split the code from the soil name
    'CXbd - Cambissolo Háplico Tb Distrófico'

    Returns:
        soil_code, soil_name
    """
    if pd.isna(legend_value):
        return "Unknown", "Unknown"

    legend_value = str(legend_value).strip()

    if " - " in legend_value:
        soil_code, soil_name = legend_value.split(" - ", 1)
        return soil_code.strip(), soil_name.strip()

    return legend_value, legend_value


def check_soil_suitability_fast(geojson_path, soil_shapefile):
    """
    Check if a farmer's field is suitable for agriculture based on
    EMBRAPA soil suitability classes.

    Suitability classes:
        1, 2, 3 -> suitable for agriculture
        4, 5, 6 -> not suitable for agriculture
    """

    field = gpd.read_file(geojson_path)

    if field.empty:
        return {
            "message": "The provided GeoJSON is empty."
        }

    soil_columns = ["legenda", "classe_apt", "geometry"]
    soils = gpd.read_file(soil_shapefile, columns=soil_columns, encoding="latin1")

    if soils.empty:
        return {
            "message": "The EMBRAPA soil shapefile is empty."
        }

    # Fix broken accents after reading
    soils["legenda"] = soils["legenda"].apply(fix_text_encoding)
    soils["legenda_ap"] = soils["legenda_ap"].apply(fix_text_encoding)

    soils = soils.to_crs(field.crs)

    minx, miny, maxx, maxy = field.total_bounds
    candidate_idx = list(soils.sindex.intersection((minx, miny, maxx, maxy)))
    candidate_soils = soils.iloc[candidate_idx].copy()

    if candidate_soils.empty:
        return {
            "message": "Nenhum dado de solo encontrado para esta área."
        }

    clipped = gpd.clip(candidate_soils, field)

    if clipped.empty:
        return {
            "message": "Nenhum dado de solo encontrado para esta área."
        }

    clipped = clipped.to_crs(5880)
    clipped["area"] = clipped.geometry.area

    total_area = clipped["area"].sum()

    if total_area == 0:
        return {
            "message": "A área resultante do talhão é zero após o recorte."
        }

    clipped["classe_apt_num"] = pd.to_numeric(
        clipped["classe_apt"],
        errors="coerce"
    )

    unclassified_area = clipped.loc[
        clipped["classe_apt_num"].isna(),
        "area"
    ].sum()

    classified_area = total_area - unclassified_area

    classified_area_percentage = (classified_area / total_area) * 100
    unclassified_area_percentage = (unclassified_area / total_area) * 100

    classified = clipped.dropna(subset=["classe_apt_num"]).copy()

    if classified.empty:
        print(
            f"{unclassified_area_percentage:.0f}% of the field is in area without"
            "suitable agricultural classification by EMBRAPA."
        )

        return {
            "message": "It was not found a suitable agricultural class for this field.",
            "classified_area_percentage": round(classified_area_percentage, 2),
            "unclassified_area_percentage": round(unclassified_area_percentage, 2)
        }

    classified["classe_apt_num"] = classified["classe_apt_num"].astype(int)

    area_by_class = (
        classified
        .groupby("classe_apt_num")["area"]
        .sum()
        .sort_values(ascending=False)
    )

    dominant_class = int(area_by_class.index[0])
    dominant_area = area_by_class.iloc[0]
    dominant_percentage = (dominant_area / total_area) * 100

    suitable = dominant_class in {1, 2, 3}

    dominant_rows = classified[classified["classe_apt_num"] == dominant_class].copy()

    if dominant_rows["legenda"].dropna().empty:
        dominant_legend = "Unknown"
    else:
        dominant_legend = dominant_rows["legenda"].dropna().mode().iloc[0]

    soil_code, soil_name = split_soil_legend(dominant_legend)

    # print information about the field
    if suitable:
        print(
            f"{dominant_percentage:.0f}% of the field is class {dominant_class} "
            f"({soil_code} | {soil_name}) and is suitable for agriculture."
        )
    else:
        print(
            f"{dominant_percentage:.0f}% of the field is class {dominant_class} "
            f"({soil_code} | {soil_name}) and is not suitable for agriculture."
        )

    print(
        f"{classified_area_percentage:.0f}% of the area has classification and "
        f"{unclassified_area_percentage:.0f}% hasn't."
    )

    return {
        "dominant_class": dominant_class,
        "soil_code": soil_code,
        "soil_name": soil_name,
        "dominant_percentage": round(dominant_percentage, 2),
        "suitable_for_agriculture": suitable,
        "classified_area_percentage": round(classified_area_percentage, 2),
        "unclassified_area_percentage": round(unclassified_area_percentage, 2)
    }


if __name__ == "__main__":
    geojson = "poligono2084.geojson"
    soil_shp = "aptagr_bra.shp"

    result = check_soil_suitability_fast(geojson, soil_shp)

    print(result)
