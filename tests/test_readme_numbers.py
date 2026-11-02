"""F17: every headline number string appears verbatim in README.md (README cannot drift from results/)."""

from vaios.config import ROOT
from vaios.report import headline_numbers


def test_readme_contains_every_headline_number():
    readme = (ROOT / "README.md").read_text()
    missing = {k: v for k, v in headline_numbers().items() if v not in readme}
    assert not missing, missing
