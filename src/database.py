import sqlite3
from pathlib import Path

import pandas as pd


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

DATABASE_PATH = DATA_DIR / "sevasetu.db"
CSV_PATH = DATA_DIR / "welfare_data.csv"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Create a connection to the SevaSetu SQLite database.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    return sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False
    )


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():
    """
    Create the welfare_data table and load the existing
    synthetic CSV dataset into SQLite.
    """

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Welfare dataset not found: {CSV_PATH}"
        )

    df = pd.read_csv(CSV_PATH)

    conn = get_connection()

    try:
        df.to_sql(
            "welfare_data",
            conn,
            if_exists="replace",
            index=False
        )

        conn.commit()

    finally:
        conn.close()

    return len(df)


# ============================================================
# READ WELFARE DATA
# ============================================================

def load_welfare_data():
    """
    Load welfare data from SQLite.
    Create the welfare table from CSV only when it is missing.
    """

    conn = get_connection()

    try:
        table = conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name='welfare_data'"
        ).fetchone()

        if table is None:
            if not CSV_PATH.exists():
                raise FileNotFoundError(
                    f"Welfare dataset not found: {CSV_PATH}"
                )

            source_df = pd.read_csv(CSV_PATH)
            source_df.to_sql(
                "welfare_data",
                conn,
                if_exists="fail",
                index=False
            )
            conn.commit()

        df = pd.read_sql_query(
            "SELECT * FROM welfare_data",
            conn
        )

    finally:
        conn.close()

    return df


# ============================================================
# DATABASE INFORMATION
# ============================================================

def get_database_info():
    """
    Return basic database information for the dashboard.
    """

    conn = get_connection()

    try:
        tables = pd.read_sql_query(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            ORDER BY name
            """,
            conn
        )

        count_result = pd.read_sql_query(
            """
            SELECT COUNT(*) AS total_rows
            FROM welfare_data
            """,
            conn
        )

    finally:
        conn.close()

    return {
        "database": str(DATABASE_PATH),
        "tables": tables["name"].tolist(),
        "welfare_rows": int(
            count_result.iloc[0]["total_rows"]
        ),
    }
    # ============================================================
# AI INVESTIGATION HISTORY
# ============================================================

def create_ai_investigation_table():
    """
    Create a table for storing officer-triggered AI investigations.
    """

    conn = get_connection()

    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ai_investigations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                district TEXT,
                block TEXT,
                priority_score REAL,
                risk_level TEXT,
                coverage REAL,
                coverage_gap REAL,
                pending_rate REAL,
                processing_days REAL,
                anomaly_status TEXT,
                ai_response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.commit()

    finally:
        conn.close()


def save_ai_investigation(area_data, ai_response):
    """
    Save an AI investigation result to SQLite.
    """

    conn = get_connection()

    try:
        conn.execute(
            """
            INSERT INTO ai_investigations (
                district,
                block,
                priority_score,
                risk_level,
                coverage,
                coverage_gap,
                pending_rate,
                processing_days,
                anomaly_status,
                ai_response
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                area_data.get("district"),
                area_data.get("block"),
                float(area_data.get("priority_score", 0)),
                area_data.get("risk_level"),
                float(area_data.get("coverage", 0)),
                float(area_data.get("coverage_gap", 0)),
                float(area_data.get("pending_rate", 0)),
                float(area_data.get("processing_days", 0)),
                area_data.get("anomaly_status"),
                ai_response,
            ),
        )

        conn.commit()

    finally:
        conn.close()


def load_ai_investigations():
    """
    Load previous AI investigations.
    """

    conn = get_connection()

    try:
        return pd.read_sql_query(
            """
            SELECT *
            FROM ai_investigations
            ORDER BY created_at DESC
            """,
            conn,
        )

    finally:
        conn.close()
        # ============================================================
# OUTREACH CANDIDATES
# ============================================================

def create_outreach_table():
    """
    Create synthetic outreach candidates for the demo.
    """

    conn = get_connection()

    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS outreach_candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                beneficiary_id TEXT NOT NULL,
                district TEXT,
                block TEXT,
                scheme TEXT,
                eligible INTEGER,
                received INTEGER,
                outreach_status TEXT DEFAULT 'Pending',
                approved INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.commit()

    finally:
        conn.close()


def load_outreach_candidates():
    """
    Load outreach candidates.
    """

    conn = get_connection()

    try:
        return pd.read_sql_query(
            """
            SELECT *
            FROM outreach_candidates
            ORDER BY created_at DESC
            """,
            conn,
        )

    finally:
        conn.close()


def add_demo_outreach_candidates():
    """
    Add synthetic beneficiaries for the hackathon demo.
    """

    candidates = [
        ("BEN-001", "Imphal East", "Block A", "Welfare Support", 1, 0),
        ("BEN-002", "Thoubal", "Block B", "Education Support", 1, 0),
        ("BEN-003", "Imphal West", "Block C", "Housing Support", 1, 0),
        ("BEN-004", "Bishnupur", "Block A", "Welfare Support", 1, 0),
        ("BEN-005", "Kakching", "Block B", "Livelihood Support", 1, 0),
    ]

    conn = get_connection()

    try:

        for candidate in candidates:

            conn.execute(
                """
                INSERT INTO outreach_candidates (
                    beneficiary_id,
                    district,
                    block,
                    scheme,
                    eligible,
                    received
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                candidate,
            )

        conn.commit()
    finally:
        conn.close()


def approve_outreach_candidate(candidate_id):
    """
    Mark an outreach candidate as approved by an officer.
    """

    conn = get_connection()

    try:
        conn.execute(
            """
            UPDATE outreach_candidates
            SET approved = 1,
                outreach_status = 'Approved'
            WHERE id = ?
            """,
            (int(candidate_id),),
        )

        conn.commit()

    finally:
        conn.close()
        
        
        
        
        # ============================================================
# INTERVENTION IMPACT TRACKING
# ============================================================

def create_intervention_table():
    """
    Store before/after welfare-service measurements.
    """
    conn = get_connection()

    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS intervention_impact (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                district TEXT,
                block TEXT,
                intervention TEXT,

                before_coverage REAL,
                after_coverage REAL,

                before_pending REAL,
                after_pending REAL,

                before_processing_days REAL,
                after_processing_days REAL,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.commit()

    finally:
        conn.close()


def add_demo_intervention_data():
    """
    Add synthetic before/after intervention records
    for the hackathon demonstration.
    """

    conn = get_connection()

    demo_records = [
        (
            "Imphal East",
            "Block A",
            "Targeted welfare outreach",
            58.0,
            76.0,
            42.0,
            24.0,
            18.0,
            11.0,
        ),
        (
            "Thoubal",
            "Block B",
            "Pending-case review",
            64.0,
            81.0,
            36.0,
            19.0,
            15.0,
            9.0,
        ),
        (
            "Bishnupur",
            "Block A",
            "Officer intervention",
            71.0,
            86.0,
            28.0,
            14.0,
            12.0,
            7.0,
        ),
    ]

    try:

        for record in demo_records:

            conn.execute(
                """
                INSERT INTO intervention_impact (
                    district,
                    block,
                    intervention,
                    before_coverage,
                    after_coverage,
                    before_pending,
                    after_pending,
                    before_processing_days,
                    after_processing_days
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                record,
            )

        conn.commit()

    finally:
        conn.close()


def load_intervention_impact():
    """
    Load intervention impact records.
    """
    conn = get_connection()

    try:

        return pd.read_sql_query(
            """
            SELECT *
            FROM intervention_impact
            ORDER BY created_at DESC
            """,
            conn,
        )

    finally:
        conn.close()
