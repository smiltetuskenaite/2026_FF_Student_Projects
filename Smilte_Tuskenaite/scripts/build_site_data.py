"""Prepare the data for the website.

Joins the raw flicker fusion table with the common names, and passes the
analysis results to the website as small JavaScript files it can load.

Reads:  data/raw/flicker_fusion_raw.csv, data/species_names.csv,
        results/fit_summary.csv, results/cff_vs_mass.png
Writes: site/species_data.js, site/fit_data.js, site/results/cff_vs_mass.png
Run from the project folder:  python scripts/build_site_data.py
"""
import json
import shutil
from pathlib import Path

import pandas as pd

# Paths: defined once here, used everywhere below
ROOT = Path(__file__).resolve().parent.parent
RAW_FILE = ROOT / "data" / "raw" / "flicker_fusion_raw.csv"
NAMES_FILE = ROOT / "data" / "species_names.csv"
FIT_FILE = ROOT / "results" / "fit_summary.csv"
PLOT_FILE = ROOT / "results" / "cff_vs_mass.png"
SITE_DIR = ROOT / "site"
SITE_RESULTS_DIR = SITE_DIR / "results"

SITE_DIR.mkdir(exist_ok=True)
SITE_RESULTS_DIR.mkdir(exist_ok=True)


def write_js_variable(name, records, out_file):
    """Write records as a JavaScript variable, so index.html works by double-click."""
    out_file.write_text(
        f"const {name} = " + json.dumps(records, indent=2) + ";\n",
        encoding="utf-8",
    )


# --- 1. Species data: raw table + common names ---------------------------
species = pd.read_csv(RAW_FILE)
names = pd.read_csv(NAMES_FILE)

# Add the common name to each species, matching on species_id.
table = species.merge(names, on="species_id", how="left")

# Stop with a clear message if any species has no common name.
missing = table[table["common_name"].isna()]
if len(missing) > 0:
    raise SystemExit(f"No common name for: {list(missing['species_id'])}")

columns = ["species_id", "common_name", "latin_name",
           "flicker_fusion_hz", "body_mass_g", "light_level"]
records = table[columns].to_dict(orient="records")

species_file = SITE_DIR / "species_data.js"
write_js_variable("SPECIES", records, species_file)
print("Saved:", species_file, "with", len(records), "species")

# --- 2. Copy the latest plot into the site folder ------------------------
# so the website folder is self-contained
shutil.copy(PLOT_FILE, SITE_RESULTS_DIR / PLOT_FILE.name)
print("Copied cff_vs_mass.png into site/results")

# --- 3. Analysis results for the plot's trend lines and result box -------
fit = pd.read_csv(FIT_FILE)
write_js_variable("FIT", fit.to_dict(orient="records"), SITE_DIR / "fit_data.js")
print("Saved fit_data.js")