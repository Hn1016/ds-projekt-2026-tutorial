from pathlib import Path

import polars as pl

from ds_projekt_2026_tutorial.answer import city_sentence
from ds_projekt_2026_tutorial.answer_dry import OPENING


def markdown_table(table: pl.DataFrame) -> str:
    """The table in Markdown: one decimal for bikes per day and the change, nulls as empty cells.

    The rounding is for the reader only; the table itself stays as it is.
    """

    def cell(name: str, value) -> str:
        if value is None:
            return ""
        if name.startswith("bikes_per_day") or name == "change_percent":
            return f"{value:.1f}"
        return str(value)

    lines = ["| " + " | ".join(table.columns) + " |", "|" + "---|" * table.width]
    for row in table.iter_rows():
        lines.append("| " + " | ".join(cell(n, v) for n, v in zip(table.columns, row)) + " |")
    return "\n".join(lines)


def result_markdown(sections: list[tuple[str, pl.DataFrame]]) -> str:
    """Each sentence followed by its table, in Markdown."""
    return "\n\n".join(f"{sentence}\n\n{markdown_table(table)}" for sentence, table in sections) + "\n"


def result(answer_path: Path, answer_dry_path: Path, out_path: Path, force: bool = False) -> Path:
    """Write the two sentences for the city, each followed by its table, to out_path, unless it is already there."""
    if out_path.exists() and not force:
        print(f"result: skipped, {out_path} already exists.")
        return out_path

    table_all = pl.read_parquet(answer_path)
    table_dry = pl.read_parquet(answer_dry_path)
    text = result_markdown([(city_sentence(table_all), table_all), (city_sentence(table_dry, OPENING), table_dry)])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Write to a .part file first so an interrupted run never looks complete.
    part = out_path.with_name(out_path.name + ".part")
    part.write_text(text)
    part.replace(out_path)

    print(f"result: wrote {out_path}.")
    return out_path
