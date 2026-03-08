"""
Generates simulated healthcare quality and safety data modelled on
the types of datasets managed within an HNZ Waitematā Quality & Risk context.
No real patient or organisational data is included.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

np.random.seed(42)

# ── Configuration ──
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2025, 12, 31)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data")

FACILITIES = [
    "North Shore Hospital", "Waitakere Hospital",
    "Community Services North", "Community Services West"
]

SERVICES = [
    "Emergency Department", "General Medicine", "General Surgery",
    "Orthopaedics", "Mental Health", "Maternity",
    "Paediatrics", "Older Adult Health", "Oncology", "Cardiology"
]

ETHNICITIES = ["NZ European", "Māori", "Pacific Peoples", "Asian", "Other"]
ETHNICITY_WEIGHTS = [0.45, 0.18, 0.12, 0.15, 0.10]

EVENT_CATEGORIES = [
    "Falls", "Medication Error", "Pressure Injury",
    "Clinical Deterioration", "Surgical Complication",
    "Healthcare Associated Infection", "Documentation Error",
    "Equipment Failure", "Communication Failure", "Other"
]

SEVERITY_LEVELS = ["SAC 1 - Severe", "SAC 2 - Major", "SAC 3 - Moderate", "SAC 4 - Minor"]
SEVERITY_WEIGHTS = [0.03, 0.12, 0.30, 0.55]

COMPLAINT_CATEGORIES = [
    "Communication", "Treatment/Care", "Wait Times",
    "Staff Behaviour", "Facilities/Environment",
    "Access to Services", "Discharge Process", "Other"
]


def generate_dates(n, start=START_DATE, end=END_DATE):
    """Generate random dates with seasonal variation."""
    days = (end - start).days
    random_days = np.random.randint(0, days, n)
    dates = [start + timedelta(days=int(d)) for d in random_days]
    return sorted(dates)


def generate_adverse_events(n=3000):
    """Generate synthetic adverse event records."""
    dates = generate_dates(n)

    # Create slight upward trend in reporting (positive - more reporting is good)
    facility_probs = np.array([0.40, 0.30, 0.15, 0.15])
    facilities = np.random.choice(FACILITIES, n, p=facility_probs)
    services = np.random.choice(SERVICES, n)
    ethnicities = np.random.choice(ETHNICITIES, n, p=ETHNICITY_WEIGHTS)

    # Falls and medication errors more common
    event_weights = [0.22, 0.20, 0.12, 0.10, 0.08, 0.08, 0.07, 0.05, 0.05, 0.03]
    categories = np.random.choice(EVENT_CATEGORIES, n, p=event_weights)
    severity = np.random.choice(SEVERITY_LEVELS, n, p=SEVERITY_WEIGHTS)

    ages = np.clip(np.random.normal(65, 18, n), 0, 100).astype(int)
    # Older patients more likely to have falls
    for i in range(n):
        if categories[i] == "Falls" and np.random.random() > 0.4:
            ages[i] = min(int(np.random.normal(78, 10)), 100)

    # Days to close the event
    days_to_close = np.random.exponential(15, n).astype(int)
    days_to_close = np.clip(days_to_close, 1, 120)
    # SAC 1 events take longer
    for i in range(n):
        if severity[i] == "SAC 1 - Severe":
            days_to_close[i] = min(int(np.random.exponential(45)), 120)

    # Harm levels
    harm_levels = []
    for s in severity:
        if s == "SAC 1 - Severe":
            harm_levels.append(np.random.choice(["Death", "Severe Harm"], p=[0.3, 0.7]))
        elif s == "SAC 2 - Major":
            harm_levels.append(np.random.choice(["Moderate Harm", "Severe Harm"], p=[0.7, 0.3]))
        elif s == "SAC 3 - Moderate":
            harm_levels.append(np.random.choice(["Minor Harm", "Moderate Harm"], p=[0.6, 0.4]))
        else:
            harm_levels.append(np.random.choice(["No Harm", "Minor Harm"], p=[0.5, 0.5]))

    df = pd.DataFrame({
        "event_id": [f"AE-{i+1:05d}" for i in range(n)],
        "event_date": dates,
        "facility": facilities,
        "service": services,
        "event_category": categories,
        "severity": severity,
        "harm_level": harm_levels,
        "patient_age": ages,
        "patient_ethnicity": ethnicities,
        "days_to_close": days_to_close,
        "status": np.random.choice(
            ["Closed", "Open", "Under Investigation"],
            n, p=[0.75, 0.10, 0.15]
        ),
    })

    # Add month/year columns for easier analysis
    df["month"] = pd.to_datetime(df["event_date"]).dt.to_period("M").astype(str)
    df["year"] = pd.to_datetime(df["event_date"]).dt.year

    return df


def generate_complaints(n=1500):
    """Generate synthetic patient complaint records."""
    dates = generate_dates(n)

    facilities = np.random.choice(FACILITIES, n, p=[0.35, 0.30, 0.18, 0.17])
    services = np.random.choice(SERVICES, n)
    ethnicities = np.random.choice(ETHNICITIES, n, p=ETHNICITY_WEIGHTS)

    cat_weights = [0.25, 0.20, 0.15, 0.12, 0.10, 0.08, 0.07, 0.03]
    categories = np.random.choice(COMPLAINT_CATEGORIES, n, p=cat_weights)

    resolution_days = np.random.exponential(12, n).astype(int)
    resolution_days = np.clip(resolution_days, 1, 90)

    df = pd.DataFrame({
        "complaint_id": [f"CMP-{i+1:05d}" for i in range(n)],
        "received_date": dates,
        "facility": facilities,
        "service": services,
        "category": categories,
        "patient_ethnicity": ethnicities,
        "resolution_days": resolution_days,
        "status": np.random.choice(
            ["Resolved", "Open", "In Progress"],
            n, p=[0.70, 0.12, 0.18]
        ),
        "escalated": np.random.choice([True, False], n, p=[0.15, 0.85]),
    })

    df["month"] = pd.to_datetime(df["received_date"]).dt.to_period("M").astype(str)
    df["year"] = pd.to_datetime(df["received_date"]).dt.year

    return df


def generate_quality_indicators():
    """Generate monthly KPI data across facilities."""
    months = pd.date_range(START_DATE, END_DATE, freq="MS")
    records = []

    indicators = {
        "Hand Hygiene Compliance (%)": {"base": 82, "target": 80, "trend": 0.15, "std": 3},
        "Falls per 1000 Bed Days": {"base": 5.5, "target": 5.0, "trend": -0.03, "std": 0.8},
        "Medication Errors per 1000 Admissions": {"base": 3.2, "target": 2.5, "trend": -0.02, "std": 0.5},
        "Pressure Injuries per 1000 Bed Days": {"base": 1.8, "target": 1.5, "trend": -0.01, "std": 0.3},
        "Patient Experience Score (%)": {"base": 78, "target": 85, "trend": 0.12, "std": 4},
        "HAI Rate per 1000 Bed Days": {"base": 2.1, "target": 1.5, "trend": -0.01, "std": 0.4},
        "Complaint Resolution within 20 Days (%)": {"base": 65, "target": 80, "trend": 0.20, "std": 5},
        "Adverse Event Closure within 30 Days (%)": {"base": 60, "target": 75, "trend": 0.18, "std": 5},
    }

    for idx, month in enumerate(months):
        for facility in FACILITIES:
            facility_offset = FACILITIES.index(facility) * 0.5
            for indicator_name, params in indicators.items():
                value = (
                    params["base"]
                    + params["trend"] * idx
                    + np.random.normal(0, params["std"])
                    + facility_offset * np.random.choice([-1, 1])
                )
                # Clamp percentages
                if "%" in indicator_name:
                    value = np.clip(value, 0, 100)
                else:
                    value = max(0, value)

                records.append({
                    "month": month.strftime("%Y-%m"),
                    "facility": facility,
                    "indicator": indicator_name,
                    "value": round(value, 2),
                    "target": params["target"],
                })

    return pd.DataFrame(records)


def generate_equity_data():
    """Generate health equity indicators by ethnicity."""
    months = pd.date_range(START_DATE, END_DATE, freq="MS")
    records = []

    equity_indicators = {
        "ED Wait Time (median mins)": {
            "NZ European": 120, "Māori": 145, "Pacific Peoples": 140,
            "Asian": 125, "Other": 122
        },
        "Readmission Rate (%)": {
            "NZ European": 8.5, "Māori": 12.2, "Pacific Peoples": 11.5,
            "Asian": 8.8, "Other": 9.0
        },
        "Did Not Attend Rate (%)": {
            "NZ European": 5.0, "Māori": 14.5, "Pacific Peoples": 12.0,
            "Asian": 6.5, "Other": 7.0
        },
        "Patient Experience Score (%)": {
            "NZ European": 82, "Māori": 72, "Pacific Peoples": 74,
            "Asian": 78, "Other": 79
        },
    }

    for idx, month in enumerate(months):
        for indicator, ethnicity_values in equity_indicators.items():
            for ethnicity, base_value in ethnicity_values.items():
                # Slight improvement trend for equity
                improvement = 0.05 * idx if ethnicity in ["Māori", "Pacific Peoples"] else 0.02 * idx
                if "Wait Time" in indicator or "Rate" in indicator:
                    value = base_value - improvement + np.random.normal(0, base_value * 0.05)
                else:
                    value = base_value + improvement + np.random.normal(0, base_value * 0.03)
                value = max(0, round(value, 1))

                records.append({
                    "month": month.strftime("%Y-%m"),
                    "ethnicity": ethnicity,
                    "indicator": indicator,
                    "value": value,
                })

    return pd.DataFrame(records)


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Generating adverse events data...")
    ae_df = generate_adverse_events()
    ae_df.to_csv(os.path.join(OUTPUT_DIR, "adverse_events.csv"), index=False)
    print(f"  -> {len(ae_df)} records")

    print("Generating complaints data...")
    comp_df = generate_complaints()
    comp_df.to_csv(os.path.join(OUTPUT_DIR, "complaints.csv"), index=False)
    print(f"  -> {len(comp_df)} records")

    print("Generating quality indicators...")
    qi_df = generate_quality_indicators()
    qi_df.to_csv(os.path.join(OUTPUT_DIR, "quality_indicators.csv"), index=False)
    print(f"  -> {len(qi_df)} records")

    print("Generating equity data...")
    eq_df = generate_equity_data()
    eq_df.to_csv(os.path.join(OUTPUT_DIR, "equity_indicators.csv"), index=False)
    print(f"  -> {len(eq_df)} records")

    print("\nAll data generated in ./data/")
