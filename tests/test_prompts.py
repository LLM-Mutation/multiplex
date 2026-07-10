import pytest

from multiplex.prompts import APPROACH_PROMPT_KEYS, resolve_prompts


def _full_config():
    """A config defining every approach's prompts."""
    system_prompts = {}
    for keys in APPROACH_PROMPT_KEYS.values():
        for key in keys:
            system_prompts[key] = f"prompt for {key}"
    return {"system_prompts": system_prompts}


@pytest.mark.parametrize("approach", list(APPROACH_PROMPT_KEYS))
def test_resolve_returns_only_required_subset(approach):
    result = resolve_prompts(_full_config(), approach)
    assert set(result) == set(APPROACH_PROMPT_KEYS[approach])


def test_resolve_succeeds_with_only_selected_approach_keys():
    # Core of the issue: prompts for other approaches may be absent.
    config = {"system_prompts": {"basic_generate_mutants": "do it"}}
    assert resolve_prompts(config, "basic") == {"basic_generate_mutants": "do it"}


def test_resolve_missing_required_key_raises_naming_it():
    with pytest.raises(SystemExit) as exc:
        resolve_prompts({"system_prompts": {}}, "stpa")
    assert "stpa_describe_control_flow" in str(exc.value)


def test_resolve_empty_required_key_raises():
    with pytest.raises(SystemExit):
        resolve_prompts({"system_prompts": {"basic_generate_mutants": ""}}, "basic")


def test_resolve_unknown_approach_raises():
    with pytest.raises(SystemExit) as exc:
        resolve_prompts(_full_config(), "nope")
    assert "Invalid approach" in str(exc.value)


def test_resolve_missing_system_prompts_section_raises():
    with pytest.raises(SystemExit):
        resolve_prompts({}, "basic")
