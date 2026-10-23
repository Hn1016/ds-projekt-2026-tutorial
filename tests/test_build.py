import sys
from pathlib import Path

import pytest

from ds_projekt_2026_tutorial import build

DERIVED_STEPS = ["days", "load", "derive", "answer", "answer_dry", "result"]


def run_build(monkeypatch, *options):
    """Run build.main with stand-ins for the steps; return the force each step got, per call."""
    calls = []

    def stand_in(name):
        def step(*args, force=False):
            calls.append((name, force))
            return Path(name)

        return step

    for name in ["download", *DERIVED_STEPS]:
        monkeypatch.setattr(build, name, stand_in(name))
    monkeypatch.setattr(sys, "argv", ["build", *options])
    build.main()
    return calls


@pytest.mark.parametrize(
    "options, download_force, derived_force",
    [
        ((), False, False),
        (("--force",), False, True),
        (("--force-download",), True, True),
    ],
)
def test_force_options(monkeypatch, options, download_force, derived_force):
    calls = run_build(monkeypatch, *options)
    assert [force for name, force in calls if name == "download"] == [download_force] * 3
    assert [name for name, _ in calls if name != "download"] == DERIVED_STEPS
    assert all(force == derived_force for name, force in calls if name != "download")
