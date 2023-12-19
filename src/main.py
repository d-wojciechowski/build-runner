import argparse
import os
import sys
import traceback
from pathlib import Path

import yaml

import constants as const
from example_cfg import CFG_FILE_CONTENT
from executor import Executor, TaskBuilder
from module import ModulesConfigBuilder
from src.config import AppConfig


def main():
    app_cfg = init_app_cfg()
    arguments = parse_args()

    config = ModulesConfigBuilder(app_cfg).build()

    tasks = TaskBuilder(app_cfg, config).build_tasks(arguments)
    Executor(app_cfg, config).run_tasks(tasks)

    print("-" * const.COMMAND_SIZE + "\n")
    print("Application finished successfully\n")
    for task in tasks:
        for command in task.commands:
            print(f"{command.status} in {command.time:.2f}s - {command.command}")


def init_app_cfg() -> AppConfig:
    app_cfg_dir = "%s/.wc_builder" % str(Path.home())
    cfg_path = "%s/cfg.yml" % app_cfg_dir

    try:
        stream = open(cfg_path)
    except OSError:
        print("Config does not exists : " + cfg_path)
        os.makedirs(app_cfg_dir, exist_ok=True)
        print("Created config directory : " + app_cfg_dir)
        with open(cfg_path, "a") as stream:
            stream.write(CFG_FILE_CONTENT)
        stream = open(cfg_path)

    app_cfg = yaml.safe_load(stream)
    return AppConfig(**app_cfg)


def parse_args() -> dict:
    parser = argparse.ArgumentParser(
        description="Windchill modules builder",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="Example: %s -b mpml_cbt mpmlc_cb -r" % sys.argv[0],
    )
    parser.add_argument(
        "-b", "--build", nargs="+", help="Execute build in order from CFG"
    )
    parser.add_argument(
        "-u", "--test-unit", nargs="+", help="Execute unit tests in order from CFG"
    )
    parser.add_argument(
        "-i",
        "--test-integration",
        nargs="+",
        help="Execute integration tests in order from CFG",
    )
    parser.add_argument(
        "-s", "--suite", nargs="+", help="Execute a set of tasks defined in CFG"
    )
    parser.add_argument(
        "-c", "--custom", nargs="+", help="Execute a custom command defined in CFG"
    )
    parser.add_argument(
        "-r",
        "--restart",
        action="store_true",
        help="Restarts MethodServer (configure cmd in CFG)",
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    return vars(args)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Application finished with error")
        print(e)
        traceback.print_exc()
        sys.exit(1)
