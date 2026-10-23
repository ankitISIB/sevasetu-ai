import folium
from folium.plugins import HeatMap


# ============================================================
# MANIPUR MAP
# ============================================================

def create_manipur_map(df):

    # --------------------------------------------------------
    # Create base map
    # --------------------------------------------------------

    m = folium.Map(
        location=[24.75, 93.95],
        zoom_start=8,
        tiles=None
    )

    # --------------------------------------------------------
    # Load Manipur GeoJSON
    # --------------------------------------------------------

    geojson_path = "data/maps/manipur.geojson"

    try:

        folium.GeoJson(
            geojson_path,
            name="Manipur Boundary",
            style_function=lambda feature: {
                "fillColor": "#eeeeee",
                "color": "#333333",
                "weight": 2,
                "fillOpacity": 0.15
            }
        ).add_to(m)

    except Exception as e:

        print("GeoJSON loading error:", e)

    # --------------------------------------------------------
    # Prepare map data
    # --------------------------------------------------------

    map_df = df.copy()

    # Synthetic coordinates used for demonstration.
    # These are NOT real beneficiary locations.

    if "latitude" not in map_df.columns:

        coordinates = [
            (24.82, 93.95),
            (24.65, 93.88),
            (24.90, 94.10),
            (24.55, 93.75),
            (24.78, 94.20),
            (24.95, 93.80),
            (24.45, 94.05),
            (24.70, 94.35),
            (24.35, 93.90),
            (25.00, 94.25),
            (24.60, 94.25),
            (24.85, 94.40),
            (24.40, 94.20),
            (24.75, 93.65),
            (24.95, 94.45),
            (24.50, 93.95)
        ]

        # Repeat coordinates if more areas are present
        while len(coordinates) < len(map_df):

            coordinates.extend(coordinates)

        coordinates = coordinates[:len(map_df)]

        map_df["latitude"] = [
            x[0] for x in coordinates
        ]

        map_df["longitude"] = [
            x[1] for x in coordinates
        ]

    # --------------------------------------------------------
    # Risk classification
    # --------------------------------------------------------

    def get_risk(score):

        if score >= 75:
            return "CRITICAL"

        elif score >= 50:
            return "HIGH"

        elif score >= 25:
            return "MEDIUM"

        return "NORMAL"

    map_df["risk"] = map_df["priority_score"].apply(
        get_risk
    )

    # --------------------------------------------------------
    # Risk colors
    # --------------------------------------------------------

    risk_colors = {
        "CRITICAL": "red",
        "HIGH": "orange",
        "MEDIUM": "beige",
        "NORMAL": "green"
    }

    # --------------------------------------------------------
    # Heatmap
    # --------------------------------------------------------

    heat_data = []

    for _, row in map_df.iterrows():

        heat_data.append([
            row["latitude"],
            row["longitude"],
            float(row["priority_score"]) / 100
        ])

    if heat_data:

        HeatMap(
            heat_data,
            radius=35,
            blur=25,
            min_opacity=0.35,
            max_zoom=10
        ).add_to(m)

    # --------------------------------------------------------
    # Markers
    # --------------------------------------------------------

    for _, row in map_df.iterrows():

        risk = row["risk"]

        color = risk_colors[risk]

        priority = float(row["priority_score"])

        coverage = float(row["coverage"])

        gap = float(row["coverage_gap"])

        pending = int(row["pending"])

        pending_rate = float(row["pending_rate"])

        rejection_rate = float(
            row["rejection_rate"]
        )

        processing_days = float(
            row["processing_days"]
        )

        district = row["district"]

        # ----------------------------------------------------
        # Recommended action
        # ----------------------------------------------------

        if risk == "CRITICAL":

            recommendation = (
                "Immediate intervention required. "
                "Prioritize pending-case clearance, "
                "field verification and targeted welfare outreach."
            )

        elif risk == "HIGH":

            recommendation = (
                "Increase monitoring, accelerate pending cases "
                "and conduct targeted outreach."
            )

        elif risk == "MEDIUM":

            recommendation = (
                "Monitor coverage and processing performance "
                "and consider additional outreach."
            )

        else:

            recommendation = (
                "Continue routine monitoring and service delivery."
            )

        # ----------------------------------------------------
        # Popup
        # ----------------------------------------------------

        popup_html = f"""
        <div style="
            width:300px;
            font-family:Arial;
        ">

            <h3 style="margin-bottom:5px;">
                📍 {district}
            </h3>

            <hr>

            <b>Risk:</b>
            <span style="
                color:{color};
                font-weight:bold;
            ">
                {risk}
            </span>

            <br><br>

            <b>Priority Score:</b>
            {priority:.1f}/100

            <br>

            <b>Coverage:</b>
            {coverage:.1f}%

            <br>

            <b>Coverage Gap:</b>
            {gap:.1f}%

            <hr>

            <b>Pending Cases:</b>
            {pending:,}

            <br>

            <b>Pending Rate:</b>
            {pending_rate:.1f}%

            <br>

            <b>Rejection Rate:</b>
            {rejection_rate:.1f}%

            <br>

            <b>Avg Processing:</b>
            {processing_days:.1f} days

            <hr>

            <b>🤖 AI Recommended Action</b>

            <p>
                {recommendation}
            </p>

        </div>
        """

        # ----------------------------------------------------
        # Critical outer marker
        # ----------------------------------------------------

        if risk == "CRITICAL":

            folium.CircleMarker(
                location=[
                    row["latitude"],
                    row["longitude"]
                ],
                radius=15,
                color="red",
                fill=False,
                weight=4,
                opacity=0.8
            ).add_to(m)

        # ----------------------------------------------------
        # Main marker
        # ----------------------------------------------------

        folium.CircleMarker(
            location=[
                row["latitude"],
                row["longitude"]
            ],
            radius=9 if risk != "CRITICAL" else 11,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            weight=2,
            popup=folium.Popup(
                popup_html,
                max_width=350
            ),
            tooltip=(
                f"{district} | "
                f"{risk} | "
                f"Priority {priority:.1f}"
            )
        ).add_to(m)

        # ----------------------------------------------------
        # Area label
        # ----------------------------------------------------

        folium.Marker(
            location=[
                row["latitude"],
                row["longitude"]
            ],
            icon=folium.DivIcon(
                html=f"""
                <div style="
                    font-size:11px;
                    font-weight:bold;
                    color:#222;
                    white-space:nowrap;
                    margin-left:10px;
                    margin-top:-5px;
                ">
                    {district}
                </div>
                """
            )
        ).add_to(m)

    # --------------------------------------------------------
    # Legend
    # --------------------------------------------------------

    legend_html = """
    <div style="
        position: fixed;
        bottom: 30px;
        left: 30px;
        z-index: 9999;
        background: white;
        padding: 12px;
        border: 2px solid #777;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        font-size: 13px;
    ">

        <b>Welfare Risk Level</b>

        <br><br>

        <span style="color:red;">●</span>
        Critical (75+)

        <br>

        <span style="color:orange;">●</span>
        High (50–74)

        <br>

        <span style="color:#d8c27c;">●</span>
        Medium (25–49)

        <br>

        <span style="color:green;">●</span>
        Normal (&lt;25)

    </div>
    """

    m.get_root().html.add_child(
        folium.Element(legend_html)
    )

    # --------------------------------------------------------
    # Information panel
    # --------------------------------------------------------

    critical_count = len(
        map_df[map_df["risk"] == "CRITICAL"]
    )

    high_count = len(
        map_df[map_df["risk"] == "HIGH"]
    )

    medium_count = len(
        map_df[map_df["risk"] == "MEDIUM"]
    )

    normal_count = len(
        map_df[map_df["risk"] == "NORMAL"]
    )

    info_html = f"""
    <div style="
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        background: white;
        padding: 12px 15px;
        border-radius: 8px;
        border: 2px solid #777;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        font-size: 13px;
    ">

        <b>🗺️ Manipur Welfare Intelligence</b>

        <br><br>

        🔴 Critical:
        <b>{critical_count}</b>

        <br>

        🟠 High:
        <b>{high_count}</b>

        <br>

        🟡 Medium:
        <b>{medium_count}</b>

        <br>

        🟢 Normal:
        <b>{normal_count}</b>

    </div>
    """

    m.get_root().html.add_child(
        folium.Element(info_html)
    )

    # --------------------------------------------------------
    # Layer control
    # --------------------------------------------------------

    folium.LayerControl().add_to(m)

    return m
