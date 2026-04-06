# Overview
This is intended to be used as a playground for experimenting with AI generation of SysMLv2 text using API keys for LLMs. It may also be possible to just skip the API keys and use Claude Code or Codex directly in the repo at this point. This is mainly for generating/editing SysMLv2 and visualizing the diagrams, nothing more comprehensive than that. There may be simpler dev environment architectures out there, but this uses free tools which are neatly packaged in a docker compose stack for quick setup. The following are the components of the environment, each contained in a docker container (using a docker compose stack) and notes on how they are used:

1) VS Code 
    - "Syside Editor: SysML v2 Essential" extension is used for SysMLv2 Syntax Highlighting
    - Jupyter notebooks (via "Jupyter" extension) used for AI API key SysMLv2 text generation experimentation.
    - Python code, managed by a local [UV environment](https://docs.astral.sh/uv/).
    - Python functions using the OpenAI interface, querying LLMs, output text to .sysml files, or sent to the SysMLv2 API server. SysML text diagrams can be analyzed at a shallow level using Syside Editor.

2) Jupyter Server (docker-compose.yml - container 3)
    - Jupyter server, separate from VSCode Jupyter (served via docker container) 
    - Hosts the SysMLv2 Jupyter kernel, included in [SysMLv2 Official Release](https://github.com/Systems-Modeling/SysML-v2-Release) that allows for diagram rendering. 
    - This repo and other repos containing example notebooks and .sysml files are bind-mounted into the docker container (handled in docker compose file). This way changes can be made in VSCode or the Jupyter server.

3) SysMLv2 API (docker-compose.yml - containers 1 + 2)
    - Postgres + SysMLv2 API (https://github.com/Systems-Modeling/SysML-v2-API-Services)
    - Enables loading / saving generated SysML

# Install

0) Install Docker if you don't already have it.
    - Mac/Windows: [Docker Desktop](https://www.docker.com/products/docker-desktop/)
    - Linux: [Docker Engine](https://docs.docker.com/engine/install/)  (I think you can use Docker Desktop on certain distros as well)

1) [Install VSCode](https://code.visualstudio.com/download); add VSCode Extensions from Extensions side bar (Cntl + Shift + X):
    - "Syside Editor: SysML v2 Essential"
    - "Jupyter"

2) Add `.env` file in the project root. It should include variables for the following that are loaded via Docker automatically when docker setup is run:
    ```
        PLAY_SECRET=<strong-hex-password-with-no-symbols>
        POSTGRES_PASSWORD=<strong-hex-password-with-no-symbols>
        JUPYTER_PASSWORD=set-this-to-strong-password
        # Add your LLM API keys here too.
    ```
    - To ensure passwords have enough "entropy" (otherwise API docker build may fail) use the following command to generate passwords: `openssl rand -hex 32` (PLAY_SECRET should use at least 32, others you can probably use `-hex 8`)
    - You can add other API keys for your LLM services to this file as well for use in the local UV environment

3) From project root, run the script that pulls other example repos and launches all docker containers: 
    - `bash start.sh`

# Usage

After the containers all start successfully, here is a sample workflow:

- Ensure docker containers are running: `docker ps`
    - There should be 3 running with the prefix "sysmlv2-"
- Access the SysMLv2 API server docs here: http://localhost:9000/docs/
- Access the separate Jupyter notebook here: http://localhost:8888
    - You'll need to enter the password here that was added to the `.env` file for JUPYTER_PASSWORD
- Create a Jupyter notebook (or borrow an example from one of the pulled repos) in VSCode (or the Jupyter server; it doesn't matter. Since the folder is "bind-mounted", adding a file in one location will cause it to appear in both locations).
    - Use this notebook in VSCode for Python code (Langchain, OpenAI, regex, etc...)
    - Add/remove packages using `uv add` / `uv remove`. See other [commands](https://docs.astral.sh/uv/reference/cli/) if not familiar
- Create a Jupyter notebook from the Jupyter server. 
    - Click the "+" button to open a "Launcher". At the launch screen, click the "SysML" button under "Notebook"
    - **IMPORTANT**: Don't modify a file from both VSCode *AND* the web Jupyter Server; this may cause saving conflicts. Thats why we're keeping one notebook for rendering (using the SysML Jupyter kernel), where you can copy SysML code into, and one for code generation (using the python kernel). Its basically a way to have two different environments operating on the same folder.
- Shutdown docker containers simultaneously (data will be preserved):
    - `docker compose down`

