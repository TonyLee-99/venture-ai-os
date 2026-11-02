"""F06: features as of T0 ignore every row timestamped at or after T0 (poisoned-future-rows test)."""

import pandas as pd
from sql_fixture import T0, build

FEATURES_SQL = "SELECT * EXCLUDE (t0) FROM features_pit ORDER BY slug"


def test_universe_is_only_protocols_listed_before_t0():
    con = build()
    assert sorted(r[0] for r in con.execute("SELECT slug FROM features_pit").fetchall()) == ["alpha", "beta"]


def test_known_feature_values():
    f = build().execute(FEATURES_SQL).df().set_index("slug")
    assert f.loc["alpha", "commits_90d"] == 30 and f.loc["alpha", "prior_raises"] == 1
    assert f.loc["alpha", "tvl_t0"] == 400.0           # last TVL strictly before T0
    assert f.loc["beta", "prior_raises"] == 0           # beta's raise is after T0
    assert f.loc["beta", "listing_age_days"] == 17


def test_poisoned_future_rows_change_nothing():
    clean = build().execute(FEATURES_SQL).df()
    future = T0 + pd.Timedelta(days=1)
    poison = {
        "stg_tvl_daily": pd.DataFrame([("alpha", T0, 9e9), ("beta", future, 9e9)], columns=["slug", "day", "tvl_usd"]),
        "stg_raises": pd.DataFrame([{"slug": "alpha", "raise_date": T0, "round": "A", "amount_musd": 50.0,
                                     "lead_investors": "X", "other_investors": "", "source": ""}]),
        "stg_gh_repos": pd.DataFrame([{"owner": "alpha-org", "repo": "new", "repo_created_at": future, "stars_now": 99999}]),
        # GitHub windows computed for a different as-of date must not leak into this T0
        "stg_gh_windows": pd.DataFrame([{"owner": "alpha-org", "repo": "a", "as_of": future,
                                         "repo_created_at": pd.Timestamp("2023-01-01"), "stars_now": 10, "forks_now": 1,
                                         "archived": False, "commits_before": 9999, "commits_90d": 9999,
                                         "commits_prev90d": 9999}]),
    }
    dirty = build(poison).execute(FEATURES_SQL).df()
    pd.testing.assert_frame_equal(clean, dirty)


def test_labels_see_the_future_but_features_do_not():
    con = build()
    lab = con.execute("SELECT slug, raised, amount_musd FROM labels_pit ORDER BY slug").fetchall()
    assert lab == [("alpha", False, 0.0), ("beta", True, 3.0)]
