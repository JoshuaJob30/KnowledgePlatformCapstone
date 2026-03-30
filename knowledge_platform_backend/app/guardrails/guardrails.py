import yaml, re, logging

logger = logging.getLogger(__name__)

def load_policies(path="app/guardrails/policies.yaml"):
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"[Guardrails] Failed to load policies: {e}")
        return {"blocklist": [], "patterns": []}

policies = load_policies()

def guardrail_check(question: str) -> bool:
    """
    Return True if the query should be blocked by safety policy.
    """
    q = question.lower()

    # Check blocklist words
    for word in policies.get("blocklist", []):
        if word in q:
            logger.warning(f"[Guardrails] Blocked by word: {word}")
            return True

    # Check regex patterns
    for pattern in policies.get("patterns", []):
        if re.search(pattern, q):
            logger.warning(f"[Guardrails] Blocked by pattern: {pattern}")
            return True

    return False
