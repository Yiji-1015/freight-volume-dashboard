"""Build a portfolio demo map from synthetic freight volume data."""

from __future__ import annotations

import json
from pathlib import Path

import folium
import pandas as pd
from folium.plugins import MarkerCluster


ROOT = Path(__file__).resolve().parents[1]
GEOJSON_PATH = ROOT / "state_geo.geojson"
SAMPLE_PATH = ROOT / "data" / "processed" / "geo_box_sample.csv"
OUTPUT_DIR = ROOT / "outputs"
OUTPUT_PATH = OUTPUT_DIR / "freight_volume_demo_map.html"
WAREHOUSE = (37.0871367274512, 127.0979525129808)


def short_region_name(value: str) -> str:
    parts = str(value).split()
    return parts[-1] if parts else str(value)


def main() -> None:
    if not SAMPLE_PATH.exists():
        raise FileNotFoundError(
            f"{SAMPLE_PATH} does not exist. Run scripts/generate_sample_data.py first."
        )

    df = pd.read_csv(SAMPLE_PATH)
    df["MAP_SIG_KOR_NM"] = df["STO"].map(short_region_name)

    heat = (
        df.groupby("MAP_SIG_KOR_NM", as_index=False)["BOX_TOT"]
        .sum()
        .sort_values("BOX_TOT", ascending=False)
    )

    with GEOJSON_PATH.open(encoding="utf-8") as f:
        geo = json.load(f)

    volume_by_region = dict(zip(heat["MAP_SIG_KOR_NM"], heat["BOX_TOT"]))
    for feature in geo["features"]:
        sig_nm = feature["properties"].get("SIG_KOR_NM", "")
        box_total = volume_by_region.get(sig_nm, 0)
        feature["properties"]["tooltip"] = (
            f"<b>{sig_nm}</b><br>Sample freight volume: {box_total:,.0f} boxes"
        )

    m = folium.Map(location=WAREHOUSE, zoom_start=7, tiles="cartodbpositron")

    warehouse_cluster = MarkerCluster(name="Distribution Center")
    warehouse_cluster.add_child(
        folium.Marker(
            location=WAREHOUSE,
            popup="Demo Distribution Center",
            icon=folium.Icon(color="red", icon="star"),
        )
    )
    warehouse_cluster.add_to(m)

    customer_cluster = MarkerCluster(name="Sample Customers")
    for row in df.itertuples(index=False):
        customer_cluster.add_child(
            folium.CircleMarker(
                location=[row.LAT_NO, row.LON_NO],
                radius=4,
                color="#2563eb",
                fill=True,
                fill_opacity=0.72,
                popup=f"{row.CU_NM}<br>{row.STO}<br>{row.BOX_TOT:,.0f} boxes",
            )
        )
    customer_cluster.add_to(m)

    bins = heat["BOX_TOT"].quantile([0, 0.45, 0.75, 0.9, 1.0]).round(0).tolist()
    bins = sorted(set(max(0, int(v)) for v in bins))
    if len(bins) < 4:
        bins = 4
    else:
        bins[0] = max(0, bins[0] - 1)
        bins[-1] = bins[-1] + 1

    choropleth = folium.Choropleth(
        geo_data=geo,
        data=heat,
        columns=["MAP_SIG_KOR_NM", "BOX_TOT"],
        key_on="feature.properties.SIG_KOR_NM",
        fill_color="YlOrRd",
        fill_opacity=0.68,
        line_opacity=0.35,
        nan_fill_color="#d1d5db",
        nan_fill_opacity=0.35,
        bins=bins,
        legend_name="Synthetic Freight Volume (boxes)",
        name="Freight Volume Heatmap",
    )
    choropleth.add_to(m)
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(["tooltip"], labels=False)
    )

    folium.LayerControl(collapsed=False).add_to(m)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    m.save(OUTPUT_PATH)
    print(f"Saved {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
