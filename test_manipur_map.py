import pandas as pd
import folium
from folium.plugins import HeatMap

from src.analytics import calculate_metrics, area_summary
from src.scoring import calculate_priority_score


# ============================================================
# 1. LOAD DATA
# ============================================================

df = pd.read_csv("data/welfare_data.csv")


# ============================================================
# 2. CALCULATE WELFARE METRICS
# ============================================================

df = calculate_metrics(df)

summary = area_summary(df)

summary = calculate_priority_score(summary)


# ============================================================
# 3. CREATE DISTRICT-LEVEL SUMMARY
# ============================================================

districts = summary.groupby("district").agg(
    eligible=("eligible", "sum"),
    received=("received", "sum"),
    pending=("pending", "sum"),
    applications=("applications", "sum"),
    rejected=("rejected", "sum"),
    outreach=("outreach", "sum"),
    processing_days=("processing_days", "mean"),
    latitude=("latitude", "first"),
    longitude=("longitude", "first")
).reset_index()


# ============================================================
# 4. CALCULATE DISTRICT METRICS
# ============================================================

districts["coverage"] = (
    districts["received"] /
    districts["eligible"]
) * 100

districts["coverage"] = districts["coverage"].clip(0, 100)

districts["coverage_gap"] = (
    100 - districts["coverage"]
)

districts["pending_rate"] = (
    districts["pending"] /
    districts["applications"]
) * 100

districts["rejection_rate"] = (
    districts["rejected"] /
    districts["applications"]
) * 100


# ============================================================
# 5. CALCULATE PRIORITY SCORE
# ============================================================

districts = calculate_priority_score(districts)


# ============================================================
# 6. CLASSIFY RISK
# ============================================================

def get_risk(score):

    if score >= 75:
        return "CRITICAL", "red"

    elif score >= 50:
        return "HIGH", "orange"

    elif score >= 25:
        return "MEDIUM", "yellow"

    else:
        return "NORMAL", "green"


districts["status"] = districts["priority_score"].apply(
    lambda x: get_risk(x)[0]
)

districts["marker_color"] = districts["priority_score"].apply(
    lambda x: get_risk(x)[1]
)


# ============================================================
# 7. CREATE MANIPUR MAP
# ============================================================

manipur_map = folium.Map(
    location=[24.7, 93.9],
    zoom_start=8,
    tiles=None
)


# ============================================================
# 8. ADD MANIPUR STATE BOUNDARY
# ============================================================

folium.GeoJson(
    "data/maps/manipur.geojson",

    name="Manipur Boundary",

    style_function=lambda feature: {
        "fillColor": "#eeeeee",
        "color": "black",
        "weight": 2,
        "fillOpacity": 0.08
    }

).add_to(manipur_map)


# ============================================================
# 9. CREATE HEATMAP
# ============================================================

heat_data = []

for _, row in districts.iterrows():

    heat_data.append([
        row["latitude"],
        row["longitude"],
        row["priority_score"] / 100
    ])


HeatMap(
    heat_data,

    radius=45,

    blur=30,

    min_opacity=0.35,

    max_zoom=10

).add_to(manipur_map)


# ============================================================
# 10. ADD RISK MARKERS
# ============================================================

