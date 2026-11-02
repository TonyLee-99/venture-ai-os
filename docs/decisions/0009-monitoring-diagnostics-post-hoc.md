# 0009. Monitoring diagnostics added after the pre-specified test missed (exploratory)

Status: accepted (2026-11-02).

The ADR 0005 test stays the headline (hit rate 42% vs 36% chance, p = 0.44). Everything in
`results/monitoring/diagnostics.json` was added afterwards and is labelled exploratory:
- power of the pre-specified test (how many of 12 events must be hit for p < 0.05);
- expanding-window replay of PELT (detection delay in weeks; alarms that later disappear);
- PELT vs the z-score detector at the same number of alarms; an event-leads window (3 days before to 14 after);
- event list v2 = v1 + the first DEX pool of every CoinGecko "x402 Ecosystem" token (GeckoTerminal dates),
  to test the crypto-catalyst explanation of the October 2025 surge without hand-picking events;
- an artifact check on the September 2026 drop (daily shape, facilitator shares, public x402scan commits).
Because the event list was extended after seeing the miss, a better v2 hit rate would be a hypothesis for the
next quarter's data, not a validated result.
