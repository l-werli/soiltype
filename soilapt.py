import geopandas as gpd


def check_soil_suitability(geojson_path, soil_shapefile):

    field = gpd.read_file(geojson_path)

    soil_columns = ["legenda", "legenda_ap", "classe_apt", "geometry"]
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
        .groupby("classe_apt")["area"]
        .sum()
        .sort_values(ascending=False)
    )

    dominant_class = int(area_by_class.index[0])

    suitable = dominant_class in {1, 2, 3}
    if suitable == true
        print(" O [Dominant_soil] é adequado para plantio")
    else: print(Este solo não é adequado para plantio)

    dominant_soil = intersection.loc[
        intersection["classe"] == dominant_class,
        "legenda"
    ].iloc[0]

    return {
        "dominant_class": int(dominant_class),
        "dominant_soil": dominant_soil,
        "suitable_for_agriculture": suitable
    }


if __name__ == "__main__":
  
    geojson = "data/area.geojson"
    soil_shp = "data/aptagr_bra.shp"

    result = check_soil_suitability(geojson, soil_shp)

    print(result)
