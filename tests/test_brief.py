"""The weekly brief's shipped inflection claims all pass the receipts verifier offline."""

import json

import pytest

from vaios.config import RESULTS
from vaios.dakr.docstore import DocStore
from vaios.receipts.verify import check_claim

BRIEFS = sorted((RESULTS / "briefs").glob("20*.json"))


@pytest.mark.skipif(not BRIEFS, reason="no brief yet")
def test_brief_claims_verify_and_unexplained_are_flagged():
    out = json.loads(BRIEFS[-1].read_text())
    store = DocStore()
    assert out["brief"]["inflections"]
    for n in out["brief"]["inflections"]:
        for c in n["claims"]:
            assert check_claim(c, store, out["facts"]).ok, (n["series"], c["id"])
        if not n["claims"]:
            assert n["needs_human"]


def test_brief_exists():
    assert BRIEFS, "run `make brief`"
