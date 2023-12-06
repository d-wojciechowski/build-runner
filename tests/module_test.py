from src.module import ModulesConfigBuilder, ModuleInfo


def test_should_create_module_config_correctly_when_test(app_config):
    config = ModulesConfigBuilder(app_config).build()

    assert len(config.modules) == 2

    assert config.modules["nameA"].order == 1
    assert config.modules["nameB"].order == 2

    assert config.modules["nameA"].location == f"{app_config.root}/not/here1"
    assert config.modules["nameB"].location == f"{app_config.root}/not/here2"

    assert config.modules["nameA"].srcs == ["src", "src_test", "src_web"]
    assert config.modules["nameB"].srcs == ["src", "src_test", "src_web"]


def test_should_create_module_config_correctly_when_prod(app_config):
    app_config.profile = "prod"

    config = ModulesConfigBuilder(app_config).build()

    assert len(config.modules) == 2

    assert config.modules["nameA"].order == 1
    assert config.modules["nameB"].order == 2

    assert config.modules["nameA"].location == f"{app_config.root}/not/here1"
    assert config.modules["nameB"].location == f"{app_config.root}/not/here2"

    assert config.modules["nameA"].srcs == ["src", "src_test", "src_web"]
    assert config.modules["nameB"].srcs == ["src"]


def test_should_not_raise_exception_when_file_not_found(app_config):
    app_config.profile = "prod"
    app_config.root = "./not/here"

    config = ModulesConfigBuilder(app_config).build()

    assert len(config.modules) == 2

    assert config.modules["nameA"].order == 1
    assert config.modules["nameB"].order == 2

    assert config.modules["nameA"].location == f"{app_config.root}/not/here1"
    assert config.modules["nameB"].location == f"{app_config.root}/not/here2"

    assert config.modules["nameA"].srcs == []
    assert config.modules["nameB"].srcs == []


def test_should_correctly_convert_module_info_to_dict():
    module_info = ModuleInfo(
        name="name", location="location", order=1, srcs=["src1", "src2"]
    )
    assert module_info.to_dict() == {
        "name": "name",
        "location": "location",
        "order": 1,
        "srcs": ["src1", "src2"],
    }


def test_should_correctly_convert_module_info_to_str():
    module_info = ModuleInfo(
        name="name", location="location", order=1, srcs=["src1", "src2"]
    )
    assert (
        str(module_info)
        == "ModuleInfo(name=name, location=location, order=1, srcs=['src1', 'src2'])"
    )


def test_should_correctly_convert_module_info_to_repr():
    module_info = ModuleInfo(
        name="name", location="location", order=1, srcs=["src1", "src2"]
    )
    assert repr(module_info) == "ModuleInfo(name=name)"