for _, row in districts.iterrows():

    score = row["priority_score"]

    status = row["status"]

    marker_color = row["marker_color"]


    # ========================================================
    # AI RECOMMENDATION
    # ========================================================

    if status == "CRITICAL":

        recommendation = (
            "Immediate administrative attention required. "
            "Prioritize field outreach, pending-case resolution "
            "and additional processing capacity."
        )

    elif status == "HIGH":

        recommendation = (
            "Targeted intervention recommended. "
            "Monitor pending applications and strengthen outreach."
        )

    elif status == "MEDIUM":

        recommendation = (
            "Monitor the area closely and consider targeted "
            "outreach if the coverage gap increases."
        )

    else:

        recommendation = (
            "No immediate intervention required. "
            "Continue routine monitoring."
        )


    # ========================================================
    # POPUP
    # ========================================================

    popup_html = f"""

    <div style="
        width:310px;
        font-family:Arial,sans-serif;
        line-height:1.5;
    ">

        <div style="
            font-size:21px;
            font-weight:bold;
            margin-bottom:5px;
        ">
            {row['district']}
        </div>

        <div style="
            background:{marker_color};
            color:white;
            padding:6px 10px;
            border-radius:6px;
            display:inline-block;
            font-weight:bold;
            margin-bottom:10px;
        ">
            {status}
        </div>

        <hr>

        <b>AI Priority Score</b>
        <div style="
            font-size:25px;
            font-weight:bold;
            margin:3px 0 10px 0;
        ">
            {score:.1f}/100
        </div>

        <b>Coverage:</b>
        {row['coverage']:.1f}%

        <br>

        <b>Coverage Gap:</b>
        {row['coverage_gap']:.1f}%

        <br>

        <b>Eligible:</b>
        {int(row['eligible']):,}

        <br>

        <b>Received:</b>
        {int(row['received']):,}

        <br>

        <b>Pending Cases:</b>
        {int(row['pending']):,}

        <br>

        <b>Pending Rate:</b>
        {row['pending_rate']:.1f}%

        <br>

        <b>Rejection Rate:</b>
        {row['rejection_rate']:.1f}%

        <br>

        <b>Average Processing:</b>
        {row['processing_days']:.1f} days

        <hr>

        <div style="
            font-size:15px;
            font-weight:bold;
            margin-bottom:5px;
        ">
            AI Recommended Action
        </div>

        <div style="
            background:#f5f5f5;
            padding:8px;
            border-radius:5px;
        ">
            {recommendation}
        </div>

    </div>

    """


    # ========================================================
    # CRITICAL AREAS GET LARGER RED MARKERS
    # ========================================================

    if status == "CRITICAL":

        # Outer circle
        folium.CircleMarker(

            location=[
                row["latitude"],
                row["longitude"]
            ],

            radius=19,

            color="red",

            fill=True,

            fill_color="red",

            fill_opacity=0.18,

            weight=2,

        ).add_to(manipur_map)


        # Inner critical marker
        folium.CircleMarker(

            location=[
                row["latitude"],
                row["longitude"]
            ],

            radius=12,

            color="darkred",

            fill=True,

            fill_color="red",

            fill_opacity=0.95,

            weight=3,

            popup=folium.Popup(
                popup_html,
                max_width=350
            ),

            tooltip=(
                f"🔴 CRITICAL | "
                f"{row['district']} | "
                f"Priority {score:.1f}"
            )

        ).add_to(manipur_map)


    else:

        # Normal risk markers

        radius = 10

        if status == "HIGH":
            radius = 11

        elif status == "MEDIUM":
            radius = 10

        else:
            radius = 9


        folium.CircleMarker(

            location=[
                row["latitude"],
                row["longitude"]
            ],

            radius=radius,

            color=marker_color,

            fill=True,

            fill_color=marker_color,

            fill_opacity=0.90,

            weight=2,

            popup=folium.Popup(
                popup_html,
                max_width=350
            ),

            tooltip=(
                f"{status} | "
                f"{row['district']} | "
                f"Priority {score:.1f}"
            )

        ).add_to(manipur_map)


    # ========================================================
    # AREA LABEL
    # ========================================================

    folium.map.Marker(

        location=[
            row["latitude"],
            row["longitude"]
        ],

        icon=folium.DivIcon(

            html=f"""

            <div style="
                font-size:11px;
                font-weight:bold;
                color:black;
                white-space:nowrap;

                text-shadow:
                    1px 1px 2px white,
                    -1px -1px 2px white,
                    1px -1px 2px white,
                    -1px 1px 2px white;
            ">

                {row['district']}

            </div>

            """

        )

    ).add_to(manipur_map)


# ============================================================
# 11. RISK LEGEND
# ============================================================

