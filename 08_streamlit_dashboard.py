import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from folium.plugins import FastMarkerCluster

st.set_page_config(page_title="Accra Solar Dashboard", layout="wide")

st.title("🌞 Accra Solar Rooftop Suitability & Investment Dashboard")
st.markdown("**Case Study: Central Accra** | Geospatial AI & Economic Modeling")

# Load light data
@st.cache_data(show_spinner=True)
def load_data():
    gdf = gpd.read_file("accra_buildings_solar_roi_final.gpkg")
    if gdf.crs is None or gdf.crs.to_string() != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")
    return gdf

buildings = load_data()

# Filtering
@st.cache_data
def filter_data(_buildings, min_suitability, max_payback, min_npv):
    return _buildings[
        (_buildings['suitability_score'] >= min_suitability) &
        (_buildings['payback_years'] <= max_payback) &
        (_buildings['npv_ghs'] >= min_npv)
    ].copy()

st.sidebar.header("🔍 Filters")
min_suitability = st.sidebar.slider("Minimum Suitability Score", 0, 100, 40)
max_payback = st.sidebar.slider("Maximum Payback Period (years)", 0, 25, 12)
min_npv = st.sidebar.slider("Minimum NPV (GHS)", -50000, 400000, 0)

filtered = filter_data(buildings, min_suitability, max_payback, min_npv)

st.header(f"Filtered Results: **{len(filtered):,} buildings** (out of {len(buildings):,} total)")

# Key Metrics - Overall vs Filtered
col1, col2 = st.columns(2)
with col1:
    st.subheader("Overall (All Buildings)")
    st.metric("Total Buildings", f"{len(buildings):,}")
    st.metric("Avg Payback", f"{buildings['payback_years'].mean():.1f} years")
    st.metric("Avg NPV", f"{buildings['npv_ghs'].mean():,.0f} GHS")

with col2:
    st.subheader("Filtered Results")
    st.metric("Filtered Buildings", f"{len(filtered):,}")
    st.metric("Avg Payback", f"{filtered['payback_years'].mean():.1f} years")
    st.metric("Avg NPV", f"{filtered['npv_ghs'].mean():,.0f} GHS")

# Download Button
summary_cols = ['building_id', 'suitability_score', 'system_kw', 'payback_years',
                'npv_ghs', 'annual_kwh_year1', 'usable_area_m2']
csv = filtered[summary_cols].to_csv(index=False)
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv,
    file_name="accra_solar_filtered_buildings.csv",
    mime="text/csv"
)

# Tabs
tab1, tab2, tab3 = st.tabs(["📍 Interactive Map", "📊 Distributions", "💰 Economic Insights"])

with tab1:
    st.subheader("Solar Suitability Map")
    sample_size = min(2000, len(filtered))
    sample = filtered.sample(sample_size, random_state=42).copy()

    sample_utm = sample.to_crs("EPSG:32630")
    centroids = sample_utm.geometry.centroid.to_crs("EPSG:4326")
    sample["lat"] = centroids.y
    sample["lon"] = centroids.x

    m = folium.Map(location=[5.58, -0.125], zoom_start=13, tiles="CartoDB positron")

    points = list(zip(sample["lat"], sample["lon"]))
    FastMarkerCluster(points).add_to(m)

    top_sample = sample.nlargest(100, 'npv_ghs')
    for _, row in top_sample.iterrows():
        color = "green" if row['suitability_score'] > 70 else \
                "orange" if row['suitability_score'] > 50 else "red"

        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=5,
            color=color,
            fill=True,
            fill_opacity=0.85,
            popup=f"ID: {row.get('building_id', 'N/A')}<br>"
                  f"Suitability: {row['suitability_score']:.1f}<br>"
                  f"Payback: {row['payback_years']:.1f} yrs<br>"
                  f"NPV: {row['npv_ghs']:,.0f} GHS"
        ).add_to(m)

    # LEGEND
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; width: auto; min-width: 210px; height: auto;
        background-color: white; border:2px solid grey; z-index:9999; font-size:13px;
        padding: 12px; color: black; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); border-radius: 5px;">
        <b style="display: block; margin-bottom: 10px; font-size: 14px; border-bottom: 1px solid #ccc; padding-bottom: 5px; color: black;">Suitability Legend</b>
        <table style="border-spacing: 0 5px; border-collapse: separate;">
            <tr>
                <td style="vertical-align: middle;"><div style="background:green; width:18px; height:18px; border:1px solid black; border-radius: 50%;"></div></td>
                <td style="vertical-align: middle; padding-left: 10px; white-space: nowrap; font-weight: 500; color: black;">High Suitability (>70)</td>
            </tr>
            <tr>
                <td style="vertical-align: middle;"><div style="background:orange; width:18px; height:18px; border:1px solid black; border-radius: 50%;"></div></td>
                <td style="vertical-align: middle; padding-left: 10px; white-space: nowrap; font-weight: 500; color: black;">Medium Suitability (51-70)</td>
            </tr>
            <tr>
                <td style="vertical-align: middle;"><div style="background:red; width:18px; height:18px; border:1px solid black; border-radius: 50%;"></div></td>
                <td style="vertical-align: middle; padding-left: 10px; white-space: nowrap; font-weight: 500; color: black;">Low Suitability (≤50)</td>
            </tr>
            <tr>
                <td style="vertical-align: middle;"><div style="background:#3388ff; width:18px; height:18px; border:1px solid #1a5fb4; border-radius: 50%; opacity: 0.7;"></div></td>
                <td style="vertical-align: middle; padding-left: 10px; white-space: nowrap; font-weight: 500; color: black;">Clustered Areas (Zoom In)</td>
            </tr>
        </table>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    st_folium(m, width="100%", height=680, key="accra_solar_map_final")

with tab2:
    st.subheader("Suitability Score Distribution")
    fig = px.histogram(filtered, x="suitability_score", nbins=30)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Economic Insights")
    colA, colB = st.columns(2)
    with colA:
        fig1 = px.scatter(filtered, x="suitability_score", y="payback_years",
                         color="npv_ghs", title="Suitability vs Payback")
        st.plotly_chart(fig1, use_container_width=True)
    with colB:
        fig2 = px.box(filtered, y="payback_years", title="Payback Period Distribution")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("🔝 Top 20 Highest NPV Buildings")
    top20 = filtered.nlargest(20, "npv_ghs")
    st.dataframe(top20[['building_id', 'suitability_score', 'system_kw', 'payback_years', 'npv_ghs']].round(1))

st.caption("Accra Solar Suitability Project | Built with Streamlit & GeoPandas")
