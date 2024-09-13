from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
import os
from core.config import settings
from typing import List

router = APIRouter(
    prefix="/model",
)

