from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class solutionObjectSchema(BaseModel):
    options: Optional[List[str]]
    timeTaken: Optional[str] = 0

class rootTestObjectSchema(BaseModel):
    __root__: Dict[str, solutionObjectSchema]

class submitTestSchema(BaseModel):
    response: rootTestObjectSchema
    testId: str
  