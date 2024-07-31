from fastapi import APIRouter, Path, Depends
from fastapi_pagination import Page, Params, paginate

import oaasplatform.crud.management as crud
from oaasplatform.schemas.management import OaaSNodeOut, OaaSNodeUpdate

from oaasplatform.nocrud import info
from oaasplatform.schemas.info import InfoIn, InfoOut

router = APIRouter(tags=["Platform Management module"])

# GET /oaasMaster
@router.get("/oaasMaster", response_model=InfoOut)
async def get_oaas_master() -> InfoOut:
    return await info.get_info()

# PUT /oaasMaster
@router.put("/oaasMaster",
            response_model=InfoOut)
async def update_oaas_master_info(info: InfoIn) -> InfoOut:
    return await info.update_info(info=info)

# GET /oaasNodes
@router.get("/oaasNodes", response_model=Page[OaaSNodeOut])
async def get_oaas_nodes(params: Params = Depends()) -> Page[OaaSNodeOut]:
    queryset = await crud.get_oaas_nodes()
    items = [OaaSNodeOut(**item) for item in queryset]
    return paginate(items, params)

# POST /oaasNodes
@router.post("/oaasNodes", response_model=OaaSNodeOut)
async def create_oaas_node(oaas_node: OaaSNodeOut) -> OaaSNodeOut:
    return "Method not implemented"

# PUT /oaasNodes/{oaasNodeId}
@router.put("/oaasNodes/{oaasNodeId}", response_model=OaaSNodeOut)
async def update_oaas_node(oaas_node: OaaSNodeUpdate, oaasNodeId: int = Path(..., description="Unique identifier for an OaaS Node")
                           ) -> OaaSNodeOut:
    return "Method not implemented"

# DELETE /oaasNodes/{oaasNodeId}
@router.delete("/oaasNodes/{oaasNodeId}", response_model=OaaSNodeOut)
async def delete_oaas_node(oaasNodeId: int = Path(..., description="Unique identifier for an OaaS Node")) -> OaaSNodeOut:
    return "Method not implemented"
