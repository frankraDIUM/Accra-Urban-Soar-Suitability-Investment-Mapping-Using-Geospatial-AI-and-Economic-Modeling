# 🌞 Building-Level-Solar-Suitability-Mapping-in-Urban-Ghana
**Accra Solar Rooftop Suitability & Investment Dashboard**

A geospatial AI pipeline for building-level solar potential assessment in Central Accra, Ghana.



1. Project Objective
   Develop a scalable geospatial AI pipeline to:
   - Detect and characterize individual building rooftops.
   - Assess solar suitability per building using roof geometry and environmental factors.
   - Estimate annual solar energy generation (kWh).
   - Calculate economic viability (payback period and Net Present Value).
   - Deliver an interactive dashboard for decision-makers.

2. Study Area
   
   Location: Central Accra, Ghana.
   
   Scope: Pilot area covering 632,195 buildings.
   
   Focus: Dense urban environment with high solar potential and unreliable grid power.

3. Methodology & Pipeline

   Phase 1: Building Footprints

   - Combined Google Open Buildings and Microsoft Global Building Footprints datasets.
   - Filtered to central Accra bounding box.
   
   Final dataset: 632,195 building polygons

   Phase 2: Elevation Analysis

   - Used Copernicus DEM GLO-30
   - Derived slope and aspect rasters
   - Extracted per-building slope and aspect

   Phase 3: Solar Irradiance

   Fetched NASA POWER data (2020–2025)
   
   Annual GHI: 1,779 kWh/m²/year (used as reference for methodology justification)

   Phase 4: Rooftop Geometry & Suitability

   - Calculated accurate footprint area in UTM Zone 30N
   - Introduced roof utilization factor based on slope
   - Developed weighted suitability score (0–100):

     Slope: 45%
   
     Aspect: 30%

     Usable area: 25%

   - Added nonlinear area scoring with diminishing returns

   Phase 5: Energy Generation & Economic Analysis

   - Realistic per-kW yield: 1,280 kWh/kW/year (derived from NASA GHI with local derating)
   - System sizing with practical cap (max 35 kW)
   - Cost model: fixed baseline + variable per kW + bulk discount for larger systems
   - Included self-consumption rate (65%), O&M costs, and panel degradation (0.6%/year)
   
   Calculated:
   - Annual energy generation
   - Simple payback period
   - Net Present Value (NPV) using 8.5% discount rate over 25 years


   Final Results:

   - Average payback period: 7.0 years
   - Average NPV: +55,594 GHS per building
   - Positive NPV rate: 81.5% (515,007 buildings)
   - Total Year-1 generation potential: 6,122 GWh/year

   Phase 6: Interactive Dashboard

   Built with Streamlit
   
   Features:
   - Dynamic filters (suitability score, payback period, NPV)
   - Interactive map with clustering and legend
   - Distribution charts
   - Economic insights
   - Top 20 investment opportunities
   - CSV download of filtered results


4. Technologies Used

   Python, GeoPandas, Rasterio, Folium, Streamlit, Plotly
   
   NASA POWER API, Copernicus DEM
   
   Google Earth Engine (for initial building footprints)

6. Key Files Produced

   - accra_buildings_solar_roi_final.gpkg — Main geospatial dataset (632,195 buildings)
   - accra_solar_final_summary.csv — Clean tabular summary
   - 08_streamlit_dashboard.py — Interactive web dashboard

6. Key Insights

   - Solar rooftop systems show strong economic viability across most of central Accra.
   - Roof slope and usable area are the dominant factors influencing suitability and returns.
   - Realistic modeling (self-consumption, degradation, O&M) significantly impacts payback and NPV.
   - The pipeline is modular and scalable to other urban areas in Ghana.
