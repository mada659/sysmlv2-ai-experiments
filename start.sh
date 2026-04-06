#!/bin/bash

# Clone additional repos for experimenting with SysMLv2
if [ ! -d "./sysmlv2" ]; then
  # SysML jupyter env is already installed with the jupyter docker container. This is just to have access to the documentation and sample files.
  git clone https://github.com/Systems-Modeling/SysML-v2-Release.git ./sysmlv2
fi
if [ ! -d "./example_sysml_notebooks" ]; then
# Some good examples of Jupyter notebooks for SysMLv2. This is not an official repo, but it has some good examples of using the SysMLv2 kernel in Jupyter.
  git clone https://github.com/MBSE4U/SysMLv2JupyterBook.git ./example_sysml_notebooks
fi
if [ ! -d "./example_sysml_files" ]; then
# Some good examples of SysMLv2 files. This is not an official repo, but it has some good examples of a sequential jupyter build.
  git clone https://github.com/sensmetry/advent-of-sysml-v2.git ./example_sysml_files
fi

# Pull latest changes (optional)
cd sysmlv2 && git pull && cd ..
cd example_sysml_notebooks && git pull && cd ..
cd example_sysml_files && git pull && cd ..

# Start containers. The --build flag ensures that any changes to the Dockerfiles are picked up and the images are rebuilt. 
#The -d flag runs the containers in detached mode, allowing the script to exit while the containers continue running in the background.
docker compose up --build -d