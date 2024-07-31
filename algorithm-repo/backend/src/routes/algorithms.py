from fastapi import APIRouter, Path
from typing import List

from src.main import logger
from src.schemas.algorithms import AlgorithmsOut
from src.utils.algorithms_wrapper import read_algorithm, read_algorithms

router = APIRouter(tags=["Available Algorithms"])

@router.get("/algorithms",
            response_model=List[AlgorithmsOut])
async def get_algorithms() -> List[AlgorithmsOut]:
    return read_algorithms()

@router.get("/algorithms/{algorithm_id}",
            response_model=AlgorithmsOut)
async def get_algorithm(algorithm_id: int = Path(None, description="Identifier for an algorithm")) -> AlgorithmsOut:
    return read_algorithm(algorithm_id)