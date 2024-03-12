from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from kubectl_executor_simple import CustomKubectlExecutorSimpleAgent
# from autogen.coding import LocalCommandLineCodeExecutor
import os
from dotenv import load_dotenv
load_dotenv()

config_list = [{"model": "gpt-4-0125-preview", "api_key": os.environ["OPENAI_API_KEY"]}]
llm_config = {
    "config_list": config_list,
}

# Agent definitions 
user_proxy = UserProxyAgent(
    name="SystemExpert",
    system_message="A human admin to guide and provide-feedback.",
    code_execution_config={"last_n_messages": 2, "work_dir": "groupchat", "use_docker": False},
    human_input_mode="NEVER",
    # is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
)

kubernetes_simple_expert = CustomKubectlExecutorSimpleAgent(
    name="KubernetesExpert",
    system_message="Fetch and provide data from the Kubernetes cluster. {term_msg}",
    description="""
    Expert in Kubernetes and how various tools are installed in the cluster via Kubernetes-specific resources..
    """,
    code_execution_config={"last_n_messages": 2, "work_dir": "groupchat", "use_docker": False},
    config_list=config_list,
)

groupchat = GroupChat(
    agents=[user_proxy, kubernetes_simple_expert], 
    messages=[], 
    max_round=3,
    # allow_repeat_speaker=True, # they just go back and forth forever
    speaker_selection_method="auto",
)

groupchat_manager = GroupChatManager(
    groupchat=groupchat, 
    system_message="Help determine information about the Kubernetes cluster.",
    llm_config=llm_config, 
    human_input_mode="TERMINATE",
)

user_proxy.initiate_chat(
    groupchat_manager,
    message="Return a json representation of kubernetes pods in the cluster"
)