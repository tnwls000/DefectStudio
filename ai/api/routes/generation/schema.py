from typing import List, Union, Optional

from pydantic import BaseModel

class GenerationTaskResponse(BaseModel):
    status: str
    type_of_result: str
    result: Optional[Union[List[str], List[bytes]]]