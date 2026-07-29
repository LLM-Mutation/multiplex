"""Controller for llmorpheus prompt approach."""

from pathlib import Path
from typing import Any
from approach.llmorpheus.placeholders import create_placeholders
from approach.llmorpheus.code_generator import generate_code
from model import Model


def main(model: Model, output_dir: Path, prompts: dict[str, Any], language):
    """Controller for LLMorpheus prompt approach"""

    create_placeholders(output_dir, language)
    generate_code(model, output_dir, prompts['llmorpheus_system'], language)


def __main__(model: Model, output_dir: Path, prompts: dict[str, Any], language):
    main(model, output_dir, prompts, language)
