import datetime
from pathlib import Path

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from ds_projekt_2026_tutorial.days import day_table, days, read_weather

FIXTURE = Path(__file__).parent / "fixtures" / "weather_small.csv"


def test_day_table_on_fixture():
    table = day_table(read_weather(FIXTURE))
    expected = pl.DataFrame(
        {
            "date": [datetime.date(2020, 3, d) for d in range(2, 8)],
            "rain_minutes": [0.0, 12.5, None, None, None, 0.0],
            "dry_weekday": [True, False, False, False, False, False],
        }
    )
    assert_frame_equal(table, expected)


def test_day_table_stops_on_two_rain_values_for_one_day():
    weather = pl.DataFrame(
        {
            "Datum": ["2020-03-02T00:00+0100", "2020-03-02T00:00+0100"],
            "Standort": ["Zch_Stampfenbachstrasse", "Zch_Stampfenbachstrasse"],
            "Parameter": ["RainDur", "RainDur"],
            "Intervall": ["d1", "d1"],
            "Einheit": ["min", "min"],
            "Wert": [0.0, 3.0],
            "Status": ["bereinigt", "bereinigt"],
        }
    )
    with pytest.raises(ValueError, match="2020-03-02"):
        day_table(weather)


def test_days_writes_then_skips(tmp_path, capsys):
    out_path = tmp_path / "derived" / "days.parquet"

    days([FIXTURE], out_path)
    out = capsys.readouterr().out.splitlines()
    assert len(out) == 1 and "wrote" in out[0] and "6 days, 1 dry weekdays" in out[0]

    days([FIXTURE], out_path)
    out = capsys.readouterr().out.splitlines()
    assert len(out) == 1 and "skipped" in out[0]

    days([FIXTURE], out_path, force=True)
    out = capsys.readouterr().out.splitlines()
    assert len(out) == 1 and "wrote" in out[0]
