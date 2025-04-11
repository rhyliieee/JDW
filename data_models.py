#llm dict state

from pydantic import BaseModel
from typing import TypedDict, Annotated, List, Dict, Any, AnyStr, Optional

class JobDataModel(BaseModel):
    job_title: str
    job_type: str
    department: str
    expiry_date: str
    job_duties: str
    job_qualification: str
    expected_start_date: str
    job_location: str
    finalized_job_description: Annotated[str, "COMPILED DESCRIPTION THAT CONTAINS ALL JOB REQUIREMENTS AND RESPONSIBILITIES"]

class JobDescriptionGraphState(TypedDict):
    job_openings: List[Dict[AnyStr, Any]]
    job_descriptions: List[JobDataModel]

class JDWRequest(BaseModel):
    job_openings: List[Dict[AnyStr, Any]]

class StartResponse(BaseModel):
    trace_id: str
    message: str

class StatusResponse(BaseModel):
    trace_id: str
    status: str
    progress: Optional[Dict[str, str]] = None
    results: Optional[Dict[str, Any]] = None

