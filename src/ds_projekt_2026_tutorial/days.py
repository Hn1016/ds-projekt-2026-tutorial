from pathlib import Path

import polars as pl

# Rules for loop two, see docs/one-pager.md and docs/log.md (2026-10-14).
WEATHER_YEARS = (2019, 2025)
STATION = "Zch_Stampfenbachstrasse"
PARAMETER = "RainDur"


def read_weather(path: Path) -> pl.DataFrame:
    """Read one daily weather CSV; NA and an empty field both mean missing."""
    return pl.read_csv(path, null_values=["NA", ""], schema_overrides={"Wert": pl.Float64, "Datum": pl.String})


def day_table(weather: pl.DataFrame) -> pl.DataFrame:
    """One row per day that appears in the weather table: rain minutes at STATION and the dry_weekday flag.

    The date is the first 10 characters of Datum, the local date as the file gives it.
    A dry weekday is Monday to Friday with zero minutes of rain; a day without a
    known rain value is not dry. Stops with an error when a day has more than one
    rain value at STATION.
    """
    weather = weather.with_columns(date=pl.col("Datum").str.slice(0, 10).str.to_date("%Y-%m-%d"))
    rain = weather.filter((pl.col("Standort") == STATION) & (pl.col("Parameter") == PARAMETER)).select(
        "date", rain_minutes=pl.col("Wert")
    )
    repeated = rain.filter(pl.col("date").is_duplicated())["date"].unique().sort()
    if repeated.len() > 0:
        raise ValueError(f"more than one {PARAMETER} value at {STATION} on {', '.join(map(str, repeated))}")

    return (
        weather.select("date")
        .unique()
        .join(rain, on="date", how="left")
        .with_columns(
            dry_weekday=((pl.col("date").dt.weekday() <= 5) & (pl.col("rain_minutes") == 0)).fill_null(False)
        )
        .sort("date")
    )


def days(weather_paths: list[Path], out_path: Path, force: bool = False) -> Path:
    """Write the day table for the weather files to out_path, unless it is already there."""
    if out_path.exists() and not force:
        print(f"days: skipped, {out_path} already exists")
        return out_path

    table = day_table(pl.concat([read_weather(p) for p in weather_paths]))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Write to a .part file first so an interrupted run never looks complete.
    part = out_path.with_name(out_path.name + ".part")
    table.write_parquet(part)
    part.replace(out_path)

    print(f"days: wrote {out_path} ({table.height} days, {table['dry_weekday'].sum()} dry weekdays)")
    return out_path
