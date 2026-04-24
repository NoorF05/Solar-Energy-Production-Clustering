

import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.express as px
from folium.plugins import HeatMap

st.set_page_config(layout="wide")

# ---------------------------
# LOAD DATA
# ---------------------------
@st.cache_data
def load_data():
    area_df = pd.read_csv("final_area_df.csv")
    df2 = pd.read_csv("project_level_data.csv")
    return area_df, df2

area_df, df2 = load_data()

# ---------------------------
# SIDEBAR
# ---------------------------
st.sidebar.title("Filters")

cluster_filter = st.sidebar.multiselect(
    "Select Cluster",
    options=area_df["cluster_name"].unique(),
    default=area_df["cluster_name"].unique()
)

energy_range = st.sidebar.slider(
    "Energy Range (kWh)",
    int(area_df["energy_kwh"].min()),
    int(area_df["energy_kwh"].max()),
    (int(area_df["energy_kwh"].min()), int(area_df["energy_kwh"].max()))
)

# ---------------------------
# APPLY FILTERS
# ---------------------------
filtered_area = area_df[
    (area_df["cluster_name"].isin(cluster_filter)) &
    (area_df["energy_kwh"].between(*energy_range))
]

# ---------------------------
# TITLE
# ---------------------------
st.title("🌞 Solar Energy Production Zone Analyzer")

st.markdown("""

Analyze solar zones, optimize ROI, and identify high-potential regions.
""")

# ---------------------------
# KPI SECTION
# ---------------------------
st.subheader("📊 Key Performance Indicators")

# Row 1 (top 2 metrics)
col1, col2 = st.columns(2)

col1.metric("⚡ Total Energy", f"{filtered_area['energy_kwh'].sum():,.0f}")
col2.metric("🏗️ Total Projects", f"{filtered_area['num_projects'].sum():,.0f}")

# Row 2 (bottom 2 metrics)
col3, col4 = st.columns(2)

col3.metric("📍 ZIP Coverage", filtered_area.shape[0])
col4.metric(
    "🟢 High Zone %",
    f"{(filtered_area['cluster_name']=='High Production Zone').mean()*100:.1f}%"
)

st.divider()
# ---------------------------
# MAP SECTION (FIXED CENTER + HEATMAP)
# ---------------------------
st.subheader("📍 Solar Production Zones Map")

if not filtered_area.empty:
    center_lat = filtered_area["lat"].mean()
    center_lng = filtered_area["lng"].mean()
else:
    center_lat, center_lng = 39.5, -98.35

m = folium.Map(location=[center_lat, center_lng], zoom_start=6)

color_map = {
    "High Production Zone": "green",
    "Medium Production Zone": "blue",
    "Low Production Zone": "red"
}

heat_data = filtered_area[['lat', 'lng', 'energy_kwh']].dropna().values.tolist()
HeatMap(heat_data).add_to(m)

for _, row in filtered_area.dropna(subset=["lat", "lng"]).iterrows():
    folium.CircleMarker(
        location=[row["lat"], row["lng"]],
        radius=5,
        color=color_map[row["cluster_name"]],
        fill=True,
        fill_opacity=0.7,
        popup=f"""
        ZIP: {row['Zip']}<br>
        Cluster: {row['cluster_name']}<br>
        Energy: {row['energy_kwh']:.2f}<br>
        Efficiency: {row['energy_per_kw']:.2f}
        """
    ).add_to(m)

# ✅ ADD LEGEND INSIDE MAP (THIS IS THE KEY FIX)
legend_html = """
<div style="
position: fixed;
bottom: 40px; left: 40px;
background-color: white;
padding: 12px;
border-radius: 10px;
box-shadow: 0 0 10px rgba(0,0,0,0.2);
font-size: 14px;
z-index:9999;
">
<b>🌞 Solar Zones</b><br>
<span style="color:green">●</span> High Production<br>
<span style="color:blue">●</span> Medium Production<br>
<span style="color:red">●</span> Low Production
</div>
"""

m.get_root().html.add_child(folium.Element(legend_html))

st_folium(m, width=1000, height=500)

st.divider()
# ---------------------------
# CLUSTER ANALYSIS (FIXED → USING FILTERED DATA)
# ---------------------------
st.subheader("📊 Cluster Insights")

c1, c2 = st.columns(2)

with c1:
    fig1 = px.box(
        filtered_area,
        x="cluster_name",
        y="energy_per_kw",
        color="cluster_name",
        title="Energy Efficiency by Cluster"
    )
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    fig2 = px.scatter(
        filtered_area,
        x="capacity_factor",
        y="energy_per_kw",
        color="cluster_name",
        title="Efficiency vs Capacity Factor"
    )
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

