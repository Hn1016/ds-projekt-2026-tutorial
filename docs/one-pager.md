# One-pager: Is cycling in Zurich growing?

## Why

**The question as it arrived:** "Is cycling in Zurich growing?"
Nothing else came with it: no time span, no definition of cycling, no place.

**Who reads the result:** a planner in the city's transport planning who has to answer this in public, for example in a yearly report on the bike strategy. They will say yes or no, name where, and must be able to defend the answer when someone doubts the numbers.

## What

**What the reader gets:** a table, with one sentence above it.

- The sentence gives yes or no for the city, plus how many places grew, shrank or cannot be compared.
- The table has the average number of bikes per day and the change from 2019 to 2025.
- A chart is a view of the table, not the result.

**Unit of the result:** one row per place and year. Changed on 2026-10-08 from one row per counting site and year, because a place gets a new site ID every few years, so site IDs cannot be followed across years (see `docs/log.md`).

**Rules for the first answer:** decided on 2026-10-09, before any comparison was computed (see `docs/log.md`).

- Years: 2025, the last full year, against 2019, the last full year before the pandemic.
- Days: a day counts when it has any bike data. Known limit: a day with a partial outage counts as a full day and lowers the average.
- Comparable: a place counts in a year when it has bike data on at least 300 days of that year. A place is comparable when that holds in both years.
- Change: a place grew when its bikes per day rose by more than 5 percent, shrank when they fell by more than 5 percent, and is unchanged in between.
- Answer for the city: yes when more than half of the comparable places grew.
- Known limit: whether the 10 counting places stand for the whole city is untested (see `docs/log.md`, "Hypothesis · 2026-10-09 · Cycling grew at the comparable places").
- Known limit: the status of a place can depend on the pair of years. Measured on 2026-10-25 on the pairs 2018 to 2024, 2018 to 2025 and 2019 to 2024: 2 of the 8 places comparable in all four pairs, 2682375/1247055 and 2682933/1248821, grew only when the end year is 2025 and are unchanged with 2024 (see `docs/log.md`, "Hypothesis · 2026-10-25").

## How

**Source:** the open data portal of the city of Zurich, dataset "Daten der automatischen Fussgänger- und Velozählung, Viertelstundenwerte". The pipeline uses the single all-years file (`verkehrszaehlungen_werte_fussgaenger_velo_alle_jahre.parquet`) with counts per counter and quarter hour, not the yearly CSVs. Changed on 2026-10-08, because it is one download and the exploration already ran on it (see `docs/log.md`). The current date of the data is in `data/raw/manifest.csv`, which records when each file was downloaded, and in the line the load step prints when it writes `counts.parquet`, which gives the first and last day of the data.

**Loop one (all days):**
1. Download the all-years file.
2. Sum the quarter hours to bikes per place and day.
3. Count the days of a place that have any bike data.
4. Keep the places that can be compared across years.
5. Average per place and year, then compute the change from 2019 to 2025.

**First table:** one row per place and year, with the number of days that have data and the average number of bikes per day on those days. A place-year counts when it has bike data on at least 300 days.

**Loop two (dry weekdays):** repeat the comparison on dry weekdays only. This needs a second source, the city's daily weather data.

**Rules for loop two:** decided on 2026-10-14, before any comparison was computed (see `docs/log.md`).

- Weekday: Monday to Friday. Known limit: public holidays count as weekdays.
- Size of that limit, measured on 2026-10-16: without the canton's ten public holidays per year, one place (2681339/1248647) moves from unchanged to grew, and the answer for the city stays yes (see `docs/log.md`).
- Dry: a day with zero minutes of rain, parameter `RainDur` with daily values, at the station `Zch_Stampfenbachstrasse`. A weekday without a known `RainDur` value at that station is not dry. Known limit: one station stands for the whole city.
- Weather source: the city's daily weather data, one CSV per year at `https://data.stadt-zuerich.ch/dataset/ugz_meteodaten_tagesmittelwerte/download/ugz_ogd_meteo_d1_<year>.csv`.
- Places and years: the same 10 comparable places and the same years, 2019 and 2025, as the first answer. The 5 percent band and the majority rule stay.

## Non-goals

- A city-wide number of cyclists. The counters sit at chosen sites and say nothing about the streets between them.
- Causes. Whether a new bike lane or a policy changed anything is a different project.
- Forecasts.
- Pedestrians. They are in the same dataset and stay out.
- Correcting the counts to true bike numbers. The result compares a place with itself over time, so the counting error matters less as long as it stays the same.

## Done

- Every place and year has either a value or a stated reason why it cannot be compared. Nothing is dropped silently.
- The sentence for the city exists, with the counts of places that grew, shrank or cannot be compared.
- The unknowns are written into the result: counting error, sites that moved or were added, the years covered.
- Someone else can rebuild the table from nothing with one command and gets the same numbers from the same raw files.
- Loop one is done when all of this holds for all days. Loop two is done when the same table exists for dry weekdays and the two tables are compared.
- Checked on 2026-10-16: a fresh clone of `main`, `uv sync` and `uv run build` gave both sentences and both answer tables identical to my working copy, from a counts file one day newer. Known limit: on my machine, with the same Python and the same uv cache; the build has not run on another machine (see `docs/log.md`).
- Checked on 2026-10-25: the sentence for the city is yes for the three other pairs of years 2018 to 2024, 2018 to 2025 and 2019 to 2024, with 7 of 11, 8 of 10 and 6 of 10 comparable places grown (see `docs/log.md`, "Hypothesis · 2026-10-25").
