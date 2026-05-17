import hashlib

_ADJECTIVES = [
    "Quiet", "Brave", "Calm", "Gentle", "Swift", "Bright", "Silent", "Warm",
    "Clear", "Bold", "Soft", "Steady", "Free", "Kind", "Wise", "Still",
    "Open", "True", "Light", "Strong", "Safe", "Deep", "Keen", "Pure",
    "Fair", "Glad", "Firm", "Lean", "Neat", "Rich", "Sharp", "Vast",
]

_NOUNS = [
    "Oak", "River", "Stone", "Ember", "Cloud", "Tide", "Cedar", "Dusk",
    "Willow", "Crest", "Haven", "Bloom", "Shore", "Ash", "Brook", "Fern",
    "Hollow", "Pine", "Ridge", "Sage", "Vale", "Birch", "Cliff", "Glen",
    "Heath", "Mist", "Path", "Reed", "Rift", "Rowan", "Spire", "Trail",
]


def generate_pseudonym(user_id: str) -> str:
    digest = hashlib.sha256(user_id.encode()).hexdigest()
    adj_idx = int(digest[:8], 16) % len(_ADJECTIVES)
    noun_idx = int(digest[8:16], 16) % len(_NOUNS)
    suffix = int(digest[16:20], 16) % 1000
    return f"{_ADJECTIVES[adj_idx]}{_NOUNS[noun_idx]}_{suffix:03d}"
