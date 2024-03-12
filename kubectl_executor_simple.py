from autogen import UserProxyAgent
import subprocess
from typing import Callable, Dict, List, Literal, Optional, Union

class CustomKubectlExecutorSimpleAgent(UserProxyAgent):
    def __init__(
            self, 
            name:str, 
            system_message: Optional[Union[str, List]] = "", 
            code_execution_config: Optional[Union[Dict, Literal[False]]] = None, 
            config_list: Optional[List[Dict]] = None,
            human_input_mode: Optional[str] = "NEVER",
            description: Optional[str] = None,
        ):
        """
        Custom agent for executing various kubectl commands to extract data from a Kubernetes cluster.

        Usage:
        - get_named_resources: get a list of all the Kubernetes resources in the cluster
        """
        function_map = {
            "get_named_resources": self.get_named_resources,
        }

        custom_functions = [
            {
                "name": "get_named_resources",
                "description": "A function to get a list of named resources from a Kubernetes cluster. Takes two string arguments: resource_type and namespace_scoped.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "resource_type": {
                            "type": "string",
                            "description": "The api kind of Kubernetes resource, e.g., deployments, pods, nodes"
                        },
                        "namespace_scoped": {
                            "type": "boolean",
                            "description": "Whether the resource is namespace-scoped, e.g., true or false"
                        },
                    },
                    "required": ["resource_type", "namespace_scoped"],
                }
            }
        ]

        llm_config = {
            "functions": custom_functions,
            "config_list": config_list,
        }
        super().__init__(
            name=name, 
            system_message=system_message, 
            code_execution_config=code_execution_config, 
            llm_config=llm_config, 
            function_map=function_map, 
            human_input_mode=human_input_mode,
            description=description,
        )


    def get_named_resources(resource_type, namespace_scoped) -> str:
        """ A generic tool to extract named resources from a Kubernetes cluster based on input parameters """

        if namespace_scoped:
            command = r"""kubectl get %s --all-namespaces -o json | jq '[.items[] | {name: .metadata.name, namespace: .metadata.namespace}]'""" % resource_type
        else:
            command = r"""kubectl get %s -o json | jq '[.items[] | {name: .metadata.name}]'""" % resource_type

        try:
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error executing kubectl command for {resource_type}: {e.stderr}"
