import os
import re
import xml.etree.ElementTree as Et

import src.constants as const
from src.config import AppConfig


class ModuleInfo:
    def __init__(self, **kwargs):
        self.name = kwargs["name"]
        self.location = kwargs["location"]
        self.order = kwargs.get("order")
        self.srcs = kwargs.get("srcs", [])

    def to_dict(self):
        return {
            "name": self.name,
            "location": self.location,
            "order": self.order,
            "srcs": self.srcs,
        }

    def __str__(self) -> str:
        return f"ModuleInfo(name={self.name}, location={self.location}, order={self.order}, srcs={self.srcs})"

    def __repr__(self) -> str:
        return f"ModuleInfo(name={self.name})"


class ModulesConfig:
    def __init__(self, modules: dict):
        self.modules: dict = modules


class ModulesConfigBuilder:
    order_pattern = re.compile("^#? ?(\\w+)/(\\w+)\n?")

    def __init__(self, app_cfg: AppConfig):
        self.app_cfg = app_cfg

    def build(self) -> ModulesConfig:
        modules = self.__create_modules_by_registry()
        self.__set_build_order(modules)
        self.__set_srcs(modules)
        return modules

    def __set_build_order(self, modules: ModulesConfig):
        idx = 0
        order_path = self.app_cfg.input.build_order
        with open(order_path) as f:
            for line_number, line in enumerate(f, 1):
                if self.order_pattern.fullmatch(line):
                    sanitized_string = line.replace("#", "").strip().split("/")[1]
                    idx += 1
                    module = modules.modules.get(sanitized_string)
                    if module is not None:
                        module.order = idx

    def __create_modules_by_registry(self) -> ModulesConfig:
        module_registry_path = self.app_cfg.input.module_registry
        tree = Et.parse(module_registry_path)
        root = tree.getroot()
        modules = root.findall(".//Module")
        result = {}
        for module in modules:
            abs_location = "%s/%s" % (self.app_cfg.root, module.attrib["location"])
            result[module.attrib["name"].split("/")[1]] = ModuleInfo(
                name=module.attrib["name"], location=abs_location
            )
        return ModulesConfig(result)

    def __set_srcs(self, modules: ModulesConfig):
        if self.app_cfg.profile == "test":
            for name, module in modules.modules.items():
                module.srcs = list(const.SRC_ALIASES.values())
        else:
            for name, module in modules.modules.items():
                try:
                    module.srcs = [
                        f.name
                        for f in os.scandir(module.location)
                        if f.is_dir() and "src" in f.name
                    ]
                except FileNotFoundError:
                    pass
        pass
