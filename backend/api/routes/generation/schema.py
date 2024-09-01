from typing import Optional

from pydantic import BaseModel, Field

class TTIRequest(BaseModel):
    model: str = Field(...)
    prompt: str = Field(...)
    negative_prompt: Optional[str] = Field(None)
    width: Optional[int] = Field(512)
    height: Optional[int] = Field(512)
    num_inference_steps: Optional[int] = Field(50)
    guidance_scale: Optional[float] = Field(7.5)
    seed: Optional[int] = Field(-1)
    num_images_per_prompt: Optional[int] = Field(1)
    batch_count: Optional[int] = Field(1)
    batch_size: Optional[int] = Field(1)