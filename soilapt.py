import geopandas as gpd


def check_soil_suitability(geojson_path, soil_shapefile):

    field = gpd.read_file(geojson_path)

    soil_columns = ["legenda", "legenda_ap", "classe", "geometry"]
    soils = gpd.read_file(soil_shapefile, columns=soil_columns)

    soils = soils.to_crs("5880")

    intersection = gpd.overlay(field, soils, how="intersection")

    if intersection.empty:
        return {
            "suitable": False,
            "message": "No soil data found"
        }

    intersection["area"] = intersection.geometry.area

    area_by_class = (
        intersection
        .groupby("classe")["area"]
        .sum()
        .sort_values(ascending=False)
    )

    dominant_class = int(area_by_class.index[0])

    suitable = dominant_class in {1, 2, 3}

    return {
        "dominant_class": int(dominant_class),
        "suitable_for_agriculture": suitable
    }


if __name__ == "__main__":
  
    geojson = "data/farm_area.geojson"
    soil_shp = "data/aptagr_bra.shp"

    result = check_soil_suitability(geojson, soil_shp)

    print(result)
