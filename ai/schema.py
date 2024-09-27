from typing import Optional, List, Union

from pydantic import BaseModel


class CeleryTaskResponse(BaseModel):
    task_name: str
    task_status: str
    task_arguments: dict
    result_data_type: Optional[str] = None
    result_data: Optional[Union[List[str], str]] = None
    message: Optional[str] = None
