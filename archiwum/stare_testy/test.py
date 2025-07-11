import yaml
from lux_core.executor import run_scenario

with open("lux_core/layer0/layer0_scenerio.yaml") as f:
    scenario = yaml.safe_load(f)

result = run_scenario(scenario)
print(result)