legend_html = """

<div style="
    position: fixed;
    bottom: 30px;
    left: 30px;

    width: 235px;

    z-index: 9999;

    background:white;

    border:2px solid #444;

    border-radius:10px;

    padding:15px;

    box-shadow:
        0 3px 12px rgba(0,0,0,0.25);

    font-family:Arial,sans-serif;
">

    <div style="
        font-size:18px;
        font-weight:bold;
        margin-bottom:12px;
    ">
        Welfare Risk Level
    </div>


    <div style="margin-bottom:8px;">

        <span style="
            display:inline-block;
            width:16px;
            height:16px;
            background:red;
            border-radius:50%;
            margin-right:8px;
        "></span>

        <b>Critical</b> — 75+

    </div>


    <div style="margin-bottom:8px;">

        <span style="
            display:inline-block;
            width:16px;
            height:16px;
            background:orange;
            border-radius:50%;
            margin-right:8px;
        "></span>

        <b>High</b> — 50–74

    </div>


    <div style="margin-bottom:8px;">

        <span style="
            display:inline-block;
            width:16px;
            height:16px;
            background:#f1c40f;
            border-radius:50%;
            margin-right:8px;
        "></span>

        <b>Medium</b> — 25–49

    </div>


    <div>

        <span style="
            display:inline-block;
            width:16px;
            height:16px;
            background:green;
            border-radius:50%;
            margin-right:8px;
        "></span>

        <b>Normal</b> — 0–24

    </div>

</div>

"""

manipur_map.get_root().html.add_child(
    folium.Element(legend_html)
)


# ============================================================
# 12. INFORMATION PANEL
# ============================================================

critical_count = len(
    districts[
        districts["priority_score"] >= 75
    ]
)

high_count = len(
    districts[
        (districts["priority_score"] >= 50)
        &
        (districts["priority_score"] < 75)
    ]
)

medium_count = len(
    districts[
        (districts["priority_score"] >= 25)
        &
        (districts["priority_score"] < 50)
    ]
)

normal_count = len(
    districts[
        districts["priority_score"] < 25
    ]
)


info_html = f"""

<div style="
    position: fixed;

    top: 20px;

    right: 20px;

    width:260px;

    z-index:9999;

    background:white;

    border:2px solid #444;

    border-radius:10px;

    padding:15px;

    box-shadow:
        0 3px 12px rgba(0,0,0,0.25);

    font-family:Arial,sans-serif;
">

    <div style="
        font-size:20px;
        font-weight:bold;
        margin-bottom:5px;
    ">
        SevaSetu AI
    </div>

    <div style="
        font-size:13px;
        color:#666;
        margin-bottom:10px;
    ">
        Manipur Welfare Intelligence
    </div>

    <hr>

    <b>Areas Analysed:</b>
    {len(districts)}

    <br><br>

    <span style="color:red;">
        🔴 Critical: {critical_count}
    </span>

    <br>

    <span style="color:orange;">
        🟠 High: {high_count}
    </span>

    <br>

    <span style="color:#b7950b;">
        🟡 Medium: {medium_count}
    </span>

    <br>

    <span style="color:green;">
        🟢 Normal: {normal_count}
    </span>

    <hr>

    <div style="
        font-size:12px;
        color:#666;
    ">
        Heatmap intensity represents
        AI-generated welfare priority.
    </div>

</div>

"""

manipur_map.get_root().html.add_child(
    folium.Element(info_html)
)


# ============================================================
# 13. LAYER CONTROL
# ============================================================

folium.LayerControl().add_to(manipur_map)


# ============================================================
# 14. SAVE MAP
# ============================================================

output_file = "data/manipur_welfare_map.html"

manipur_map.save(output_file)


# ============================================================
# 15. PRINT SUMMARY
# ============================================================

print()

print("=" * 70)

print(
    "SEVASETU AI — MANIPUR WELFARE MAP CREATED"
)

print("=" * 70)

print()

print(
    districts[
        [
            "district",
            "status",
            "coverage",
            "coverage_gap",
            "pending",
            "pending_rate",
            "priority_score"
        ]
    ]
    .sort_values(
        "priority_score",
        ascending=False
    )
    .to_string(index=False)
)

print()

print("=" * 70)

print("Critical areas:", critical_count)

print("High-risk areas:", high_count)

print("Medium-risk areas:", medium_count)

print("Normal areas:", normal_count)

print()

print("MAP FILE:")

print(output_file)

print("=" * 70)
