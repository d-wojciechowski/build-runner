import pytest

from src.config import AppConfig
from src.constants import Target
from src.executor import Executor, ExecutionStatus, TaskBuilder
from src.module import ModulesConfig


def build_args(kwargs: dict) -> dict:
    return {
        "build": kwargs.get("build", None),
        "test_unit": kwargs.get("test_unit", None),
        "test_integration": kwargs.get("test_integration", None),
        "suite": kwargs.get("suite", None),
        "custom": kwargs.get("custom", None),
        "restart": kwargs.get("restart", False),
    }


def test_should_not_execute_test_unit_when_invalid_alias(
    app_config: AppConfig, modules_config: ModulesConfig
):
    app_config.fail_on_error = False

    with pytest.raises(Exception) as exc_info:
        TaskBuilder(app_config, modules_config).build_tasks(
            arguments=build_args({"test_unit": ["x_Custom.class"]})
        )

    assert exc_info.value.__class__.__name__ == "ExecutorException"
    assert exc_info.value.message == "Module alias x not found"


def test_should_not_execute_test_unit_when_command_failed(
    app_config: AppConfig, modules_config: ModulesConfig
):
    app_config.fail_on_error = True

    with pytest.raises(Exception) as exc_info:
        tasks = TaskBuilder(app_config, modules_config).build_tasks(
            build_args({"test_unit": ["a_Custom.class"]})
        )
        Executor(app_config, modules_config).run_tasks(tasks)

    assert exc_info.value.__class__.__name__ == "ExecutorException"
    assert (
        exc_info.value.message
        == "Command ant test.unit -f not/here1/src_test/build.xml -Dtest.includes=**/Custom.class failed with code 1"
    )


def test_should_execute_test_unit_commands_based_on_arguments(
    app_config: AppConfig, modules_config: ModulesConfig
):
    app_config.fail_on_error = False

    tasks = TaskBuilder(app_config, modules_config).build_tasks(
        build_args({"test_unit": ["a_Custom.class"]})
    )
    Executor(app_config, modules_config).run_tasks(tasks)

    assert len(tasks) == 1
    assert tasks[0].module.name == "nameA"
    assert tasks[0].target == Target.TEST_UNIT
    assert tasks[0].targets == "Custom.class"

    assert len(tasks[0].commands) == 1
    assert (
        tasks[0].commands[0].command
        == "ant test.unit -f not/here1/src_test/build.xml -Dtest.includes=**/Custom.class"
    )
    assert tasks[0].commands[0].status == ExecutionStatus.FAILED


def test_should_execute_test_integ_commands_based_on_arguments(
    app_config: AppConfig, modules_config: ModulesConfig
):
    app_config.fail_on_error = False

    tasks = TaskBuilder(app_config, modules_config).build_tasks(
        build_args({"test_integration": ["a_Custom.class"]})
    )
    Executor(app_config, modules_config).run_tasks(tasks)

    assert len(tasks) == 1
    assert tasks[0].module.name == "nameA"
    assert tasks[0].target == Target.TEST_INTEGRATION
    assert tasks[0].targets == "Custom.class"

    assert len(tasks[0].commands) == 1
    assert (
        tasks[0].commands[0].command
        == "ant test.integration -f not/here1/src_test/build.xml -Dtest.includes=**/Custom.class"
    )
    assert tasks[0].commands[0].status == ExecutionStatus.FAILED


