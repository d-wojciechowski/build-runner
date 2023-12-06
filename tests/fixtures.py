import pytest

from src.config import *
from src.module import ModulesConfig, ModuleInfo

BUILD_ORDER = """
a/nameA
#b/nameB
***************
"""

MODULES = """
<ModuleRegistry>
      <Module location="not/here2" name="b/nameB" description="DummyModule2"></Module>
      <Module location="not/here1" name="a/nameA" description="DummyModule1"></Module>
</ModuleRegistry>
"""


@pytest.fixture
def modules_config() -> ModulesConfig:
    modules = {
        "nameA": ModuleInfo(
            name="nameA",
            location="not/here1",
            order=1,
            srcs=["src", "src_test", "src_web"],
        ),
        "nameB": ModuleInfo(
            name="nameB",
            location="not/here2",
            order=2,
            srcs=["src", "src_test", "src_web"],
        ),
        "nameC": ModuleInfo(
            name="nameC",
            location="not/here3",
            order=3,
            srcs=["src", "src_test", "src_web"],
        ),
    }
    return ModulesConfig(modules)


@pytest.fixture
def data_folder(tmpdir) -> str:
    data_dir = tmpdir.mkdir("data")

    bo_file = data_dir.join("build_order.txt")
    bo_file.write(BUILD_ORDER)

    mod_file = data_dir.join("modules.xml")
    mod_file.write(MODULES)
    return data_dir.strpath


@pytest.fixture
def srcs_folder(tmpdir) -> str:
    srcs_dir = tmpdir.mkdir("srcs")
    dir_not = srcs_dir.mkdir("not")

    dir_here_1 = dir_not.mkdir("here1")
    dir_here_1.mkdir("src")
    dir_here_1.mkdir("src_test")
    dir_here_1.mkdir("src_web")
    dir_here_1.mkdir("not_not")

    dir_here_2 = dir_not.mkdir("here2")
    dir_here_2.mkdir("src")
    dir_here_2.mkdir("not_not")

    return srcs_dir.strpath


@pytest.fixture
def app_config(data_folder: str, srcs_folder: str) -> AppConfig:
    aliases = {
        "a": "nameA",
        "b": "nameB",
    }
    ootb_commands = OOTBCommands(restart="echo " + "Restarting")
    commands = Commands(ootb=ootb_commands, custom={})
    input_cfg = Input(
        build_order=data_folder + "/" + "build_order.txt",
        module_registry=data_folder + "/" + "modules.xml",
    )
    return AppConfig(
        profile="test",
        root=srcs_folder,
        fail_on_error=True,
        commands=commands,
        input=input_cfg,
        aliases=aliases,
        suites={},
    )
