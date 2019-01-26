import yaml

settings = {}
with open('settings.yml', 'r') as f:
  settings = yaml.load(f)
