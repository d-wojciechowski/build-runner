import os
import re
import time
import xml.etree.ElementTree as Et
import pandas as pd
import yaml


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
            "srcs": self.srcs
        }


class ModulesConfig:
    order_pattern = re.compile("^#? ?(\\w+)/(\\w+)\n?")

    def __init__(self, app_cfg: dict):
        self.modules: dict
        self.__init_modules_registry(app_cfg)
        self.__init_build_order(app_cfg)
        self.__init_srcs(app_cfg)

    def __init_build_order(self, app_cfg: dict):
        idx = 0
        order_path = app_cfg["app"]["input"]["build_order"]
        with open(order_path) as f:
            for line_number, line in enumerate(f, 1):
                if self.order_pattern.fullmatch(line):
                    sanitized_string = line.removeprefix("#").strip()
                    idx += 1
                    module = self.modules.get(sanitized_string)
                    if module is not None:
                        module.order = idx

    def __init_modules_registry(self, app_cfg: dict):
        module_registry_path = app_cfg["app"]["input"]["module_registry"]
        tree = Et.parse(module_registry_path)
        root = tree.getroot()
        modules = root.findall(".//Module")
        result = {}
        for module in modules:
            result[module.attrib["name"]] = ModuleInfo(name=module.attrib["name"], location=module.attrib["location"])
        self.modules = result

    def __init_srcs(self, app_cfg: dict):
        root = app_cfg["app"]["root"]
        if app_cfg["app"]["profile"] == "test":
            for name, module in self.modules.items():
                module.srcs = ["src_test", "src_web", "src"]
        else:
            for name, module in self.modules.items():
                module.srcs = [f.name for f in os.scandir(root + "/" + module.location) if
                               f.is_dir() and "src" in f.name]
        pass


def build_config_excel(app_cfg: dict, config: ModulesConfig):
    df = pd.DataFrame.from_records([m.to_dict() for m in config.modules.values()])
    df["src"] = df["srcs"].apply(lambda x: "src" in x)
    df["src_test"] = df["srcs"].apply(lambda x: "src_test" in x)
    df["src_web"] = df["srcs"].apply(lambda x: "src_web" in x)

    start = time.time()
    # df.to_excel(app_cfg["app"]["input"]["run_data"])
    print((time.time() - start) * 1000)
    pass

def main():
    start = time.time()
    app_cfg = yaml.safe_load(open("config/cfg.yml"))

    config = ModulesConfig(app_cfg)
    # build_config_excel(app_cfg, config)
    print((time.time() - start) * 1000)


if __name__ == '__main__':
    main()
