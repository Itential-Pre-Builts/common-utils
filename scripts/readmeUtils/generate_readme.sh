#!/bin/sh

# Check if documenation/documentation_mapping.json exists and if not, do not continue

# Ensure jinja2 template files are executable
chmod +x ./readmeUtils/generate_asset_readmes.jinja2
chmod +x ./readmeUtils/generate_readme.jinja2

# Create virtual environment for rendering jinja2 templates
python3 -m venv venv
source venv/bin/activate
python -m pip install Jinja2

# Create asset READMEs
python ./readmeUtils/generate_asset_readmes.py

# Aggregate asset READMEs and overall Project README and generates
# top level README
python ./readmeUtils/generate_readme.py

python ./readmeUtils/generate_metadata.py
