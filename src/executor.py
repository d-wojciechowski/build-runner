import subprocess
from enum import Enum

import src.constants as const
from src.config import AppConfig
from src.constants import Target
from src.module import ModuleInfo, ModulesConfig


class ExecutorException(Exception):
    def __init__(self, message):
        self.message = message


class ExecutionStatus(str, Enum):
    PREPARED = "PREPARED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Command:
    def __init__(
        self, command: str, status: ExecutionStatus = ExecutionStatus.PREPARED
    ):
        self.command = command
        self.status = status

    def __repr__(self):
        return f"Command(command={self.command}, status={self.status})"


class Task:
    def __init__(self, target: Target, module: ModuleInfo = None, targets: str = None):
        self.commands = []
        self.target = target
        self.module = module
        self.targets = targets

    def __repr__(self):
        return (
            f"Task(target={self.target}, module={self.module}, targets={self.targets})"
        )


class TaskBuilder:
    def __init__(self, app_cfg: AppConfig, config: ModulesConfig):
        self.app_cfg = app_cfg
        self.config = config

    def build_tasks(self, arguments: dict) -> list:
        if arguments[Target.SUITE] is not None:
            return self.__build_suite_tasks(arguments)
        else:
            return self.__build_explicit_tasks(arguments)

    def __build_explicit_tasks(self, arguments: dict) -> list:
        tasks = []
        for target in Target.module_dependent():
            if arguments[target]:
                for module_spec in arguments[target]:
                    module, targets = self.__get_task_spec(module_spec)
                    tasks.append(self.build_single_task(target, module, targets))
        for target in Target.module_agnostic():
            if arguments[target]:
                for task in arguments[target]:
                    tasks.append(self.build_single_task(target, None, task))
        if arguments[Target.RESTART]:
            tasks.append(self.build_single_task(Target.RESTART))
        return tasks

    def build_single_task(
        self, target: Target = None, module: ModuleInfo = None, targets: str = None
    ) -> Task:
        task = Task(target, module, targets)
        task.commands = self.create_commands(task)
        return task

    def __build_suite_tasks(self, arguments: dict) -> list:
        tasks = []
        suite_name = arguments[Target.SUITE][0]
        suite = self.app_cfg.suites[suite_name]
        for module, targets in suite.get("build", {}).items():
            tasks.append(
                self.build_single_task(
                    Target.BUILD, self.config.modules[module], targets
                )
            )
        for command in suite.get("custom", []):
            tasks.append(self.build_single_task(Target.CUSTOM, None, command))
        if suite["restart"]:
            tasks.append(self.build_single_task(Target.RESTART))
        return tasks

    def __get_task_spec(self, module_spec: str) -> tuple:
        spec = module_spec.split("_")
        module_alias = spec[0]
        targets = spec[1]
        module = self.__get_module_by_alias(module_alias)
        return module, targets

    def __get_module_by_alias(self, module_alias: str) -> ModuleInfo:
        module_name = self.app_cfg.aliases.get(module_alias)
        if module_name is None:
            module_by_direct_call = self.config.modules.get(module_alias)
            if module_by_direct_call is not None:
                return module_by_direct_call
            else:
                raise ExecutorException(f"Module alias {module_alias} not found")
        else:
            return self.config.modules[module_name]

    def create_commands(self, task: Task) -> list:
        commands = []
        if task.target == Target.BUILD:
            commands.extend(TaskBuilder.__build_commands(task.module, task.targets))
        elif task.target in [Target.TEST_UNIT, Target.TEST_INTEGRATION]:
            commands.append(
                TaskBuilder.__test_commands(task.target, task.module, task.targets)
            )
        elif task.target == Target.RESTART:
            commands.append(Command(self.app_cfg.commands.ootb.restart))
        elif task.target == Target.CUSTOM:
            command = self.app_cfg.commands.custom.get(task.targets)
            if command is not None:
                commands.append(Command(command))
            elif command is None:
                if self.app_cfg.fail_on_error:
                    raise ExecutorException(
                        f'Command "{task.targets}" not found in custom commands'
                    )
                else:
                    commands.append(Command(task.targets, ExecutionStatus.FAILED))

        return commands

    @staticmethod
    def __build_commands(module: ModuleInfo, targets: str) -> list:
        commands = []
        if "s" in targets:
            if "c" in targets:
                commands.append(
                    Command(
                        "ant clobber -f %s/%s/build.xml"
                        % (module.location, const.SRC_ALIASES["s"])
                    )
                )
            commands.append(
                Command(
                    "ant -f %s/%s/build.xml" % (module.location, const.SRC_ALIASES["s"])
                )
            )
        if "t" in targets:
            if "c" in targets:
                commands.append(
                    Command(
                        "ant clobber -f %s/%s/build.xml"
                        % (module.location, const.SRC_ALIASES["t"])
                    )
                )
            commands.append(
                Command(
                    "ant -f %s/%s/build.xml" % (module.location, const.SRC_ALIASES["t"])
                )
            )
        if "w" in targets:
            commands.append(
                Command(
                    "ant -f %s/%s/build.xml" % (module.location, const.SRC_ALIASES["w"])
                )
            )
        return commands

    @staticmethod
    def __test_commands(test_type: Target, module: ModuleInfo, targets: str) -> Command:
        test_cmd = "ant %s -f %s/%s/build.xml" % (
            test_type.replace("_", "."),
            module.location,
            const.SRC_ALIASES["t"],
        )
        if targets:
            test_cmd = test_cmd + " -Dtest.includes=**/%s" % targets
        return Command(test_cmd)


class Executor:
    def __init__(self, app_cfg: AppConfig, config: ModulesConfig):
        self.tasks = []
        self.app_cfg = app_cfg
        self.config = config

    def run_tasks(self, tasks: list):
        for task in tasks:
            self.run_commands(task)

    def run_commands(self, task):
        for command in task.commands:
            self.run_command(command)

    def run_command(self, command):
        self.__print_header(command.command)
        if command.status is not ExecutionStatus.PREPARED:
            return
        command.status = ExecutionStatus.RUNNING
        completed_process = subprocess.run(command.command, shell=True)
        if completed_process.returncode != 0:
            command.status = ExecutionStatus.FAILED
            print(
                f"Command {command.command} failed with code {completed_process.returncode}"
            )
            if self.app_cfg.fail_on_error:
                raise ExecutorException(
                    f"Command {command.command} failed with code {completed_process.returncode}"
                )
        else:
            command.status = ExecutionStatus.COMPLETED
            print(f"Command {command.command} completed successfully")
        self.__print_footer()

    @staticmethod
    def __print_header(command):
        print("-" * const.COMMAND_SIZE)
        message = f"Executing command {command}"
        dash_count = int(((const.COMMAND_SIZE - len(message)) / 2) - 1)
        print("-" * dash_count + " " + message + " " + "-" * dash_count)
        print("-" * const.COMMAND_SIZE)

    @staticmethod
    def __print_footer():
        # print("-" * const.COMMAND_SIZE)
        pass
