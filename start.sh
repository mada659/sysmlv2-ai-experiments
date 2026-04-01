#!/bin/bash

# Clone additional repos for experimenting with SysMLv2
if [ ! -d "./sysmlv2" ]; then
  git clone https://github.com/Systems-Modeling/SysML-v2-Release.git ./sysmlv2
fi
if [ ! -d "./example_sysml_notebooks" ]; then
  git clone https://github.com/MBSE4U/SysMLv2JupyterBook.git ./example_sysml_notebooks
fi
if [ ! -d "./example_sysml_files" ]; then
  git clone https://github.com/sensmetry/advent-of-sysml-v2.git ./example_sysml_files
fi

# Pull latest changes (optional)
cd sysmlv2 && git pull && cd ..
cd example_sysml_notebooks && git pull && cd ..
cd example_sysml_files && git pull && cd ..

# Start containers
docker compose up