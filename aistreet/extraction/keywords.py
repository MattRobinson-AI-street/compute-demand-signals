"""Keyword patterns and rules for signal extraction."""

# Demand indicators - capacity tight/constrained
DEMAND_UP_KEYWORDS = {
    "strong demand",
    "driven by strong demand",
    "driven by demand",
    "robust demand",
    "exceptional demand",
    "record demand",
    "increased demand",
    "increasing demand",
    "growing demand",
    "demand growth",
    "demand continues",
    "demand remained strong",
    "demand increased",
    "higher demand",
    "shortage",
    "shortages",
    "supply constrained",
    "supply constraints",
    "capacity constrained",
    "capacity constraints",
    "constrained by",
    "limited availability",
    "tight supply",
    "remains constrained",
    "supply remained tight",
    "sold out",
    "backlog",
    "wait times",
    "lead times increased",
    "expanding capacity",
    "capacity expansion",
    "adding capacity",
    "building capacity",
    "increased capacity",
}

# Demand slack indicators - capacity loose/declining
DEMAND_DOWN_KEYWORDS = {
    "declining demand",
    "decreased demand",
    "lower demand",
    "weakening demand",
    "softening demand",
    "demand declined",
    "demand decreased",
    "excess capacity",
    "spare capacity",
    "underutilized",
    "abundant supply",
    "ample supply",
    "oversupply",
    "readily available",
    "slack capacity",
    "unused capacity",
    "idle capacity",
    "reducing capacity",
    "capacity reduction",
}

# Demand stable indicators
DEMAND_FLAT_KEYWORDS = {
    "stable demand",
    "steady demand",
    "consistent demand",
    "demand remained stable",
    "demand was stable",
    "maintained capacity",
    "maintaining capacity",
}

# Compute-related terms (signal relevance)
COMPUTE_KEYWORDS = {
    "gpu",
    "gpus",
    "ai infrastructure",
    "ai compute",
    "compute capacity",
    "data center",
    "datacenter",
    "training",
    "inference",
    "nvidia",
    "cuda",
    "tensor",
    "h100",
    "a100",
    "cloud infrastructure",
    "hyperscale",
    "ai chips",
    "accelerators",
    "server capacity",
    "colocation",
}

# AI-specific indicators (vs general infrastructure)
AI_SPECIFIC_KEYWORDS = {
    "ai",
    "artificial intelligence",
    "machine learning",
    "ml",
    "gpu",
    "gpus",
    "ai infrastructure",
    "ai compute",
    "ai services",
    "ai workload",
    "ai training",
    "ai inference",
    "ai chips",
    "nvidia",
    "cuda",
    "tensor",
    "h100",
    "a100",
    "accelerator",
    "accelerators",
    "llm",
    "large language model",
    "generative ai",
    "gen ai",
    "deep learning",
}

# Segment indicators
TRAINING_KEYWORDS = {
    "training",
    "model training",
    "ai training",
    "training infrastructure",
    "training workload",
}

INFERENCE_KEYWORDS = {
    "inference",
    "model inference",
    "ai inference",
    "inference infrastructure",
    "inference workload",
    "serving",
}

# Constraint indicators
POWER_KEYWORDS = {
    "power",
    "electricity",
    "energy",
    "power capacity",
    "power constraint",
    "power availability",
    "electrical",
}

CHIP_KEYWORDS = {
    "chip",
    "chips",
    "gpu",
    "gpus",
    "processor",
    "semiconductor",
    "supply constraint",
    "allocation",
}

NETWORKING_KEYWORDS = {
    "network",
    "networking",
    "bandwidth",
    "interconnect",
    "infiniband",
    "ethernet",
}

CAPACITY_KEYWORDS = {
    "capacity",
    "space",
    "facility",
    "footprint",
    "real estate",
    "availability",
}

# Pricing indicators
PRICING_UP_KEYWORDS = {
    "price increase",
    "higher price",
    "pricing pressure",
    "rate increase",
    "cost increase",
}

PRICING_DOWN_KEYWORDS = {
    "price decrease",
    "lower price",
    "price reduction",
    "cost reduction",
    "pricing decline",
}

PRICING_STABLE_KEYWORDS = {
    "stable pricing",
    "consistent pricing",
    "unchanged pricing",
}

# Time horizon indicators
NOW_KEYWORDS = {
    "current",
    "currently",
    "present",
    "this quarter",
}

NEXT_QTR_KEYWORDS = {
    "next quarter",
    "upcoming quarter",
    "q1",
    "q2",
    "q3",
    "q4",
}

SIX_TO_TWELVE_KEYWORDS = {
    "next year",
    "2025",
    "2026",
    "six months",
    "nine months",
}

TWELVE_PLUS_KEYWORDS = {
    "long term",
    "long-term",
    "multi-year",
    "future",
    "2027",
    "2028",
}


def contains_any(text_lower: str, keywords: set[str]) -> bool:
    """Check if text contains any of the keywords."""
    return any(kw in text_lower for kw in keywords)
