from IPython.display import display, SVG
from pydantic import BaseModel, Field, PrivateAttr
from jupyter_client.manager import start_new_kernel
import queue
import json
from IPython.display import display, SVG, HTML
import re
from openai import OpenAI


def query_llama(
    prompt: str,
    system: str = "You are a helpful assistant.",
    base_url: str = "http://localhost:8080/v1",
    model: str = "llama",
    temperature: float = 0.7,
    max_tokens: int = 1024,
    api_key: str = "not-required",
) -> str:
    """Sends a prompt to a local llama.cpp server via the OpenAI-compatible API.

    Args:
        prompt (str): The user message to send.
        system (str): System prompt. Defaults to a generic assistant.
        base_url (str): Base URL of the llama.cpp server. Defaults to http://localhost:8080/v1.
        model (str): Model name passed to the API (llama.cpp ignores this but it must be set).
        temperature (float): Sampling temperature.
        max_tokens (int): Maximum tokens to generate.

    Returns:
        str: The model's response text.
    """
    client = OpenAI(base_url=base_url, api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def load_sysml_file(file_path: str) -> str:
    """Loads Sysml file to string

    Args:
        file_path (str): The path to the SysML file.

    Returns:
        str: The content of the SysML file as a string.
    """
    with open(file_path, "r") as f:
        return f.read()


class SysMLKernelClient(BaseModel):
    a_repo: str = Field(
        default="http://localhost:9000",
        description="The URL of the SysMLv2 repository.",
    )
    a_timeout: int = Field(
        default=60, description="Timeout for waiting for kernel responses in seconds."
    )
    a_kernel_name: str = Field(
        default="sysml", description="The name of the kernel to connect to."
    )

    _kernel_manager: object = PrivateAttr()
    _kernel_client: object = PrivateAttr()

    def model_post_init(self, __context__):
        """Runs automatically after instantiation"""
        self._kernel_manager, self._kernel_client = start_new_kernel(
            kernel_name=self.a_kernel_name
        )
        self.set_repo(self.a_repo)

    def help(self):
        """Lists the commands that can be run with the run function."""
        out = self.run_reg("%help")
        print(out[0]["text/plain"])

    def set_repo(self, repo_url: str):
        """Sets the URL:port for the repo.

        Args:
            repo_url (str): The URL:port of the SysMLv2 repository.
        """
        out = self.run_reg("%repo " + repo_url)
        print(out[0]["text/plain"])

    def get_projects(self):
        """Lists all the projects in the repo."""
        out = self.run_reg("%projects")
        print(out[0]["text/plain"])
        # txt = out[0]["text/plain"]
        # txt = re.sub(r"API.+\n", "", txt)  # Remove the API info line
        # return out[0]["text/plain"].split("\n")

    def load_project(self, project_name: str):
        """Gets the details of a project in the repo.

        Args:
            project_name (str): The name of the project to get details for.
        """
        out = self.run_reg("%load " + project_name)
        return out

    def push_to_repo(self, element_name: str):
        """Commits all elements in the element or package to the Sysml API.

        Args:
            element_name (str): The name of the element or package to be committed.
        """
        out = self.run_reg("%publish " + element_name)
        return out

    def viz_element(
        self, element_name: str, save_file: str = None, display_inline: bool = True
    ):
        """Visualizes a SysMLv2 diagram in the kernel.

        Args:
            element_name (str): Package or element name to be visualized. For example, if you want to visualize the package MyPkg, you can call viz_element("MyPkg"). If you want to visualize a specific element, you can call viz_element("MyPkg::myElement").
            save_file (str, optional): Path to save the SVG image. If None, image is not saved.
            display_inline (bool): Whether to display the image inline in the notebook. Defaults to True.
        """
        self.run_viz(
            "%viz " + element_name, save_file=save_file, display_inline=display_inline
        )
        # self.render(out)

    def shutdown_kernel(self):
        """Shuts down the Sysml kernel."""
        self._kernel_client.stop_channels()
        self._kernel_manager.shutdown_kernel()

    def run(self, code: str, save_file: str = None, display_inline: bool = True):
        if re.search(r"\s*%viz\s*", code):
            return self.run_viz(
                code, save_file=save_file, display_inline=display_inline
            )
        else:
            return self.run_reg(code)

    def run_reg(self, code: str):
        """Runs Sysmlv2 magic commands or SysMLv2 textual syntax in the kernel and returns the outputs.

        Args:
            code (str): The code to be executed in the kernel.

        Example::
            run("%repo http://localhost:9000")
            run("%projects")
            run("%publish MyPkg")

            # 1. Your Python-generated SysMLv2 textual syntax:
            sysml_src = ""
            package MyPkg {
                part def Vehicle;
                part myCar2 : Vehicle;
            }
            ""
            # 2. Parse it in the SysML kernel
            run(sysml_src)

        Returns:
            list: A list of outputs from the kernel execution.
        """
        print(f"Running code in {self.a_kernel_name} kernel:...")
        msg_id = self._kernel_client.execute(code)
        outputs = []
        while True:
            msg = self._kernel_client.get_iopub_msg(timeout=self.a_timeout)
            if msg["parent_header"].get("msg_id") != msg_id:
                continue
            t = msg["msg_type"]
            if t == "stream":
                outputs.append(msg["content"]["text"])
            elif t in ("execute_result", "display_data"):
                outputs.append(msg["content"]["data"])
            elif t == "error":
                raise RuntimeError("\n".join(msg["content"]["traceback"]))
            elif t == "status" and msg["content"]["execution_state"] == "idle":
                break
        return (
            outputs[0]["text/plain"]
            if len(outputs) == 1 and isinstance(outputs[0], str)
            else outputs
        )

    def run_viz(self, code: str, save_file: str = None, display_inline: bool = True):
        """Runs SysMLv2 visualization commands in the kernel and renders the diagrams in the notebook.

        Args:
            code (str): The code to be executed in the kernel.
            save_file (str, optional): Path to save the SVG image. If None, image is not saved.
            display_inline (bool): Whether to display the image inline in the notebook. Defaults to True.

        Raises:
            RuntimeError: _description_
        """
        msg_id = self._kernel_client.execute(code)
        while True:
            msg = self._kernel_client.get_iopub_msg(timeout=self.a_timeout)
            if msg["parent_header"].get("msg_id") != msg_id:
                continue
            t = msg["msg_type"]
            if t in ("execute_result", "display_data"):
                data = msg["content"]["data"]
                if "image/svg+xml" in data:
                    svg_content = data["image/svg+xml"]

                    # Save to file if requested
                    if save_file:
                        with open(save_file, "w", encoding="utf-8") as f:
                            f.write(svg_content)
                        print(f"SVG saved to: {save_file}")

                    # Display inline if requested
                    if display_inline:
                        img_svg = SVG(svg_content)
                        display(img_svg)
                elif "text/html" in data:
                    if display_inline:
                        display(HTML(data["text/html"]))
            elif t == "error":
                raise RuntimeError("\n".join(msg["content"]["traceback"]))
            elif t == "status" and msg["content"]["execution_state"] == "idle":
                break
