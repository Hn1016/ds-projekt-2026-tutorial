import argparse
from pathlib import Path

from ds_projekt_2026_tutorial.answer import answer
from ds_projekt_2026_tutorial.answer_dry import answer_dry
from ds_projekt_2026_tutorial.days import WEATHER_YEARS, days
from ds_projekt_2026_tutorial.derive import derive
from ds_projekt_2026_tutorial.download import URL, WEATHER_URL, download
from ds_projekt_2026_tutorial.load import load

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
DERIVED_DIR = ROOT / "data" / "derived"


def main() -> None:
    parser = argparse.ArgumentParser(prog="build", description="Build the project's data from nothing.")
    parser.add_argument(
        "--force", action="store_true", help="rebuild every derived step; the files in data/raw stay as they are"
    )
    parser.add_argument(
        "--force-download", action="store_true", help="fetch the raw files again and rebuild every derived step"
    )
    args = parser.parse_args()
    # Raw data changes only on purpose: --force alone never downloads again.
    fetch = args.force_download
    rebuild = args.force or args.force_download

    raw = download(URL, RAW_DIR, force=fetch)
    weather = [download(WEATHER_URL.format(year=y), RAW_DIR, force=fetch) for y in WEATHER_YEARS]
    days_path = days(weather, DERIVED_DIR / "days.parquet", force=rebuild)
    counts = load(raw, DERIVED_DIR / "counts.parquet", force=rebuild)
    place_year = derive(counts, DERIVED_DIR / "place_year.parquet", force=rebuild)
    answer_all = answer(place_year, DERIVED_DIR / "answer.parquet", force=rebuild)
    answer_dry(counts, days_path, answer_all, DERIVED_DIR / "answer_dry.parquet", force=rebuild)
