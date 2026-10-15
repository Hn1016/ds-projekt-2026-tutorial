import datetime
from pathlib import Path

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from ds_projekt_2026_tutorial.answer import city_sentence, place_change_table
from ds_projekt_2026_tutorial.answer_dry import OPENING, answer_dry, dry_counts, dry_place_change_table

FIXTURES = Path(__file__).parent / "fixtures"
DRY_FIXTURE = FIXTURES / "place_year_dry_small.csv"
ALL_FIXTURE = FIXTURES / "place_year_small.csv"
SENTENCE = (
    "For the city on dry weekdays: yes. 2 of 3 comparable places grew, 1 shrank, 0 are unchanged, "
    "2 places cannot be compared."
)


def answer_all() -> pl.DataFrame:
    return place_change_table(pl.read_csv(ALL_FIXTURE))


def test_dry_counts_keeps_only_dry_weekdays():
    days = pl.DataFrame(
        {
            # Monday dry, Tuesday wet, Saturday dry but not a weekday.
            "date": [datetime.date(2020, 3, 2), datetime.date(2020, 3, 3), datetime.date(2020, 3, 7)],
            "rain_minutes": [0.0, 12.5, 0.0],
            "dry_weekday": [True, False, False],
        }
    )
    counts = pl.DataFrame(
        {
            "DATUM": [
                datetime.datetime(2020, 3, 2, 8, 0),
                datetime.datetime(2020, 3, 2, 23, 45),
                datetime.datetime(2020, 3, 3, 8, 0),
                datetime.datetime(2020, 3, 7, 8, 0),
                datetime.datetime(2020, 3, 9, 8, 0),
            ],
            "VELO_IN": [1, 2, 3, 4, 5],
        }
    )
    kept = dry_counts(counts, days)
    assert kept["VELO_IN"].to_list() == [1, 2]


def test_dry_place_change_table_on_fixture():
    table = dry_place_change_table(pl.read_csv(DRY_FIXTURE), answer_all())
    expected = pl.DataFrame(
        {
            "OST": [1000, 3000, 5000, 7000, 9000],
            "NORD": [2000, 4000, 6000, 8000, 1000],
            "bikes_per_day_2019": [150.0, 220.0, 120.0, 60.0, None],
            "bikes_per_day_2025": [180.0, 165.0, 138.0, 90.0, 70.0],
            "change_percent": [20.0, -25.0, 15.0, None, None],
            "status": ["grew", "shrank", "grew", "not comparable", "not comparable"],
            "reason": [None, None, None, "not comparable on all days", "not comparable on all days"],
        }
    )
    assert_frame_equal(table, expected, check_dtypes=False)
    assert city_sentence(table, OPENING) == SENTENCE


def test_dry_place_change_table_stops_without_dry_data_for_a_comparable_place():
    # Place 1000/2000 is comparable in loop one but has no dry-weekday data in 2025.
    place_year_dry = pl.DataFrame(
        {"OST": [1000], "NORD": [2000], "year": [2019], "days_with_bikes": [110], "bikes_per_day": [150.0]}
    )
    with pytest.raises(ValueError, match="1000/2000"):
        dry_place_change_table(place_year_dry, answer_all())


def test_answer_dry_writes_skips_and_forces(tmp_path, capsys):
    counts_path = tmp_path / "counts.parquet"
    days_path = tmp_path / "days.parquet"
    answer_path = tmp_path / "answer.parquet"
    # Monday 2019-03-04 and Monday 2025-03-03 are dry weekdays; place 1000/2000 has bikes on both.
    pl.DataFrame(
        {
            "FK_STANDORT": [1, 1],
            "DATUM": [datetime.datetime(2019, 3, 4, 8, 0), datetime.datetime(2025, 3, 3, 8, 0)],
            "VELO_IN": [10, 12],
            "VELO_OUT": [0, 0],
            "OST": [1000, 1000],
            "NORD": [2000, 2000],
        }
    ).write_parquet(counts_path)
    pl.DataFrame(
        {
            "date": [datetime.date(2019, 3, 4), datetime.date(2025, 3, 3)],
            "rain_minutes": [0.0, 0.0],
            "dry_weekday": [True, True],
        }
    ).write_parquet(days_path)
    answer_all().filter(pl.col("OST") == 1000).write_parquet(answer_path)
    out_path = tmp_path / "derived" / "answer_dry.parquet"

    answer_dry(counts_path, days_path, answer_path, out_path)
    out = capsys.readouterr().out.splitlines()
    one_place = "yes. 1 of 1 comparable places grew, 0 shrank, 0 are unchanged, 0 places cannot be compared."
    assert len(out) == 1 and "wrote" in out[0] and out[0].endswith(f"{OPENING}: {one_place}")

    answer_dry(counts_path, days_path, answer_path, out_path)
    out = capsys.readouterr().out.splitlines()
    assert len(out) == 1 and "skipped" in out[0] and out[0].endswith(f"{OPENING}: {one_place}")

    answer_dry(counts_path, days_path, answer_path, out_path, force=True)
    out = capsys.readouterr().out.splitlines()
    assert len(out) == 1 and "wrote" in out[0]
