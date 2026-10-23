from pathlib import Path

import polars as pl
from test_answer import SENTENCE
from test_answer_dry import SENTENCE as DRY_SENTENCE

from ds_projekt_2026_tutorial.answer import city_sentence, place_change_table
from ds_projekt_2026_tutorial.answer_dry import dry_place_change_table
from ds_projekt_2026_tutorial.result import result, result_markdown

FIXTURES = Path(__file__).parent / "fixtures"


def test_result_markdown_on_fixture():
    table = place_change_table(pl.read_csv(FIXTURES / "place_year_small.csv"))
    lines = result_markdown([(city_sentence(table), table)]).splitlines()
    assert lines[0] == SENTENCE
    rows = [line for line in lines if line.startswith("|")][2:]
    assert len(rows) == 5
    # One decimal for bikes per day and the change, nulls as empty cells.
    assert rows[0] == "| 1000 | 2000 | 100.0 | 120.0 | 20.0 | grew |  |"
    assert rows[4] == "| 9000 | 1000 |  | 60.0 |  | not comparable | 2019: no data |"


def test_result_writes_skips_and_forces(tmp_path, capsys):
    table_all = place_change_table(pl.read_csv(FIXTURES / "place_year_small.csv"))
    table_dry = dry_place_change_table(pl.read_csv(FIXTURES / "place_year_dry_small.csv"), table_all)
    answer_path, answer_dry_path = tmp_path / "answer.parquet", tmp_path / "answer_dry.parquet"
    table_all.write_parquet(answer_path)
    table_dry.write_parquet(answer_dry_path)
    out_path = tmp_path / "derived" / "result.md"

    result(answer_path, answer_dry_path, out_path)
    out = capsys.readouterr().out.splitlines()
    assert len(out) == 1 and "wrote" in out[0]
    lines = out_path.read_text().splitlines()
    assert lines[0] == SENTENCE and DRY_SENTENCE in lines

    result(answer_path, answer_dry_path, out_path)
    out = capsys.readouterr().out.splitlines()
    assert len(out) == 1 and "skipped" in out[0]

    result(answer_path, answer_dry_path, out_path, force=True)
    out = capsys.readouterr().out.splitlines()
    assert len(out) == 1 and "wrote" in out[0]
