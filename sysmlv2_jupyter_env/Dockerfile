# Use a Mambaforge base image, which is a faster alternative to Miniforge
# It includes a pre-installed conda-like environment with mamba
FROM condaforge/mambaforge:23.11.0-0
 
# Install dependencies available in apt that are good to have (git, JDK). Jupyter install handled later
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    # curl \
    wget \
    openjdk-17-jdk-headless \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
 
# Dont change this variable
USER $MAMBA_USER
 
# Set working directory
WORKDIR /mbse
 
# OPT 1) Copy only the install files
RUN wget https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/heads/master/install/jupyter/install.sh
RUN wget https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/refs/heads/master/install/jupyter/install.py
RUN chmod +x /mbse/install.sh && \
bash -x /mbse/install.sh
 
# OPT 1) Copy the entire SysMLv2 repo multiple GBs
# RUN git clone https://github.com/Systems-Modeling/SysML-v2-Release.git ./sysmlv2
# RUN chmod +x /mbse/install/jupyter/install.sh && \
# bash -x /mbse/install/jupyter/install.sh
 
# Add additional python libraries (using mamba). Or don't... just keep this env for SysMLv2 rendering
# RUN mamba install -y \
#     && mamba clean -afy
 
EXPOSE 8888
 
# Set default command to launch Jupyter Lab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--notebook-dir=/mbse"]