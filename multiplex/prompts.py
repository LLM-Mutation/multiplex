"""Check prompts for the selected mutation approach."""

APPROACH_PROMPT_KEYS = {
    "basic": ["basic_generate_mutants"],
    "hazop": [
        "hazop_describe_process",
        "hazop_identify_deviations",
        "hazop_implement_deviations",
    ],
    "stpa": [
        "stpa_describe_control_flow",
        "stpa_identify_ucas",
        "stpa_implement_ucas",
    ],
    "mutahunter": ["mutahunter_generate_mutants"],
    "llmorpheus": ["llmorpheus_system"],
}


def resolve_prompts(config, approach):
    """Return the system prompts required by ``approach``."""
    if approach not in APPROACH_PROMPT_KEYS:
        valid = ", ".join(sorted(APPROACH_PROMPT_KEYS))
        raise SystemExit(f"Invalid approach '{approach}'. Choose one of: {valid}")

    system_prompts = config.get("system_prompts") or {}
    required = APPROACH_PROMPT_KEYS[approach]
    missing = [key for key in required if not system_prompts.get(key)]
    if missing:
        raise SystemExit(
            f"Approach '{approach}' requires these system_prompts keys: "
            f"{', '.join(missing)}"
        )

    return {key: system_prompts[key] for key in required}
