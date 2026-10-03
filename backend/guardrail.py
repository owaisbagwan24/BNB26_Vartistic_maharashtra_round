"""Re:Learn Cognitive Firewall: Socratic Guardrail & Adversarial Leak Filter.

Enforces zero-solution-leakage policy:
1. Intercepts adversarial prompt injections (jailbreaks, "ignore previous instructions").
2. Strips complete code blocks, multiline code, or copy-paste answers.
3. Enforces strict length limits (<50 words) to avoid cognitive offloading.
4. Guarantees Socratic posture: guides with analogies, questions, and mental models.
"""
import re
from typing import Tuple, Dict, Any

ADVERSARIAL_INJECTION_PATTERNS = [
    r"ignore (all )?(previous|above) instructions",
    r"system (prompt|override)",
    r"just (give|print|tell|write) (me )?(the )?(code|answer|solution)",
    r"what is the (exact )?(code|fix|solution)",
    r"solve (this|it) for me",
    r"i don't care (about )?why",
    r"do my homework",
    r"output (only|just) python code"
]

CODE_BLOCK_REGEX = re.compile(r"```(?:python)?[\s\S]*?```", re.IGNORECASE)
INLINE_CODE_REGEX = re.compile(r"`[^`\n]{15,}`")
ASSIGNMENT_OR_DEF_REGEX = re.compile(r"^\s*(def |class |for |while |if |[a-zA-Z_]\w*\s*=).*", re.MULTILINE)

SOCRATIC_FALLBACK_REDIRECTS = {
    "M-01": "In Re:Learn, we build understanding together! Think about '=' as an action command, and '==' as an inquisitive question. How does that help line 2?",
    "M-02": "I'm your learning partner, not a copy-paste generator! Where does Python's range start counting by default?",
    "M-03": "I don't hand out direct answers, but I will give you the mental model: does 'b = a' build a new house, or make a second key to the same front door?",
    "M-05": "Let's figure it out together! What happens when you try to mathematically add text symbols to a numerical quantity?",
    "M-08": "No spoilers here! When a function 'prints', the words appear on screen. But does that automatically hand a package back to whoever called it?",
    "M-09": "You've got the concept! Take a close look at your punctuation on that line."
}

def sanitize_and_guard_response(response_text: str, misconception_id: str = "M-01") -> Tuple[str, bool]:
    """Inspects candidate LLM or engine response.

    Returns:
        (sanitized_text, was_flagged)
    """
    cleaned = response_text.strip()
    was_flagged = False

    # 1. Block markdown code blocks
    if CODE_BLOCK_REGEX.search(cleaned):
        cleaned = CODE_BLOCK_REGEX.sub("", cleaned).strip()
        was_flagged = True

    # 2. Block long inline code leaks
    if INLINE_CODE_REGEX.search(cleaned):
        cleaned = INLINE_CODE_REGEX.sub("[concept]", cleaned)
        was_flagged = True

    # 3. Block raw code syntax line leaks
    lines = cleaned.splitlines()
    safe_lines = []
    for l in lines:
        if ASSIGNMENT_OR_DEF_REGEX.match(l) and not any(k in l for k in ["Think", "Imagine", "Notice", "Why", "Does"]):
            was_flagged = True
            continue
        safe_lines.append(l)
    cleaned = "\n".join(safe_lines).strip()

    # 4. If empty or severely stripped, substitute Socratic analogy
    if not cleaned or len(cleaned) < 10 or was_flagged:
        fallback = SOCRATIC_FALLBACK_REDIRECTS.get(misconception_id, SOCRATIC_FALLBACK_REDIRECTS["M-01"])
        return fallback, True

    # 5. Enforce word count limit (<50 words)
    words = cleaned.split()
    if len(words) > 50:
        cleaned = " ".join(words[:48]) + "... What do you think happens next?"

    return cleaned, False

def check_adversarial_prompt(user_message: str) -> bool:
    """Detects if student input contains an adversarial injection or demand for direct solutions."""
    lowered = user_message.lower().strip()
    for pat in ADVERSARIAL_INJECTION_PATTERNS:
        if re.search(pat, lowered):
            return True
    return False
