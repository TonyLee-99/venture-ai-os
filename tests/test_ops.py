"""F14: nightly entrypoint + CI workflow exist and are offline-safe."""

from vaios.config import ROOT


def test_ci_runs_make_check_offline():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
    assert "make check" in ci and "VAIOS_STRICT_REPLAY" in ci


def test_nightly_cron_runs_sourcing_from_cache():
    n = (ROOT / ".github" / "workflows" / "nightly.yml").read_text()
    assert "schedule:" in n and "cron:" in n and "make sourcing-run" in n and "VAIOS_STRICT_REPLAY" in n


def test_makefile_targets():
    mk = (ROOT / "Makefile").read_text()
    for t in ("check:", "verify:", "reproduce:", "sourcing-run:", "replay:", "init:"):
        assert t in mk
    assert (ROOT / "Dockerfile").exists() and (ROOT / "uv.lock").exists()
