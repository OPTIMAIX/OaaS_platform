from datetime import datetime

import os, json

EXECUTIONS_FILE = "executions.json"

def update_executions_file(task_id: str, output: dict, error: dict):
    if os.path.exists(EXECUTIONS_FILE):
        with open(EXECUTIONS_FILE, "r") as file:
            data = json.load(file)
    
        for executions in data:
            if executions["task_id"] == task_id:
                executions["output"] = output
                executions["error"] = error
                executions["finished"] = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
                # Save to file
                with open(EXECUTIONS_FILE, "w+") as file:
                    json.dump(data, file, indent=4)
                return executions
        raise IndexError
    raise FileNotFoundError