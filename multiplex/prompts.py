"""Resolve and validate system prompts for the selected mutation approach."""

# Each approach uses only its own system prompts. Only the selected approach's
# keys are required for a run; unrelated keys may be omitted from the config.
# Adding an approach means adding its required prompt keys here.
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
    """Return the system prompts required by ``approach``.

    Only the keys the selected approach actually uses are read, so a config need
    not define prompts for approaches it will not run. Raises ``SystemExit`` with
    an actionable message if the approach is unknown or any required
    ``system_prompts`` key is missing or empty.
    """
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
