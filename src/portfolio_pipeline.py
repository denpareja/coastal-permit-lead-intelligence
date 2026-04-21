from pathlib import Path
import random
import string

import pandas as pd


# =========================
# CONFIG
# =========================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "output"

DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42
N_RECORDS = 250
TARGET_COUNTIES = ["MIAMI-DADE", "BROWARD", "PALM BEACH"]


# =========================
# SYNTHETIC DATA
# =========================
COUNTIES = [
    "MIAMI-DADE",
    "BROWARD",
    "PALM BEACH",
    "MONROE",
    "PINELLAS",
    "LEE",
    "SARASOTA",
]

CITIES_BY_COUNTY = {
    "MIAMI-DADE": ["Miami", "Miami Beach", "Aventura", "Key Biscayne"],
    "BROWARD": ["Fort Lauderdale", "Hollywood", "Pompano Beach", "Dania Beach"],
    "PALM BEACH": ["West Palm Beach", "Boca Raton", "Delray Beach", "Jupiter"],
    "MONROE": ["Key Largo", "Islamorada", "Marathon", "Key West"],
    "PINELLAS": ["St. Petersburg", "Clearwater", "Largo", "Tarpon Springs"],
    "LEE": ["Fort Myers", "Cape Coral", "Sanibel", "Bonita Springs"],
    "SARASOTA": ["Sarasota", "Venice", "Longboat Key", "North Port"],
}

PERMITTING_PROGRAMS = [
    "Coastal Construction Control Line",
    "Beach and Shore Preservation",
    "Environmental Resource Permit",
    "Joint Coastal Permit",
]

PERMIT_TYPES = [
    "Seawall Repair",
    "Marina Expansion",
    "Dune Restoration",
    "Shoreline Stabilization",
    "Dock Replacement",
    "Bulkhead Improvement",
    "Living Shoreline",
    "Waterfront Redevelopment",
]

STATUSES = [
    "Pending",
    "Issued",
    "Under Review",
    "Additional Info Requested",
    "Closed",
]

HIGH_VALUE_COMPANIES = [
    "Atlantic Marina Holdings LLC",
    "Bluewater Resort Group",
    "Coastal Infrastructure Partners",
    "Harborfront Development Corp",
    "Seaside Port Authority",
    "Sunshore Hospitality Group",
]

MID_VALUE_COMPANIES = [
    "Bayline Property Services LLC",
    "Ocean Crest Condo Association",
    "Palm Edge Construction LLC",
    "Tideview Engineering Inc",
    "Watermark Site Services",
    "South Coast Builders LLC",
]

FIRST_NAMES = [
    "Maria", "John", "Ana", "Daniel", "Laura", "Peter",
    "Alex", "Jordan", "Taylor", "Morgan", "Casey",
    "Chris", "Sam", "Jamie", "Drew", "Cameron"
]

LAST_NAMES = [
    "Garcia", "Smith", "Johnson", "Rodriguez",
    "Miller", "Brown", "Taylor", "Davis"
]

PROJECT_PREFIXES = [
    "Harbor", "Ocean", "Bay", "Palm", "Seaside", "Coral", "Tide", "Anchor"
]

PROJECT_SUFFIXES = [
    "Point", "Landing", "Cove", "Pier", "Marina", "Village", "Shore", "Terminal"
]


def random_application_number(rng: random.Random) -> str:
    letters = "".join(rng.choices(string.ascii_uppercase, k=3))
    digits = "".join(rng.choices(string.digits, k=6))
    return f"ERP-{letters}-{digits}"


def random_address(rng: random.Random, city: str) -> str:
    street_number = rng.randint(100, 9999)
    street_name = rng.choice([
        "Ocean Dr",
        "Harbor Blvd",
        "Seaside Ave",
        "Marina Way",
        "Coastal Hwy",
        "Bayshore Rd",
        "Palm Shore Ln",
    ])
    return f"{street_number} {street_name}, {city}, FL"


def random_project_name(rng: random.Random, permit_type: str) -> str:
    return f"{rng.choice(PROJECT_PREFIXES)} {rng.choice(PROJECT_SUFFIXES)} {permit_type}"


def pick_company_and_contact(rng: random.Random) -> tuple[str, str]:
    profile = rng.choices(
        population=["high", "mid", "individual"],
        weights=[0.35, 0.45, 0.20],
        k=1,
    )[0]

    contact = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"

    if profile == "high":
        return rng.choice(HIGH_VALUE_COMPANIES), contact
    if profile == "mid":
        return rng.choice(MID_VALUE_COMPANIES), contact
    return "", contact


