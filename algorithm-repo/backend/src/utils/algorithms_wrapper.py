from fastapi import HTTPException
from typing import List
from pydantic import parse_obj_as
import json, os

from src.main import logger
from src.schemas.algorithms import AlgorithmsOut
from src.utils.algorithms_lookups import lookup_all_algorithms

ALGORITHMS_FILE = "algorithms.json"

def create_algorithms_file():
    if os.path.exists(ALGORITHMS_FILE):
        logger.info(f"File {ALGORITHMS_FILE} already exists, updating...")
        os.remove(ALGORITHMS_FILE)
        #raise FileExistsError
    # Creating!
    list_modules = lookup_all_algorithms()
    list_dict = []
    id = 0

    for alg in list_modules:
        info_algorithms = {
            "id": id,
            "name": "name",
            "version": "version",
            "description": "description",
            "module": "",
            #"input_parameters": "",
            "input_schema": "",
            "output_schema": "",
        }
        try:
            data = alg.to_dict()
        except:
            raise Exception

        info_algorithms["name"] = data["name"]
        info_algorithms["version"] = data["version"]
        info_algorithms["description"] = data["description"]
        info_algorithms["module"] = data["module"]
        #info_algorithms["input_parameters"] = data["input_parameters"]
        info_algorithms["input_schema"] = data["input_schema"]
        info_algorithms["output_schema"] = data["output_schema"]

        list_dict.append(info_algorithms)
        id = id+1

    # Write to file
    with open(ALGORITHMS_FILE, "w+") as file:
        json.dump(list_dict, file, indent=4)

#
#   Routes functions!
#

def read_algorithms() -> List[AlgorithmsOut]:
    try:
        file = open(ALGORITHMS_FILE, "r")
        data = json.loads(file.read())
        return parse_obj_as(List[AlgorithmsOut], data)
    except FileNotFoundError:
        logger.error("File not found")
        raise HTTPException(
            status_code=422,
            detail=f"Algorithms file not found or empty"
        )

def read_algorithm(id: int) -> dict:
    file = open(ALGORITHMS_FILE, "r")
    data = json.loads(file.read())
    
    for algorithm in data:
        if algorithm["id"] == id: 
            return AlgorithmsOut.parse_obj(algorithm)

    logger.error("Algorithm ID not found")
    raise HTTPException(
        status_code=422,
        detail=f"Algorithm ID {id} not found"
    )
