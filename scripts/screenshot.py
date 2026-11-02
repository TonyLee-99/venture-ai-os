"""Headless screenshot of dashboard/index.html into docs/img/ (Playwright, Chromium)."""

from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1250, "height": 900}, device_scale_factor=2)
    errors = []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.goto((ROOT / "dashboard" / "index.html").as_uri())
    out = ROOT / "docs" / "img"
    out.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(out / "dashboard.png"), full_page=True)
    page.screenshot(path=str(out / "dashboard_top.png"), clip={"x": 0, "y": 0, "width": 1250, "height": 760})
    browser.close()
    assert not errors, errors
    print("screenshots -> docs/img/dashboard.png, docs/img/dashboard_top.png")