def build_synthetic_dataset() -> pd.DataFrame:
    rng = random.Random(RANDOM_SEED)
    rows = []

    for _ in range(N_RECORDS):
        county = rng.choice(COUNTIES)
        city = rng.choice(CITIES_BY_COUNTY[county])
        permit_type = rng.choice(PERMIT_TYPES)
        company, contact = pick_company_and_contact(rng)
        program = rng.choice(PERMITTING_PROGRAMS)
        status = rng.choices(
            population=STATUSES,
            weights=[0.30, 0.25, 0.20, 0.15, 0.10],
            k=1,
        )[0]

        received_date = pd.Timestamp("2025-01-01") + pd.to_timedelta(
            rng.randint(0, 450), unit="D"
        )

        row = {
            "application_number": random_application_number(rng),
            "county": county,
            "city": city,
            "permitting_program": program,
            "permit_type": permit_type,
            "permit_status": status,
            "project_name": random_project_name(rng, permit_type),
            "applicant_name": contact,
            "applicant_company": company,
            "street_address": random_address(rng, city),
            "received_date": received_date.date().isoformat(),
            "estimated_project_value_usd": rng.randrange(75000, 2500000, 5000),
            "detail_url": f"https://example.com/permits/{random_application_number(rng).lower()}",
        }
        rows.append(row)

    return pd.DataFrame(rows)


# =========================
# LEAD SCORING
# =========================
def score_lead(row: pd.Series) -> str:
    high_keywords = [
        "PORT",
        "AUTHORITY",
        "RESORT",
        "HOSPITALITY",
        "MARINA",
        "INFRASTRUCTURE",
        "DEVELOPMENT",
    ]

    medium_keywords = [
        "CONDO",
        "ASSOCIATION",
        "BUILDERS",
        "ENGINEERING",
        "SERVICES",
        "LLC",
        "INC",
    ]

    company = str(row.get("applicant_company", "")).upper()
    project = str(row.get("project_name", "")).upper()
    status = str(row.get("permit_status", "")).upper()

    if any(keyword in company for keyword in high_keywords):
        return "High"

    if any(keyword in project for keyword in ["MARINA", "TERMINAL", "HARBOR"]):
        return "High"

    if status == "PENDING" and any(keyword in company for keyword in medium_keywords):
        return "Medium"

    if company.strip() == "":
        return "Low"

    return "Medium"


def filter_and_rank_leads(df: pd.DataFrame) -> pd.DataFrame:
    relevant_programs = [
        "Beach and Shore Preservation",
        "Coastal Construction Control Line",
        "Joint Coastal Permit",
    ]

    active_statuses = [
        "Pending",
        "Issued",
        "Under Review",
    ]

    filtered = df[
        (df["county"].isin(TARGET_COUNTIES))
        & (df["permitting_program"].isin(relevant_programs))
        & (df["permit_status"].isin(active_statuses))
    ].copy()

    filtered["lead_priority"] = filtered.apply(score_lead, axis=1)

    priority_order = {"High": 1, "Medium": 2, "Low": 3}
    filtered["priority_rank"] = filtered["lead_priority"].map(priority_order)

    filtered.sort_values(
        by=["priority_rank", "county", "city", "estimated_project_value_usd"],
        ascending=[True, True, True, False],
        inplace=True,
    )

    columns = [
        "application_number",
        "county",
        "city",
        "permitting_program",
        "permit_type",
        "permit_status",
        "project_name",
        "applicant_name",
        "applicant_company",
        "street_address",
        "received_date",
        "estimated_project_value_usd",
        "lead_priority",
        "detail_url",
    ]

    filtered = filtered[columns].copy()

    rename_map = {
        "application_number": "Application Number",
        "county": "County",
        "city": "City",
        "permitting_program": "Permitting Program",
        "permit_type": "Permit Type",
        "permit_status": "Permit Status",
        "project_name": "Project Name",
        "applicant_name": "Applicant Name",
        "applicant_company": "Applicant Company",
        "street_address": "Street Address",
        "received_date": "Received Date",
        "estimated_project_value_usd": "Estimated Project Value (USD)",
        "lead_priority": "Lead Priority",
        "detail_url": "Detail URL",
    }

    filtered.rename(columns=rename_map, inplace=True)
    return filtered


# =========================
# RUN
# =========================
def main() -> None:
    print("Starting synthetic portfolio pipeline...")

    df_raw = build_synthetic_dataset()
    print(f"Generated raw records: {len(df_raw)}")

    raw_csv = DATA_RAW_DIR / "synthetic_coastal_permits_raw.csv"
    processed_csv = DATA_PROCESSED_DIR / "synthetic_coastal_leads_processed.csv"
    output_excel = OUTPUT_DIR / "synthetic_coastal_leads_ranked.xlsx"

    df_raw.to_csv(raw_csv, index=False)

    df_processed = filter_and_rank_leads(df_raw)
    print(f"Filtered leads: {len(df_processed)}")

    df_processed.to_csv(processed_csv, index=False)
    df_processed.to_excel(output_excel, index=False)

    print(f"Saved raw CSV: {raw_csv}")
    print(f"Saved processed CSV: {processed_csv}")
    print(f"Saved Excel: {output_excel}")
    print("\nPreview:")
    print(df_processed.head())
    print("\nDone.")


if __name__ == "__main__":
    main()