st.subheader("📊 Cluster Feature Distribution")

col1, col2 = st.columns(2)

with col1:
    fig = px.box(
        filtered_area,
        x="kmeans_cluster",
        y="energy_per_kw",
        color="kmeans_cluster",
        title="Energy per kW Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.box(
        filtered_area,
        x="kmeans_cluster",
        y="capacity_factor",
        color="kmeans_cluster",
        title="Capacity Factor Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()
# ---------------------------
# CREATE MERGED DATASET
# ---------------------------
df2["Zip"] = df2["Zip"].astype(str).str.replace(".0", "", regex=False)
area_df["Zip"] = area_df["Zip"].astype(str).str.replace(".0", "", regex=False)

merged_df = df2.merge(
    area_df[["Zip", "kmeans_cluster"]],
    on="Zip",
    how="left"
)
# ---------------------------
# TIME SERIES CLUSTER EVOLUTION
# ---------------------------
st.subheader("📈 Cluster Performance Over Time")
st.caption("Year-wise energy production trends across clusters")
time_df = merged_df.groupby(
    ["Year", "kmeans_cluster"]
)["Estimated Annual PV Energy Production (kWh)"].sum().reset_index()

fig = px.line(
    time_df,
    x="Year",
    y="Estimated Annual PV Energy Production (kWh)",
    color="kmeans_cluster",
    markers=True,
    title="Energy Production Trend by Cluster"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()
# ---------------------------
# PROJECT LEVEL ANALYSIS
# ---------------------------
st.subheader("🔍 Project-Level Insights")

# Filter project data based on selected clusters
# Ensure ZIP format matches
df2["Zip"] = df2["Zip"].astype(str).str.replace(".0", "", regex=False)
area_df["Zip"] = area_df["Zip"].astype(str).str.replace(".0", "", regex=False)

# Merge cluster info
df2_merged = df2.merge(
    area_df[["Zip", "cluster_name"]],
    on="Zip",
    how="left"
)

filtered_df2 = df2_merged[df2_merged["cluster_name"].isin(cluster_filter)]

top_dev = (
    filtered_df2.groupby("Developer")
    .size()
    .sort_values(ascending=False)
    .head(10)
    .reset_index(name="count")
)

fig3 = px.bar(
    top_dev,
    x="Developer",
    y="count",
    title="Top Developers"
)


# Utility distribution
utility_dist = (
    filtered_df2.groupby("Utility")
    .size()
    .sort_values(ascending=False)
    .head(10)
    .reset_index(name="count")
)

fig4 = px.bar(
    utility_dist,
    x="Utility",
    y="count",
    title="Top Utilities"
)


col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.plotly_chart(fig4, use_container_width=True)

st.divider()
# ---------------------------
# ZIP SEARCH (IMPROVED)
# ---------------------------
st.subheader("🔎 Search by ZIP Code")

zip_input = st.text_input("Enter ZIP Code")

if zip_input:
    result = area_df[area_df["Zip"] == zip_input]

    if not result.empty:
        row = result.iloc[0]

        st.success(f"Cluster: {row['cluster_name']}")

        col1, col2 = st.columns(2)
        col1.metric("Energy", f"{row['energy_kwh']:,.0f}")
        col2.metric("Efficiency", f"{row['energy_per_kw']:.2f}")

        # Zoom map
        zoom_map = folium.Map(
            location=[row["lat"], row["lng"]],
            zoom_start=10
        )

        folium.Marker(
            [row["lat"], row["lng"]],
            popup=row["cluster_name"],
            icon=folium.Icon(color="green")
        ).add_to(zoom_map)

        st_folium(zoom_map, width=700, height=400)

    else:
        st.error("ZIP code not found")


# ---------------------------
# BUSINESS RECOMMENDATIONS
# ---------------------------
st.subheader("💡 Business Recommendations")

with st.container():
    st.markdown("""
    🟢 **Focus on High Yield Zones**  
    Maximize ROI through targeted deployment.

    📍 **Expand Underutilized Areas**  
    Capture early market advantage in high potential zones.

    🤝 **Leverage Top Developers**  
    Build strategic partnerships in high-performing regions.

    ⚠️ **Risk-Based Strategy**  
    Align investments with cluster stability.

    🔌 **Optimize Utility Partnerships**  
    Focus on strong infrastructure regions.
    """)