def test_should_execute_build_commands_based_on_arguments(
    app_config: AppConfig, modules_config: ModulesConfig
):
    app_config.fail_on_error = False

    tasks = TaskBuilder(app_config, modules_config).build_tasks(
        build_args({"build": ["a_cstw"], "restart": True})
    )
    Executor(app_config, modules_config).run_tasks(tasks)

    assert len(tasks) == 2
    assert tasks[0].module.name == "nameA"
    assert tasks[0].target == Target.BUILD
    assert tasks[0].targets == "cstw"

    assert len(tasks[0].commands) == 5
    assert tasks[0].commands[0].command == "ant clobber -f not/here1/src/build.xml"
    assert tasks[0].commands[0].status == ExecutionStatus.FAILED
    assert tasks[0].commands[1].command == "ant -f not/here1/src/build.xml"
    assert tasks[0].commands[1].status == ExecutionStatus.FAILED
    assert tasks[0].commands[2].command == "ant clobber -f not/here1/src_test/build.xml"
    assert tasks[0].commands[2].status == ExecutionStatus.FAILED
    assert tasks[0].commands[3].command == "ant -f not/here1/src_test/build.xml"
    assert tasks[0].commands[3].status == ExecutionStatus.FAILED
    assert tasks[0].commands[4].command == "ant -f not/here1/src_web/build.xml"
    assert tasks[0].commands[4].status == ExecutionStatus.FAILED

    assert tasks[1].module is None
    assert tasks[1].target == Target.RESTART
    assert tasks[1].targets is None
    assert len(tasks[1].commands) == 1
    assert tasks[1].commands[0].command == "echo Restarting"
    assert tasks[1].commands[0].status == ExecutionStatus.COMPLETED


def test_should_execute_build_commands_based_on_arguments_not_using_alias(
    app_config: AppConfig, modules_config: ModulesConfig
):
    app_config.fail_on_error = False

    tasks = TaskBuilder(app_config, modules_config).build_tasks(
        build_args({"build": ["nameC_s"], "restart": True})
    )
    Executor(app_config, modules_config).run_tasks(tasks)

    assert len(tasks) == 2
    assert tasks[0].module.name == "nameC"
    assert tasks[0].target == Target.BUILD
    assert tasks[0].targets == "s"

    assert len(tasks[0].commands) == 1
    assert tasks[0].commands[0].command == "ant -f not/here3/src/build.xml"
    assert tasks[0].commands[0].status == ExecutionStatus.FAILED

    assert tasks[1].module is None
    assert tasks[1].target == Target.RESTART
    assert tasks[1].targets is None
    assert len(tasks[1].commands) == 1
    assert tasks[1].commands[0].command == "echo Restarting"
    assert tasks[1].commands[0].status == ExecutionStatus.COMPLETED


def test_should_execute_suite_commands_based_on_arguments(
    app_config: AppConfig, modules_config: ModulesConfig
):
    app_config.fail_on_error = False
    app_config.suites = {
        "1": {"restart": True, "build": {"nameA": "cstw", "nameB": "s"}, "custom": []}
    }

    tasks = TaskBuilder(app_config, modules_config).build_tasks(
        build_args({"suite": ["1"]})
    )
    Executor(app_config, modules_config).run_tasks(tasks)

    assert len(tasks) == 3
    assert tasks[0].module.name == "nameA"
    assert tasks[0].target == Target.BUILD
    assert tasks[0].targets == "cstw"

    assert len(tasks[0].commands) == 5
    assert tasks[0].commands[0].command == "ant clobber -f not/here1/src/build.xml"
    assert tasks[0].commands[0].status == ExecutionStatus.FAILED
    assert tasks[0].commands[1].command == "ant -f not/here1/src/build.xml"
    assert tasks[0].commands[1].status == ExecutionStatus.FAILED
    assert tasks[0].commands[2].command == "ant clobber -f not/here1/src_test/build.xml"
    assert tasks[0].commands[2].status == ExecutionStatus.FAILED
    assert tasks[0].commands[3].command == "ant -f not/here1/src_test/build.xml"
    assert tasks[0].commands[3].status == ExecutionStatus.FAILED
    assert tasks[0].commands[4].command == "ant -f not/here1/src_web/build.xml"
    assert tasks[0].commands[4].status == ExecutionStatus.FAILED

    assert len(tasks) == 3
    assert tasks[0].module.name == "nameA"
    assert tasks[0].target == Target.BUILD
    assert tasks[0].targets == "cstw"

    assert len(tasks[1].commands) == 1
    assert tasks[1].commands[0].command == "ant -f not/here2/src/build.xml"
    assert tasks[1].commands[0].status == ExecutionStatus.FAILED

    assert tasks[2].module is None
    assert tasks[2].target == Target.RESTART
    assert tasks[2].targets is None
    assert len(tasks[2].commands) == 1
    assert tasks[2].commands[0].command == "echo Restarting"
    assert tasks[2].commands[0].status == ExecutionStatus.COMPLETED


