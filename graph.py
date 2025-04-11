from langgraph.graph import START, StateGraph, END
from langgraph.graph import StateGraph
from data_models import JobDescriptionGraphState
from utils import CacheManager # Assuming cache_manager is defined in utils.py
from typing import List, Dict
from agents import create_jd_agent  # Replace 'some_module' with the actual module where create_rar_agent is defined

cache_manager = CacheManager()
# NODE TO CREATE JOB DESCRIPTION
def create_job_description(state: JobDescriptionGraphState) -> JobDescriptionGraphState:
    try:
        if not cache_manager.has("jdw_agent_chain"):
            cache_manager.set("jdw_agent_chain", create_jd_agent())

        jdw_agent_chain = cache_manager.get("jdw_agent_chain")
        #GET ALL JOB REQUIREMENTS FOR GENERATION OF JOB DESCRIPTION
        job_openings = state.get("job_openings", [])

        # VARIABLE HOLDER
        job_descriptions = []

        for opening in job_openings:
            job_description = jdw_agent_chain.invoke({
                "raw_job_description": opening.get("content"),
                "job_title": opening.get("name")
            })
            job_descriptions.append(job_description)

        print(f'---JOB DESCRIPTIONS GENERATED FOR: {len(job_openings)} JOB OPENINGS---')
        return {"job_descriptions": job_descriptions}
    
    except Exception as e:
        raise RuntimeError(f"ERROR IN 'create_job_description' NODE: {str(e)}")
def graphbuilder():
    #PLOT THE GRAPH
    graph_builder = StateGraph(JobDescriptionGraphState)
    ## ADD NODES TO THE GRAPH
    graph_builder.add_node("CreateJobDescription",create_job_description )

    ## ADD EDGES TO THE GRAPH
    graph_builder.add_edge(START, "CreateJobDescription")
    graph_builder.add_edge("CreateJobDescription", END)

    return graph_builder.compile()
