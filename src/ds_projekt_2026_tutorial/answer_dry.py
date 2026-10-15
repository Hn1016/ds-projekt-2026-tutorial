from pathlib import Path

import polars as pl

from ds_projekt_2026_tutorial.answer import FIRST_YEAR, LAST_YEAR, city_sentence, status_expr
from ds_projekt_2026_tutorial.derive import place_year_table

# Rules for loop two, see docs/one-pager.md and docs/log.md (2026-10-14).
OPENING = "For the city on dry weekdays"
REASON = "not comparable on all days"


def dry_counts(counts: pl.DataFrame, days: pl.DataFrame) -> pl.DataFrame:
    """The rows of counts whose date is a dry weekday in the day table."""
    dry = days.filter(pl.col("dry_weekday")).select("date")
    return counts.join(dry, left_on=pl.col("DATUM").dt.date(), right_on="date", how="semi")


def dry_place_change_table(place_year_dry: pl.DataFrame, answer_all: pl.DataFrame) -> pl.DataFrame:
    """One row per place of the loop-one answer: bikes per day on dry weekdays, the change and a status.

    A place is comparable when it is comparable in the loop-one answer; the others get
    the reason REASON and no change. The 5 percent band applies as in loop one.
    Stops with an error when a comparable place has no dry-weekday data in one of the years.
    """

    def year(y: int) -> pl.DataFrame:
        return place_year_dry.filter(pl.col("year") == y).select(
            "OST", "NORD", pl.col("bikes_per_day").alias(f"bikes_per_day_{y}")
        )

    first, last = pl.col(f"bikes_per_day_{FIRST_YEAR}"), pl.col(f"bikes_per_day_{LAST_YEAR}")
    table = (
        answer_all.select("OST", "NORD", comparable=pl.col("status") != "not comparable")
        .join(year(FIRST_YEAR), on=["OST", "NORD"], how="left")
        .join(year(LAST_YEAR), on=["OST", "NORD"], how="left")
    )
    missing = table.filter(pl.col("comparable") & (first.is_null() | last.is_null()))
    if missing.height > 0:
        places = ", ".join(f"{o}/{n}" for o, n in missing.select("OST", "NORD").iter_rows())
        raise ValueError(f"no dry-weekday data in {FIRST_YEAR} or {LAST_YEAR} for comparable places {places}")

    return (
        table.with_columns(reason=pl.when(~pl.col("comparable")).then(pl.lit(REASON)))
        .with_columns(change_percent=pl.when(pl.col("reason").is_null()).then((last - first) / first * 100))
        .with_columns(status=status_expr())
        .select("OST", "NORD", first, last, "change_percent", "status", "reason")
        .sort("OST", "NORD")
    )


def answer_dry(counts_path: Path, days_path: Path, answer_path: Path, out_path: Path, force: bool = False) -> Path:
    """Write the place change table on dry weekdays to out_path, unless it is already there. Prints the city sentence."""
    if out_path.exists() and not force:
        print(f"answer_dry: skipped, {out_path} already exists. {city_sentence(pl.read_parquet(out_path), OPENING)}")
        return out_path

    counts = dry_counts(pl.read_parquet(counts_path), pl.read_parquet(days_path))
    table = dry_place_change_table(place_year_table(counts), pl.read_parquet(answer_path))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Write to a .part file first so an interrupted run never looks complete.
    part = out_path.with_name(out_path.name + ".part")
    table.write_parquet(part)
    part.replace(out_path)

    print(f"answer_dry: wrote {out_path}. {city_sentence(table, OPENING)}")
    return out_path
