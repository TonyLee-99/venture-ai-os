"""Comparable companies monitored by the post-investment job (public comparables, NOT Decasonic's portfolio).

Each entry links an x402scan facilitator id (on-chain traction) and/or GitHub repos (build velocity).
Chosen 2026-11-02 as the largest public x402 facilitators and agent-payment SDKs by GitHub footprint.
"""

MONITORED_REPOS = [
    "x402-foundation/x402",
    "coinbase/agentkit",
    "google-agentic-commerce/AP2",
    "daydreamsai/daydreams",
    "stripe/agent-toolkit",
    "cloudflare/agents",
    "Merit-Systems/x402scan",
    "thirdweb-dev/js",
    "crossmint/crossmint-sdk",
    "nevermined-io/payments",
]
