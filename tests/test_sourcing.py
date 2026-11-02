"""F05: sourcing draws on >= 4 independent sources, resolves entities across them, and dedupes vs the CRM."""

import json

import numpy as np
import pandas as pd

from vaios.agents import sourcing
from vaios.config import RESULTS


def test_resolution_merges_on_shared_keys_and_not_on_missing_ones():
    m = pd.DataFrame([
        {"source": "github_search", "name": "daydreamsai", "github_owner": "daydreamsai", "domain": "daydreams.systems"},
        {"source": "x402scan", "name": "daydreams", "github_owner": np.nan, "domain": ""},          # name key
        {"source": "yc_directory", "name": "Other Co", "github_owner": np.nan, "domain": "daydreams.systems"},  # domain
        {"source": "defillama", "name": "Unrelated", "github_owner": np.nan, "domain": ""},          # NaN must not link
        {"source": "hn", "name": "Lonely", "github_owner": np.nan, "domain": "github.com"},          # shared host ignored
    ])
    r = sourcing.resolve(m)
    assert r["entity_idx"].nunique() == 3
    assert r.loc[0, "entity_idx"] == r.loc[1, "entity_idx"] == r.loc[2, "entity_idx"]


def test_incumbents_and_relevance():
    assert sourcing.is_incumbent(["nvidia-ai-blueprints"], "nvidia-ai-blueprints")
    assert not sourcing.is_incumbent(["faremeter"], "faremeter")
    assert sourcing.relevance("x402 payments for AI agents with USDC") >= 4
    assert sourcing.relevance("a todo app") == 0


def test_committed_candidates():
    c = pd.read_csv(RESULTS / "sourcing" / "candidates.csv")
    s = json.loads((RESULTS / "sourcing" / "shortlist.json").read_text())
    sources = {x for v in c["sources"] for x in v.split(",")}
    assert len(sources) >= 4 and (c["n_sources"] > 1).sum() >= 10
    in_crm = set(c.loc[c["crm_stage"].notna(), "entity"])
    assert in_crm, "the SYNTHETIC CRM should match at least one candidate (dedupe demo)"
    short = {r["entity"] for r in s["shortlist"]}
    assert short and not (short & in_crm)
    sub = c[c["entity"].isin(short)]
    assert sub["investable"].all() and (sub["relevance"] >= sourcing.CORE_RELEVANCE).all()
