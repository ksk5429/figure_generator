"""Smoke + visual regression tests.

Visual regression uses pytest-mpl. To generate baseline images on a new
figure:

    pytest --mpl-generate-path=tests/baseline_images tests/test_figures.py

After inspection, commit the baseline PNGs. CI runs `pytest --mpl` which
compares generated figures against the committed baselines.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from figgen import utils, validate
from figgen.domain import frf, scour


@pytest.fixture
def synthetic_scour_df() -> pd.DataFrame:
    r = np.linspace(-20.0, 20.0, 101)
    z = 4.0 * np.exp(-((r / 6.0) ** 2))
    return pd.DataFrame({"r_m": r, "z_m": z})


def test_load_journal_all_exist():
    for journal in ("isfog", "geotechnique", "ocean_engineering", "marine_structures", "thesis", "poster"):
        spec = utils.load_journal(journal)
        assert spec.widths_in
        assert spec.formats


def test_validation_catches_missing_column(synthetic_scour_df):
    with pytest.raises(validate.ValidationError):
        validate.validate_dataframe(
            synthetic_scour_df,
            required=["r_m", "z_m", "does_not_exist"],
            require_units=False,
            context="test",
        )


def test_validation_requires_units_when_requested(synthetic_scour_df):
    # Synthetic frame uses _m suffixes, so units should be inferable.
    report = validate.validate_dataframe(
        synthetic_scour_df,
        required=["r_m", "z_m"],
        require_units=True,
        context="test",
    )
    assert report.ok


def test_validation_rejects_missing_units():
    df = pd.DataFrame({"radius": [1, 2, 3], "scour": [0.1, 0.5, 1.2]})
    with pytest.raises(validate.ValidationError):
        validate.validate_dataframe(
            df,
            required=["radius", "scour"],
            require_units=True,
            context="test",
        )


@pytest.mark.mpl_image_compare(baseline_dir="baseline_images", filename="scour_profile.png")
def test_scour_profile_renders(synthetic_scour_df):
    fig, _ = scour.plot_profile(synthetic_scour_df, journal="thesis")
    return fig


@pytest.mark.mpl_image_compare(baseline_dir="baseline_images", filename="frf_mag.png")
def test_frf_plot_renders():
    f = np.logspace(-1, 2, 500)
    mag = 1 / np.sqrt((1 - (f / 3.0) ** 2) ** 2 + (0.05 * f / 3.0) ** 2)
    fig, _ = frf.plot(f, mag, modal_peaks=[3.0], journal="thesis")
    return fig
