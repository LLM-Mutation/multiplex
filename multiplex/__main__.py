import argparse
import os
import shutil
import yaml
from pathlib import Path

import approach.basic.controller as basic
import approach.mutahunter.controller as mutahunter
import approach.stpa.controller as stpa
import approach.hazop.controller as hazop
import approach.llmorpheus.controller as llmorpheus
from execute import maven, defects4j

from model import Model
from util.io import reset_source_code
from util.extract_method import extract_method_from_file


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

    output_path = Path(config['project']['projectroot'], 'output/')
    duplicate_file_path = Path(config['project']['filename'] + ".orig")
    prompts = {
        "hazop_describe_process" : config['system_prompts']['hazop_describe_process'],
        "hazop_identify_deviations" : config['system_prompts']['hazop_identify_deviations'],
        "hazop_implement_deviations" : config['system_prompts']['hazop_implement_deviations'],
        "stpa_describe_control_flow" : config['system_prompts']['stpa_describe_control_flow'],
        "stpa_identify_ucas" : config['system_prompts']['stpa_identify_ucas'],
        "stpa_implement_ucas" : config['system_prompts']['stpa_implement_ucas'],
        "basic_generate_mutants" : config['system_prompts']['basic_generate_mutants'],
        "mutahunter_generate_mutants" : config['system_prompts']['mutahunter_generate_mutants'],
        "llmorpheus_system" : config['system_prompts']['llmorpheus_system']
    }

    print(f"File: {config['project']['filename']}")
    print(f"Method: {config['project']['method']}")

    if output_path.exists():
        # response = input(f"Output dir ({output_path}) already exists. Would you like to delete it and continue? (y/n)")
        response = "y"

        if response == "y":
            shutil.rmtree(output_path)
            os.makedirs(output_path, exist_ok=True)
        else:
            raise SystemExit()

    else:
        os.makedirs(output_path, exist_ok=True)

    reset_source_code(duplicate_file_path, config['project']['filename'])

    method_start_byte, method_end_byte = extract_method_from_file(
        config['project']['filename'], config['project']['method'], output_path, config['project']['line']
    )

    model = Model(model=config['llm']['model'], endpoint=config['llm']['endpoint'],
                  api_key_var=config['llm']['token_env_var'])

    if config['mutation']['approach'] == "stpa":
        stpa.main(model, output_path, prompts)
    elif config['mutation']['approach'] == "hazop":
        hazop.main(model, output_path, prompts)
    elif config['mutation']['approach'] == "basic":
        basic.main(model, output_path, prompts)
    elif config['mutation']['approach'] == "mutahunter":
        mutahunter.main(model, output_path, prompts)
    elif config['mutation']['approach'] == "llmorpheus":
        llmorpheus.main(model, output_path, prompts)
    else:
        print("Invalid approach")

    if config['project']['runtool'] == "mvn":
        maven.run_mutants(
            config['project']['projectroot'],
            config['project']['filename'],
            output_path,
            method_start_byte,
            method_end_byte,
            duplicate_file_path,
            config['mutation']['approach'],
        )
    elif config['project']['runtool'] == "d4j":
        defects4j.run_mutants(config['project']['projectroot'], config['project']['filename'], output_path,
                              method_start_byte, method_end_byte, duplicate_file_path, config['mutation']['approach'])

    reset_source_code(duplicate_file_path, config['project']['filename'])


if __name__ == "__main__":
    main()
