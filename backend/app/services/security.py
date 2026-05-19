import re


class PromptSecurityService:
    _patterns: dict[str, re.Pattern[str]] = {
        "ignore_previous_instructions": re.compile(
            r"\b(ignore|forget|discard)\b.*\b(previous|prior|above)\b.*\binstructions?\b",
            re.I | re.S,
        ),
        "system_prompt_extraction": re.compile(
            r"\b(system prompt|developer message|hidden instructions|initial instructions)\b",
            re.I,
        ),
        "jailbreak_attempt": re.compile(
            r"\b(jailbreak|DAN mode|do anything now|bypass safety|override policy)\b",
            re.I,
        ),
        "data_exfiltration": re.compile(r"\b(api key|secrets?|credentials?|tokens?|private key)\b", re.I),
        "role_manipulation": re.compile(
            r"\bact as\b.*\b(unrestricted|uncensored|no rules|root|admin)\b",
            re.I | re.S,
        ),
    }

    def analyze(self, prompt: str) -> list[str]:
        return [name for name, pattern in self._patterns.items() if pattern.search(prompt)]
