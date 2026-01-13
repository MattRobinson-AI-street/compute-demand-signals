"""Keyword patterns and rules for signal extraction."""

# Demand direction indicators
DEMAND_UP_KEYWORDS = {
    "increased demand",
    "growing demand",
    "strong demand",
    "higher demand",
    "demand growth",
    "increased capacity",
    "expanding capacity",
    "capacity expansion",
    "accelerat",
    "ramp",
    "scaling",
    "significant increase",
    "robust demand",
    "surge",
}

DEMAND_DOWN_KEYWORDS = {
    "decreased demand",
    "declining demand",
    "lower demand",
    "reduced demand",
    "weakening demand",
    "softening demand",
    "demand slowdown",
    "decreased capacity",
    "capacity reduction",
    "slowdown",
    "decelerat",
}

DEMAND_FLAT_KEYWORDS = {
    "stable demand",
    "steady demand",
    "consistent demand",
    "unchanged demand",
    "flat demand",
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
    "accelerat",
    "nvidia",
    "cuda",
    "tensor",
    "h100",
    "a100",
    "cloud infrastructure",
    "hyperscale",
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
