CFG_FILE_CONTENT = """profile: prod
root: /opt
fail_on_error: false
commands:
  ootb:
    restart: echo "Restarting"
  custom:
    full: echo "Full"
input:
  build_order: ignored/compile.includes
  module_registry: ignored/moduleRegistry.xml
aliases:
  mpml: MPMLink
  mpmlc: MPMLinkCommon
  ppb: ProcessPlanBrowser
  ass: Associative
suites:
  current:
    restart: true
    build:
      MPMLink: cst
      MPMLinkCommon: cst
      ProcessPlanBrowser: cst
"""
