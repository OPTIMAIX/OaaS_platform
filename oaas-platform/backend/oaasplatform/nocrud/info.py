from fastapi import HTTPException
import os, json

from oaasplatform.main import logger
from oaasplatform.schemas.info import InfoIn, InfoOut
from oaasplatform.utils import info as info_utils

def create_info():
    # Create JSON
        info = {
            "ip_address": "0.0.0.0",
            "ip_port": 5000,
            "name": "changeme",
            "description": "changeme",
            "owner_info": "changeme",
            "computation_resources": {
                "cpu": "",
                "ram": ""
            }
        }

        # Fill dict
        info = update_computation_resources(info)

        # Save to file
        with open("info_data.json", "w+") as file:
            json.dump(info, file, indent=4)

        try:
            info_obj = InfoOut.parse_obj(info)
            return info_obj
        except:
            raise HTTPException(
                status_code=422,
                detail="Validation error"
            )

def update_computation_resources(data):
    data["ip_address"] = info_utils.get_ip_public()
    data["computation_resources"]["cpu"] = info_utils.get_cpu()
    data["computation_resources"]["ram"] = info_utils.get_ram()
    return data

def get_info_startup():
    # Check if json file exists
    if os.path.exists("info_data.json"):
        with open("info_data.json", "r") as file:
            data = json.load(file)
            
        data = update_computation_resources(data)
        with open("info_data.json", "w+") as file:
            json.dump(data, file, indent=4)

        info_obj = InfoOut(**data)
        logger.info("System info updated!")
        #return info_obj
    
    # If not exists, create with gathered info
    else:
        info_obj = create_info()
        logger.info("System info file created!")
        #return info_obj

""" 
    Routes methods

 """

async def get_info():
    # Check if json file exists
    if os.path.exists("info_data.json"):
        with open("info_data.json", "r") as file:
            data = json.load(file)
            info_obj = InfoOut(**data)
            return info_obj
    
    # If not exists, create with gathered info
    else:
        info_obj = create_info()
        return info_obj

async def update_info(info: InfoIn):
    # read JSON
    if os.path.exists("info_data.json"):
        with open("info_data.json", "r") as file:
            data = json.load(file)
            
        # Update JSON with new info
        data["name"] = info.name
        data["description"] = info.description
        data["owner_info"] = info.owner_info

        data = update_computation_resources(data)

        # Save to file
        with open("info_data.json", "w+") as file:
            json.dump(data, file, indent=4)

        # Return to user
        try:
            info_obj = InfoOut.parse_obj(data)
            return info_obj
        except:
            raise HTTPException(
                status_code=422,
                detail="Validation error"
            )
    else:
        raise HTTPException(
            status_code=422,
            detail="File info not exists"
        )
    
async def get_cpu_ram_info():
    return {
        "cpu": info_utils.get_cpu(),
        "ram": info_utils.get_ram()
    }
