# app/models.py
from pydantic import BaseModel, Field
from typing import Optional, Union

class StartRequest(BaseModel):
    topic: str = Field(..., description="El tema para iniciar la investigación del agente")
    searcher: str = Field(..., description="El buscador en el cual se hará la investigación del agente")

class StartResponse(BaseModel):
    thread_id: str
    interrupt_message: Optional[str] = None
    status: str = "Interrupt received" # O "Error" si falla

class ResumeRequest(BaseModel):
    thread_id: str
    # Permitir solo uno de los dos: approval o feedback
    approval: Optional[bool] = None
    feedback: Optional[str] = None

    # Validación personalizada (opcional pero recomendada)
    # from pydantic import validator
    # @validator('feedback', always=True)
    # def check_approval_or_feedback(cls, v, values):
    #     if values.get('approval') is not None and v is not None:
    #         raise ValueError('Cannot provide both approval and feedback')
    #     if values.get('approval') is None and v is None:
    #         raise ValueError('Must provide either approval (true) or feedback (string)')
    #     return v

class ResumeResponse(BaseModel):
    thread_id: str
    interrupt_message: Optional[str] = None
    final_report: Optional[str] = None
    status: str # e.g., "Interrupt received", "Completed", "Error"