"""Composite Liveability Index (CLI) for Dublin Small Areas using OpenStreetMap and CSO boundaries.
Author: Aung Kaung Myat (MSc GIS & Remote Sensing, University College Dublin)
Python version of my ArcGIS Pro workflow. All layers must be in ITM (EPSG:2157). Inputs: see DATA.md."""
import geopandas as gpd
import mapclassify as mc
import pandas as pd

# 1. Load data and check the projection
sa = gpd.read_file("Dublin_Small_Areas.shp")
pois = gpd.read_file("gis_osm_pois_free_1.shp")
transport = gpd.read_file("gis_osm_transport_free_1.shp")
landuse = gpd.read_file("gis_osm_landuse_a_free_1.shp")
roads = gpd.read_file("gis_osm_roads_free_1.shp")
buildings = gpd.read_file("gis_osm_buildings_a_free_1.shp")
for layer in (sa, pois, transport, landuse, roads, buildings):
    assert layer.crs.to_epsg() == 2157, "Project all layers to ITM (EPSG:2157) first"


def has_access(points, classes, distance_m):
    """1 if a Small Area touches the buffer around the selected points, otherwise 0."""
    selected = points[points["fclass"].isin(classes)]
    catchment = selected.buffer(distance_m).unary_union  # merged buffers (Dissolve ALL)
    return sa.intersects(catchment).astype(int)


def area_ratio(polys, classes=None):
    """Share of each Small Area covered by the polygons (overlaps merged first)."""
    polys = polys[polys["fclass"].isin(classes)].copy() if classes else polys.copy()
    polys["geometry"] = polys.make_valid()
    inside = gpd.overlay(sa[["SA_GUID_2022", "geometry"]], polys.dissolve()[["geometry"]], how="intersection")
    area = inside.area.groupby(inside["SA_GUID_2022"]).sum()
    return (sa["SA_GUID_2022"].map(area).fillna(0) / sa.area).clip(upper=1)


# 2. Indicators
sa["has_health_500m"] = has_access(pois, ["hospital", "doctors", "pharmacy"], 500)
sa["has_transit_400m"] = has_access(transport, ["bus_stop", "tram_stop", "railway_station", "railway_halt"], 400)
sa["green_space_ratio"] = area_ratio(landuse, ["park", "forest", "recreation_ground", "nature_reserve",
                                               "meadow", "grass", "allotments"])
sa["bldg_cov_ratio"] = area_ratio(buildings)

paths = roads[roads["fclass"].isin(["cycleway", "footway", "pedestrian", "path"])]
paths_in_sa = gpd.overlay(paths[["geometry"]], sa[["SA_GUID_2022", "geometry"]], how="intersection")
length_km = (paths_in_sa.length / 1000).groupby(paths_in_sa["SA_GUID_2022"]).sum()
sa["active_travel_density"] = sa["SA_GUID_2022"].map(length_km).fillna(0) / (sa.area / 1_000_000)

# 3. Composite Liveability Index: normalise to 0-1, then take the mean of the four scores
sa["CLI"] = pd.concat([
    sa["green_space_ratio"] / sa["green_space_ratio"].max(),
    sa["active_travel_density"] / sa["active_travel_density"].max(),
    sa["has_transit_400m"],
    sa["has_health_500m"],
], axis=1).mean(axis=1)

# 4. Five classes using Natural Breaks (Jenks)
labels = ["Very Low", "Low", "Medium", "High", "Very High"]
jenks = mc.FisherJenks(sa["CLI"].values, k=5)
sa["CLI_class"] = pd.Categorical.from_codes(jenks.yb, labels, ordered=True)

# 5. Planning queries (optional)
no_health_no_transit = sa[(sa["has_health_500m"] == 0) & (sa["has_transit_400m"] == 0)]
low_green_built_up = sa[(sa["green_space_ratio"] < 0.05) & (sa["bldg_cov_ratio"] > 0.40)]

# 6. Summary and export
print(f"Small Areas: {len(sa)}")
print("Class breaks:", [round(float(b), 3) for b in jenks.bins])
print(sa["CLI_class"].value_counts().sort_index())
print(f"No healthcare and no transport access: {len(no_health_no_transit)} Small Areas")
print(f"Green space below 5% and building coverage above 40%: {len(low_green_built_up)} Small Areas, "
      f"{low_green_built_up.area.sum() / 10_000:.1f} ha")
sa.to_file("dublin_liveability.gpkg", layer="small_areas", driver="GPKG")
