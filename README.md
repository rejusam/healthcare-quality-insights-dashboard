# Healthcare Quality & Safety Insights Dashboard

An interactive analytics dashboard for healthcare quality and safety data, designed around the operational context of **Health New Zealand Te Whatu Ora Waitematā**. The project uses simulated data modelled on the kinds of quality systems (adverse events, complaints, key indicators) that inform patient safety, service improvement, and regulatory reporting across a district health organisation.

> **Data disclaimer:** All data in this project is simulated. No real patient, staff, or organisational data is used.

### Live Demo

**https://healthcare-quality-insights-dashboard-fuwp49cjg9yocjj3ezksiq.streamlit.app**

Best viewed in Chrome or Edge.

---

## Table of Contents

1. [Motivation](#motivation)
2. [Dashboard Pages](#dashboard-pages)
3. [Analytical Methods](#analytical-methods)
4. [Tech Stack](#tech-stack)
5. [Getting Started](#getting-started)
6. [Project Structure](#project-structure)
7. [Data Model](#data-model)
8. [Skills & Competencies Demonstrated](#skills--competencies-demonstrated)
9. [Future Enhancements](#future-enhancements)
10. [Author](#author)

---

## Motivation

Healthcare quality and risk teams rely on timely, accurate data analysis to:

- Identify trends in adverse events and patient safety incidents
- Monitor key quality indicators against national and regional targets
- Meet reporting obligations to Te Tāhū Hauora (Health Quality & Safety Commission), Ministry of Health, and other regulatory bodies
- Support health equity goals under Te Tiriti o Waitangi
- Provide evidence-based insights to executive, divisional, and clinical leadership

This dashboard was built to consolidate those analytical workflows into a single, interactive reporting tool — comparable in function to BI platforms like Qlik — while also enabling deeper statistical analysis that goes beyond standard dashboarding.

---

## Dashboard Pages

### 1. Executive Summary
High-level KPIs and visual overview for leadership reporting:
- Total adverse events, SAC 1 (severe) count, open events, average closure time
- Monthly adverse event trends
- Severity distribution (SAC 1–4)
- Top event categories (horizontal bar chart)
- Events by facility
- **Heatmap:** Service vs Event Category cross-tabulation for pattern identification

### 2. Adverse Events Analysis
Deep-dive into patient safety events across three tabs:

- **Trends:** Monthly trend by severity (stacked area chart), year-over-year comparison by category
- **Demographics:** Patient age distribution by severity, events by ethnicity, age-group vs event category breakdown — useful for identifying at-risk populations (e.g., falls in older adults)
- **Timeliness:** Days-to-close distribution by severity (box plots), monthly average closure trend against a 30-day target line

### 3. Complaints Analysis
Tracking patient feedback and complaint resolution:
- KPIs: total complaints, average resolution days, percentage resolved within 20 days, escalation rate
- Category breakdown (pie chart) and monthly trend
- Resolution time by category (box plots with 20-day target)
- Facility vs complaint category heatmap to identify service-specific patterns

### 4. Quality Indicators & KPI Tracking
Interactive monitoring of eight quality indicators:
- **Indicators tracked:** Hand Hygiene Compliance, Falls Rate, Medication Errors, Pressure Injuries, Patient Experience Score, HAI Rate, Complaint Resolution Timeliness, Adverse Event Closure Timeliness
- Trend lines per facility with target reference lines
- **Facility benchmarking table:** Mean, Std Dev, Min, Max, Target, and meeting-target status
- **Statistical Process Control (SPC) chart:** Mean line with Upper/Lower Control Limits (3-sigma) to distinguish common-cause from special-cause variation

### 5. Health Equity — Te Tiriti o Waitangi
Dedicated analysis supporting equitable health outcomes for Māori:
- Equity indicators tracked by ethnicity: ED Wait Time, Readmission Rate, Did Not Attend Rate, Patient Experience Score
- Trend lines by ethnicity over time
- **Gap analysis table:** Disparity measurement against NZ European baseline, highlighting where targeted improvement is needed
- Adverse event rates by ethnicity including SAC 1 counts and closure times

### 6. Statistical Deep Dive
Evidence-based analysis using formal statistical methods:

- **Hypothesis Testing:**
  - *Mann-Whitney U Test:* Are SAC 1 events taking significantly longer to close than other severity levels?
  - *Kruskal-Wallis Test:* Does complaint category significantly affect resolution time? (Informs resource allocation)
  - *Chi-Square Test of Independence:* Is event severity distribution consistent across facilities, or are there site-specific patterns?
- **Correlation Analysis:**
  - Spearman rank correlation between patient age and days to close
  - Scatter plot with OLS trendline, coloured by severity
  - Correlation matrix heatmap
- **Time Series Decomposition:**
  - Additive decomposition (period=12) of monthly adverse events into trend, seasonal, and residual components
  - Identifies underlying direction, recurring seasonal patterns (e.g., winter peaks), and anomalous months for investigation

### 7. Report Generator
Automated report preparation for various audiences:
- **Monthly Quality Summary:** Aggregated KPIs in a single view
- **Adverse Events Detail:** Full event-level data, sortable and filterable
- **Complaints Summary:** Complete complaint records
- **Equity Indicators:** Pivoted summary with mean, std dev, min, max by ethnicity and indicator
- **KPI Benchmarking:** All indicators benchmarked across facilities
- **Export options:** Download as CSV or multi-sheet Excel workbook for further analysis or distribution

---

## Analytical Methods

| Method | Application | Library |
|---|---|---|
| Trend analysis | Monthly/yearly event and complaint trends | Pandas, Plotly |
| Statistical Process Control | SPC charts with 3-sigma UCL/LCL | NumPy, Plotly |
| Mann-Whitney U test | Comparing closure times across severity levels | SciPy |
| Kruskal-Wallis H test | Comparing resolution times across complaint categories | SciPy |
| Chi-Square test | Testing independence of severity vs facility | SciPy |
| Spearman correlation | Assessing monotonic relationships between variables | SciPy |
| OLS regression | Trendline fitting on scatter plots | Plotly (statsmodels) |
| Time series decomposition | Separating trend, seasonal, and residual components | Statsmodels |
| Cross-tabulation & heatmaps | Identifying patterns across two categorical dimensions | Pandas, Plotly |
| Benchmarking | Comparing facility performance against targets | Pandas |
| Gap analysis | Measuring equity disparities across ethnic groups | Pandas |

---

## Tech Stack

| Technology | Role |
|---|---|
| **Python 3.11** | Core language |
| **Streamlit** | Interactive web application framework (comparable to BI tools like Qlik for dashboarding) |
| **Pandas** | Data manipulation, aggregation, cross-tabulation, pivoting |
| **NumPy** | Numerical operations, statistical calculations |
| **Plotly** | Interactive charts — line, bar, pie, area, box, scatter, heatmap, subplots |
| **SciPy** | Hypothesis testing (Mann-Whitney U, Kruskal-Wallis, Chi-Square, Spearman) |
| **Statsmodels** | Time series decomposition |
| **OpenPyXL / XlsxWriter** | Excel report generation |

---

## Getting Started

### Prerequisites
- Python 3.9+ (3.11 recommended)
- pip or conda

### Installation

```bash
# Clone the repository
git clone https://github.com/rejusam/healthcare-quality-insights-dashboard.git
cd healthcare-quality-insights-dashboard

# Install dependencies
pip install -r requirements.txt

# Generate the simulated datasets
python generate_data.py

# Launch the dashboard
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`.

### Using the Dashboard
1. Use the **sidebar navigation** to switch between pages
2. Apply **Year** and **Facility** filters in the sidebar — all pages respond to these filters
3. On the Quality Indicators page, use the **dropdown** to select different KPIs
4. On the Statistical Deep Dive page, explore the three tabs for different analysis types
5. Use the **Report Generator** to export data as CSV or Excel

---

## Project Structure

```
├── app.py                  # Main Streamlit dashboard application
├── generate_data.py        # Simulated data generation script
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── data/                   # Generated datasets (CSV)
│   ├── adverse_events.csv      # 3,000 adverse event records
│   ├── complaints.csv          # 1,500 complaint records
│   ├── quality_indicators.csv  # Monthly KPIs across 4 facilities
│   └── equity_indicators.csv   # Ethnicity-based equity metrics
└── .streamlit/
    └── config.toml         # Streamlit theme (HNZ Waitematā teal palette)
```

---

## Data Model

### Adverse Events (`adverse_events.csv`)
| Field | Description |
|---|---|
| `event_id` | Unique identifier (AE-00001 format) |
| `event_date` | Date the event occurred |
| `facility` | North Shore Hospital, Waitakere Hospital, Community Services North/West |
| `service` | Clinical service (ED, General Medicine, Surgery, etc.) |
| `event_category` | Falls, Medication Error, Pressure Injury, Clinical Deterioration, etc. |
| `severity` | SAC 1 (Severe) through SAC 4 (Minor) |
| `harm_level` | Death, Severe Harm, Moderate Harm, Minor Harm, No Harm |
| `patient_age` | Patient age at time of event |
| `patient_ethnicity` | NZ European, Māori, Pacific Peoples, Asian, Other |
| `days_to_close` | Working days from event to closure |
| `status` | Closed, Open, Under Investigation |

### Complaints (`complaints.csv`)
| Field | Description |
|---|---|
| `complaint_id` | Unique identifier (CMP-00001 format) |
| `received_date` | Date complaint was received |
| `facility` | Facility the complaint relates to |
| `service` | Clinical service |
| `category` | Communication, Treatment/Care, Wait Times, Staff Behaviour, etc. |
| `patient_ethnicity` | Ethnicity of complainant |
| `resolution_days` | Days to resolve |
| `status` | Resolved, Open, In Progress |
| `escalated` | Whether complaint was escalated |

### Quality Indicators (`quality_indicators.csv`)
Monthly KPI values per facility, each with a defined target. Includes Hand Hygiene Compliance, Falls Rate, Medication Errors, Pressure Injuries, Patient Experience, HAI Rate, Complaint Resolution, and AE Closure timeliness.

### Equity Indicators (`equity_indicators.csv`)
Monthly values by ethnicity for ED Wait Time, Readmission Rate, DNA Rate, and Patient Experience Score — designed to surface disparities and track progress toward equitable outcomes.

---

## Skills & Competencies Demonstrated

### Data Analysis
- Trend identification across multiple dimensions (time, facility, severity, ethnicity)
- Cross-tabulation and pattern recognition using heatmaps
- Benchmarking facility performance against defined targets
- Data integrity considerations embedded in the generation logic (realistic distributions, correlated fields)

### Statistical Analysis
- Non-parametric hypothesis testing (Mann-Whitney U, Kruskal-Wallis) — appropriate for non-normally distributed healthcare data
- Chi-Square test of independence for categorical associations
- Spearman correlation for ordinal/non-linear relationships
- Statistical Process Control with control limits for ongoing monitoring
- Time series decomposition to separate signal from noise

### Reporting & BI
- Interactive dashboard with filters, drill-downs, and multiple views — functionally comparable to Qlik or similar BI tools
- Automated report templates for different audiences (executive summary, detailed data, benchmarking)
- Data export to CSV and multi-sheet Excel workbooks
- Report layouts designed for both on-screen presentation and downstream use

### Healthcare Quality Domain
- SAC (Severity Assessment Code) classification framework
- Adverse event and complaint management workflows
- Quality indicator monitoring aligned with national reporting requirements
- Understanding of healthcare-specific metrics (HAI rates, falls per bed days, hand hygiene compliance)
- Familiarity with regulatory context (Te Tāhū Hauora, Ministry of Health)

### Health Equity — Te Tiriti o Waitangi
- Ethnicity-stratified analysis to identify and monitor health disparities
- Gap analysis methodology with explicit equity framing
- Design choices that foreground Māori health outcomes alongside other populations
- Supports evidence base for targeted quality improvement initiatives

### Database & Data Management Concepts
- Structured, relational data modelling (normalised tables with consistent keys)
- Data generation reflecting real-world distributions and correlations
- Scalable architecture — data layer separated from presentation layer

### Technical Proficiency
- Python: Pandas, NumPy, SciPy, Statsmodels, Plotly
- Interactive web application development (Streamlit)
- Data export and interoperability (CSV, Excel)
- Version control (Git/GitHub)
- Clean, modular, well-documented code

---

## Future Enhancements

- SQL integration (e.g., Snowflake, MS SQL Server) for direct database connectivity
- Automated scheduled reporting via email
- User authentication and role-based access
- Integration with RL-6 / Quality Hub data formats
- Predictive modelling for adverse event risk scoring
- Natural language report generation

---

## Author

**Reju Sam John, PhD**

Data analyst and researcher with expertise in statistical modelling, data visualisation, and healthcare analytics. Background in epidemiological modelling, predictive analytics, and large-scale data analysis.

- GitHub: [github.com/rejusam](https://github.com/rejusam)
