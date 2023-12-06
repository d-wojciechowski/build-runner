<p align="center">
  <img src="./.github/app_logo.png" />
</p>

The program is used to simplify build process of ant projects across multiple modules.

## Decisions made

* The program is written in Python 3.6 due to target machine limitations
* Executable file should be compiled with centos:7.7.1908 due to target machine limitations

## Flags
* -b: build project. Sytax: [module_name/module_alias]_[s][w][t][c]
    * s: build src files
    * w: build src_web files
    * t: build src_test files
    * c: clobber all. If csw specified, then clobber would be executed for src and src_web
    * Multiple arguments to flag may be specified ex: -b mpml_swt ass_swt
* -u: execute unit tests. Syntax [module_name/module_alias]_[ClassName]
    * ClassName is optional, if not specified, all unit tests will be executed
    * Multiple arguments to flag may be specified ex: -u mpml ass_UnitTest.class
* -i: execute integration tests. Syntax [module_name/module_alias]_[ClassName]
    * ClassName is optional, if not specified, all integration tests will be executed
    * Multiple arguments to flag may be specified ex: -i mpml ass_UnitTest.class
* -s: execute suite of preconfigured build steps in ~/.wc_builder/cfg.yml
    * One argument to flag may be specified ex: -s submission1
* -c: execute custom command specified in ~/.wc_builder/cfg.yml. Syntax -c [command_alias]
    * Multiple arguments to flag may be specified ex: -c cmd1 cmd2
* -r: execute restart command specified in ~/.wc_builder/cfg.yml. It is just a shortcut.
    * No args accepted for this
* -h : printout help with example usage

## CFG file

The config file is in YML format. It is main configuration file.

* profile: test/prod. On day-to-day basis prod should be used.
* root: root folder for all modules of project
* fail_on_error: Should fail on execution errors.
* commands/ootb: aliases should not be modified. Commands may be modified.
* commands/custom: aliases may be modified/added. Commands may be modified. Source of truth for -c option.
* input/build_order: path to compile.includes file.
* input/module_registry: path to moduleRegistry.xml.
* aliases: aliases for modules. Source of truth for -b, -u, -i options. Example | mpml: MPMLink
* suites: each subentry for this config key is a separate suite. It contains restart,build and custom subconfigs.
* suites/restart: Marks if after the suite the restart command should be executed [true/false].
* suites/build: Map of modules to build with flags. Example | MPMLink: swt
* suites/custom: List of commands to execute by aliast. Example | - full

## Usage
### Build
To build one module src files, run:
```bash
wc_builder -b mpml_s
```
To build multiple modules src files, run:
```bash
wc_builder -b mpml_s ass_s
```
To build src, src_test, src_web:
```bash
wc_builder -b mpml_stw
```
To build src, src_test, src_web and after that restart:
```bash
wc_builder -b mpml_stw -r
```
To clobber and build src:
```bash
wc_builder -b mpml_cs
```


### Test
To execute all unit tests in module:
```bash
wc_builder -u mpml
````
To execute all integration tests in module:
```bash
wc_builder -i mpml
```

To execute all test in one class file unit tests in module:
```bash
wc_builder -u mpml_ATestClass.class
```
To execute all test in one class file integration tests in module:
```bash
wc_builder -i mpml_ATestClass.class
```

### Suite
To execute suite:
```bash
wc_builder -s suiteName1
```

### Custom Commands
To execute previously defined command:
```bash
wc_builder -c CommandAliast
```