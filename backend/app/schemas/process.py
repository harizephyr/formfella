from pydantic import BaseModel
from typing import List, Dict

# Pydantic models
class FormQuestion(BaseModel):
    field_id: str
    question: str
    field_name: str
    current_value: str

class QuestionResponse(BaseModel):
    field_id: str
    answer: str

class FormSubmission(BaseModel):
    responses: List[QuestionResponse]

class ProcessResponse(BaseModel):
    form_id: str
    questions: List[FormQuestion]
    total_questions: int