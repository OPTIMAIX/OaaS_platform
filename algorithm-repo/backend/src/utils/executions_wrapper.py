from fastapi import HTTPException
from typing import Union
from datetime import datetime
import os, json

from src.main import logger
from src.worker import celery, execute_algorithm
from src.schemas.executions import ExecutionsOut
from src.utils.algorithms_wrapper import read_algorithm
from src.utils.algorithms_lookups import lookup_algorithm

EXECUTIONS_FILE = "executions.json"

def create_executions_file():
    if os.path.exists(EXECUTIONS_FILE):
        logger.info(f"File {EXECUTIONS_FILE} already exists. Skipping...")
        #raise FileExistsErrorreturn
    else:
        # Creating empty 
        list_dict = []

        # Write to file
        with open(EXECUTIONS_FILE, "w+") as file:
            json.dump(list_dict, file, indent=4)

def get_last_execution() -> dict:
    file = open(EXECUTIONS_FILE, "r")
    data = json.loads(file.read())
    
    try:
        output = data[-1]
    except IndexError:
        output = []

    return output

def append_execution(exec: dict):
    if not os.path.exists(EXECUTIONS_FILE):
        logger.error("File dont exists")
        raise FileNotFoundError

    file = open(EXECUTIONS_FILE, "r")
    data = json.loads(file.read())
    data.append(exec)
    
    with open(EXECUTIONS_FILE, "w+") as file:
        json.dump(data, file, indent=4)

def update_execution(id: int):
    if os.path.exists(EXECUTIONS_FILE):
        with open(EXECUTIONS_FILE, "r") as file:
            data = json.load(file)
        
        for executions in data:
            if executions["id"] == id:
                if executions["finished"] == "":
                    # Finish celery
                    celery.control.revoke(executions["task_id"], terminate=True)
                    executions["finished"] = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
                    executions["error"]["success"] = False
                    executions["error"]["type"] = "force terminated execution"
                    executions["error"]["detail"] = "user terminated the execution"
                    # Save to file
                    with open(EXECUTIONS_FILE, "w+") as file:
                        json.dump(data, file, indent=4)
                    return executions
                else:
                    logger.error("Execution {id} already finished")
                    raise HTTPException(
                        status_code=422,
                        detail=f"Execution already finished"
                    )

        logger.error("ID not found")
        raise IndexError
    
    raise FileNotFoundError


#
#   Routes functions!
#

def read_execution(execution_id: int):
    file = open(EXECUTIONS_FILE, "r")
    data = json.loads(file.read())
    
    for execution in data:
        if execution["id"] == execution_id: 
            return ExecutionsOut.parse_obj(execution)

    logger.error("ID not found")
    raise HTTPException(
        status_code=422,
        detail=f"Execution ID {execution_id} not found"
    )

def start_execution(algorithm_id: int, input_parameters: dict, callback_id: Union[int, None], ip_client: str):
    logger.info(f"Starting execution with {algorithm_id}...")
    logger.info(f"Input parameters: {json.dumps(input_parameters)}")

    # Get algorithm
    algorithm_data = read_algorithm(algorithm_id)
    try:
        algorithm = lookup_algorithm(algorithm_data.name, input_parameters)
    except:
        raise HTTPException(
            status_code=422,
            detail=f"Unable to find algorithm"
        )

    # Validate Input
    if algorithm.validate_input() == False:
        raise HTTPException(
            status_code=422,
            detail=f"Input JSON not following the JSON Schema of the selected algorithm"
        )
    del algorithm

    # Creating execution
    last_exec = get_last_execution()
    if last_exec == []:
        exec_id = 0
    else:
        exec_id = last_exec["id"]+1

    # Start algorithm
    #algorithm.run()
    try:
        task = execute_algorithm.apply_async(args=[algorithm_data.name, input_parameters, callback_id, ip_client])
    except:
        raise HTTPException(
            status_code=422,
            detail=f"Unable to enqueue the algorithm execution"
        )

    exec_dict = {
        "id": exec_id,
        "name": algorithm_data.name,
        "task_id": task.id,
        "callback_id": callback_id,
        "input_parameters": input_parameters,
        "output": {},
        "error": {},
        "created": datetime.now().strftime("%Y-%m-%d, %H:%M:%S"),
        "finished": "",
    }

    # Append execution
    append_execution(exec_dict)

    return ExecutionsOut.parse_obj(exec_dict)

def stop_execution(execution_id):
    logger.info(f"Stopping execution {execution_id}...")

    # Update finished field
    try:
        execution = update_execution(execution_id)
    except IndexError:
        raise HTTPException(
            status_code=422,
            detail=f"Execution {execution_id} not found"
        )

    return ExecutionsOut.parse_obj(execution)

