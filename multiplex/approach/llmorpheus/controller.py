"""Controller for llmorpheus prompt approach."""

from pathlib import Path
from typing import Any
from approach.llmorpheus.placeholders import create_placeholders
from approach.llmorpheus.code_generator import generate_code
from model import Model


def main(model: Model, output_dir: Path, prompts: dict[str, Any]):
    """Controller for LLMorpheus prompt approach"""

    create_placeholders(output_dir)
    generate_code(model, output_dir, prompts['llmorpheus_system'])
    

def __main__(model: Model, output_dir: Path, prompts: dict[str, Any]):
    main(model, output_dir, prompts)
