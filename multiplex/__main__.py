import argparse
import os
import shutil
from pathlib import Path

import approach.basic.controller as basic
import approach.hazop.controller as hazop
import approach.llmorpheus.controller as llmorpheus
import approach.mutahunter.controller as mutahunter
import approach.stpa.controller as stpa
import yaml
from execute import defects4j, maven
from model import Model
from prompts import resolve_prompts
from util.extract_method import extract_method_from_file
from util.io import reset_source_code


def main():
    s = """

# # # # # # # # # # # # # # # # # # # # # # # # 
#                  _ _   _       _            #
#  _ __ ___  _   _| | |_(_)_ __ | | _____  __ #
# | '_ ` _ \| | | | | __| | '_ \| |/ _ \ \/ / #
# | | | | | | |_| | | |_| | |_) | |  __/>  <  #
# |_| |_| |_|\__,_|_|\__|_| .__/|_|\___/_/\_\ #
#                         |_|                 #
#                                             #
#     A Modular LLM-based Mutation Tool       #
#                                             #
# # # # # # # # # # # # # # # # # # # # # # # #                                                    


    """

    print(s)
    parser = argparse.ArgumentParser(description="multiplex")
    parser.add_argument("config", help="Path to config file")

    args = parser.parse_args()

    config = yaml.safe_load(open(args.config))

    output_path = Path(config["project"]["projectroot"], "output/")
    duplicate_file_path = Path(config["project"]["filename"] + ".orig")

    approach = config["mutation"]["approach"]
    prompts = resolve_prompts(config, approach)

    print(f"File: {config['project']['filename']}")
    print(f"Method: {config['project']['method']}")

    if output_path.exists():
        response = input(
            f"Output dir ({output_path}) already exists. Would you like to delete it and continue? (y/n): "
        )

        if response == "y":
            shutil.rmtree(output_path)
            os.makedirs(output_path, exist_ok=True)
        else:
            raise SystemExit()

    else:
        os.makedirs(output_path, exist_ok=True)

    reset_source_code(duplicate_file_path, config["project"]["filename"])

    method_span = extract_method_from_file(
        config["project"]["filename"],
        config["project"]["method"],
        output_path,
        config["project"]["line"],
    )
    if method_span is None:
        raise SystemExit(
            f"Method '{config['project']['method']}' not found at line {config['project']['line']} "
            f"in {config['project']['filename']}. Check project.method and project.line "
            f"(line must be the line of the method-name identifier)."
        )
    method_start_byte, method_end_byte = method_span

    model = Model(
        model=config["llm"]["model"],
        endpoint=config["llm"]["endpoint"],
        api_key_var=config["llm"]["token_env_var"],
    )

    if approach == "stpa":
        stpa.main(model, output_path, prompts)
    elif approach == "hazop":
        hazop.main(model, output_path, prompts)
    elif approach == "basic":
        basic.main(model, output_path, prompts)
    elif approach == "mutahunter":
        mutahunter.main(model, output_path, prompts)
    elif approach == "llmorpheus":
        llmorpheus.main(model, output_path, prompts)

    if config["project"]["runtool"] == "mvn":
        maven.run_mutants(
            config["project"]["projectroot"],
            config["project"]["filename"],
            output_path,
            method_start_byte,
            method_end_byte,
            duplicate_file_path,
            config["mutation"]["approach"],
        )
    elif config["project"]["runtool"] == "d4j":
        defects4j.run_mutants(
            config["project"]["projectroot"],
            config["project"]["filename"],
            output_path,
            method_start_byte,
            method_end_byte,
            duplicate_file_path,
            config["mutation"]["approach"],
        )

    reset_source_code(duplicate_file_path, config["project"]["filename"])


if __name__ == "__main__":
    main()
