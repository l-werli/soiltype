import geopandas as gpd


def check_soil_suitability(geojson_path, soil_shapefile):

    field = gpd.read_file(geojson_path)

    soil_columns = ["legenda", "legenda_ap", "classe_apt", "geometry"]
    soils = gpd.read_file(soil_shapefile, columns=soil_columns)

    soils = soils.to_crs(field.crs)

    intersection = gpd.overlay(field, soils, how="intersection")

    if intersection.empty:
        return {
            "suitable": False,
            "message": "No soil data found"
        }
    # make sure that the crs is projected and not geographic
    intersection = intersection.to_crs(5880)
    intersection["area"] = intersection.geometry.area

    area_by_class = (
        intersection
        .groupby("classe_apt")["area"]
        .sum()
        .sort_values(ascending=False)
    )
    # define for integer to prevent false detection of another class if the value is float
    dominant_class = int(area_by_class.index[0])

    suitable = dominant_class in {1, 2, 3}

    dominant_soil = intersection.loc[
        intersection["classe_apt"] == dominant_class,
        "legenda"
    ].iloc[0]

    if suitable:
        print(f"The {dominant_soil} is not suitable to have crops")
    else: print(f"The {dominant_soil} is not prepaired to have a crop")
    
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