def test_should_execute_custom_command_as_specified(
    app_config: AppConfig, modules_config: ModulesConfig
):
    app_config.fail_on_error = False
    app_config.commands.custom = {"full": "echo Full", "half": "echo Half"}

    tasks = TaskBuilder(app_config, modules_config).build_tasks(
        build_args({"custom": ["full", "half"]})
    )
    Executor(app_config, modules_config).run_tasks(tasks)

    assert len(tasks) == 2
    assert tasks[0].module is None
    assert tasks[0].target == Target.CUSTOM
    assert tasks[0].targets == "full"

    assert len(tasks[0].commands) == 1
    assert tasks[0].commands[0].command == "echo Full"
    assert tasks[0].commands[0].status == ExecutionStatus.COMPLETED

    assert len(tasks[1].commands) == 1
    assert tasks[1].commands[0].command == "echo Half"
    assert tasks[1].commands[0].status == ExecutionStatus.COMPLETED


def test_should_not_execute_custom_command_when_command_not_defined(
    app_config: AppConfig, modules_config: ModulesConfig
):
    app_config.fail_on_error = False
    app_config.commands.custom = {}

    tasks = TaskBuilder(app_config, modules_config).build_tasks(
        build_args({"custom": ["full"]})
    )
    Executor(app_config, modules_config).run_tasks(tasks)

    assert len(tasks) == 1
    assert tasks[0].module is None
    assert tasks[0].target == Target.CUSTOM
    assert tasks[0].targets == "full"

    assert len(tasks[0].commands) == 1
    assert tasks[0].commands[0].command == "full"
    assert tasks[0].commands[0].status == ExecutionStatus.FAILED


def test_should_execute_custom_suite_command_when_command_defined(
    app_config: AppConfig, modules_config: ModulesConfig
):
    app_config.fail_on_error = False
    app_config.commands.custom = {"full": "echo Full", "half": "echo Half"}
    app_config.suites = {"1": {"restart": True, "custom": ["full"]}}

    tasks = TaskBuilder(app_config, modules_config).build_tasks(
        build_args({"suite": ["1"]})
    )
    Executor(app_config, modules_config).run_tasks(tasks)

    assert len(tasks) == 2
    assert tasks[0].module is None
    assert tasks[0].target == Target.CUSTOM
    assert tasks[0].targets == "full"

    assert len(tasks[0].commands) == 1
    assert tasks[0].commands[0].command == "echo Full"
    assert tasks[0].commands[0].status == ExecutionStatus.COMPLETED

    assert tasks[1].module is None
    assert tasks[1].target == Target.RESTART
    assert tasks[1].targets == None

    assert len(tasks[1].commands) == 1
    assert tasks[1].commands[0].command == "echo Restarting"
    assert tasks[1].commands[0].status == ExecutionStatus.COMPLETED


def test_should_not_execute_custom_suite_command_when_command_not_defined(
    app_config: AppConfig, modules_config: ModulesConfig
):
    app_config.fail_on_error = True
    app_config.commands.custom = {}
    app_config.suites = {"1": {"restart": True, "custom": ["full"]}}

    with pytest.raises(Exception) as exc_info:
        TaskBuilder(app_config, modules_config).build_tasks(
            build_args({"suite": ["1"]})
        )

    assert exc_info.value.__class__.__name__ == "ExecutorException"
    assert exc_info.value.message == 'Command "full" not found in custom commands'
