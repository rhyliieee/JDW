from typing import Type
from pydantic import BaseModel
from langchain.schema.runnable import RunnableSerializable
from langchain.prompts import ChatPromptTemplate
from utils import CacheManager, load_prompts
import os
from pathlib import Path
from dotenv import load_dotenv
from data_models import JobDataModel
from langchain_openai import ChatOpenAI
load_dotenv() 
cache_manager = CacheManager()
##############################
# STEP 1: PREPARE PROMPT
# STEP 2: PREPARE LLM MODEL
# STEP 3: CHAIN PROMPT AND LLM

###### PROCESS INSIDE GRAPH

# STEP 4: GET DATA FROM STATE
# STEP 5: INVOKE CHAIN WITH DATA
# STEP 6: RETURN AND UPDATE THE STATE

PROMPTS_PATH = Path("prompts.yaml")

def initialize_llm(model_name: str):
    """
    Initialize the LLM with specific configurations.
    """

    # Load API key from environment variables
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set in the environment variables.")

    # Initialize the LLM with the given model name and configurations
    return ChatOpenAI(
        model=model_name,
        temperature=0.3,  # Set the temperature for response creativity
        api_key=api_key
    )

def create_jd_agent() -> RunnableSerializable:
    try:
        # SET PROMPTS IF NOT IN CACHE
        if not cache_manager.has("agent_prompts"):
            cache_manager.set("agent_prompts", load_prompts(PROMPTS_PATH))

        jdw_agent_prompt = cache_manager.get("agent_prompts")["jdw_agent_prompt"]

        # INITIALIZE THE LLM MODEL
        jdw_llm = initialize_llm('gpt-4o-mini')

        # ATTACH DATA MODEL TO AGENT
        jdw_llm_with_structured_output = jdw_llm.with_structured_output(JobDataModel)

        # PREPARE CHAT PROMPT TEMPLATE
        jdw_agent_sys_prompt = ChatPromptTemplate.from_template(jdw_agent_prompt)

        # CHAIN THE PROMPT TEMPLATE WITH THE RAR AGENT
        jdw_agent_chain = jdw_agent_sys_prompt | jdw_llm_with_structured_output

        print(f"---CROSS JOB COMPARISON AGENT CREATED---")

        return jdw_agent_chain
    except Exception as e:
        print(f"---ERROR IN CREATING CJC AGENT: {e}---")
        raise RuntimeError(f"FAILED TO CREATE CJC AGENT: {e}")