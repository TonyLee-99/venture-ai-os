# 0008. "Investable" means eligible for a $1-2M pre-seed/seed check, from sourced evidence only

Status: accepted (2026-11-02).

The first version called anything not an incumbent and not a personal account "investable", which let a
Stripe/Paradigm-incubated L1 rank first. Now the top 40 relevant candidates are stage-checked using only data
the system fetches and stores as snapshots: funding sentences and investor-logo alt text on the company's own
homepage and /about page (domain from the GitHub profile's website field; one curated domain, checked by hand:
gokite-ai -> gokite.ai), DefiLlama raises, the YC directory, CoinGecko FDV. Rules: a stated Series A+, a seed
of $5M+, incubation by an incumbent, tier-1 institutional backers already on the homepage, or a liquid token
with FDV > $100M => past the fund's entry stage. Everything else is "unknown", never assumed to be early.

Limits: absence of evidence is not evidence of being early; homepage logos can be partners rather than
investors (Kite's logos include ecosystem partners next to PayPal Ventures and General Catalyst); the tier-1
list is a judgment call written in `stage.py`.
