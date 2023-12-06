from enum import Enum


class Target(str, Enum):
    BUILD = "build"
    TEST_UNIT = "test_unit"
    TEST_INTEGRATION = "test_integration"
    SUITE = "suite"
    RESTART = "restart"
    CUSTOM = "custom"

    @staticmethod
    def module_dependent():
        return [Target.BUILD, Target.TEST_UNIT, Target.TEST_INTEGRATION, Target.SUITE]

    @staticmethod
    def module_agnostic():
        return [Target.CUSTOM]


COMMAND_SIZE = 128

SRC = "src"
SRC_TEST = "src_test"
SRC_WEB = "src_web"

SRC_ALIASES = {"s": SRC, "t": SRC_TEST, "w": SRC_WEB}
