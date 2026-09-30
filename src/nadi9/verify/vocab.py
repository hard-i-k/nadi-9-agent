from typing import Any, List, Set
from ..memory.claims import SubtitleDecision
from ..evidence.registry import EvidenceRegistry

def extract_nadi9_tokens(text: str) -> List[str]:
    """Extract individual tokens from Nadi-9 text, stripping punctuation."""
    import re
    tokens = re.findall(r'[\w\-]+', text.lower())
    return tokens

def get_known_vocabulary(registry: EvidenceRegistry) -> Set[str]:
    """Build set of all known Nadi-9 words from evidence."""
    known = set()
    for item in registry.get_all_active():
        import re
        # Extract nadi9 words from content patterns like "nadi9: word" or "| nadi9: word"
        matches = re.findall(r'nadi9:\s*([\w\-]+)', item.content.lower())
        known.update(matches)
        # Also extract from translation pairs
        if '=' in item.content:
            parts = item.content.split('=')
            if len(parts) >= 2:
                nadi_part = parts[-1].strip().lower()
                known.update(re.findall(r'[\w\-]+', nadi_part))
    return known

def check_vocab(decision: SubtitleDecision, registry: EvidenceRegistry) -> tuple[bool, List[str]]:
    """Check every token in nadi_9_text against known vocabulary.
    Returns (all_supported, list_of_unsupported_tokens)."""
    if not decision.nadi_9_text or decision.nadi_9_text == "INSUFFICIENT_EVIDENCE":
        return True, []
    
    known = get_known_vocabulary(registry)
    tokens = extract_nadi9_tokens(decision.nadi_9_text)
    unsupported = []
    
    for token in tokens:
        # Skip numbers, single chars, common punctuation artifacts
        if token.isdigit() or len(token) <= 1:
            continue
        # Check if token or any of its morphological parts are known
        found = False
        if token in known:
            found = True
        else:
            # Check if it's a known root with an affix
            for k in known:
                if token.startswith(k) or token.endswith(k):
                    found = True
                    break
        if not found:
            unsupported.append(token)
    
    return len(unsupported) == 0, unsupported