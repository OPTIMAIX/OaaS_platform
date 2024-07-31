from typing import List
from fastapi import APIRouter, Path
from fastapi_pagination import Page, paginate
from fastapi_pagination.bases import AbstractPage

from oaasplatform.main import logger
from oaasplatform.schemas.designs import DesignsIn, DesignsOut, DesignsUpdate

router = APIRouter(tags=["Designs handling module"])

mock_design = DesignsOut(
    designId="110",
    name="Network Plannig Use Case",
    description="This is the complete network used for the network planning use case",
    ownerInfo="optimaix",
    designJson={
        "network": {
            "nodes": [
                {"id": "node1", "type": "router"},
                {"id": "node2", "type": "switch"},
                {"id": "node3", "type": "computing", "cpu": "4 cores", "ram": "16GB"},
                {"id": "node4", "type": "computing", "cpu": "8 cores", "ram": "32GB"}
            ],
            "links": [
                {"source": "node1", "target": "node2", "capacity": "1Gbps", "latency": "10ms"},
                {"source": "node2", "target": "node3", "capacity": "1Gbps", "latency": "5ms"},
                {"source": "node2", "target": "node4", "capacity": "10Gbps", "latency": "1ms"}
            ]
        }
    }
)

class MockPage(Page):
    @classmethod
    def create(cls, items: List[DesignsOut], total: int, params: dict) -> AbstractPage:
        return cls(items=items, total=total, page=params['page'], size=params['size'])

@router.get("/designs", response_model=Page[DesignsOut])
async def get_designs() -> Page[DesignsOut]:
    return MockPage.create(items=[mock_design], total=1, params={"page": 1, "size": 10})

@router.get("/designs/{designId}", response_model=DesignsOut)
async def get_design(designId: int = Path(..., description="Unique identifier for an design")) -> DesignsOut:
    return mock_design

@router.post("/designs", response_model=DesignsOut)
async def create_design(design: DesignsIn):
    logger.info("Creating image")
    return mock_design

@router.put("/designs/{designId}", response_model=DesignsOut)
async def update_design(design: DesignsUpdate, designId: int = Path(..., description="Unique identifier for an design")) -> DesignsOut:
    return mock_design

@router.delete("/designs/{designId}")
async def delete_design(designId: int = Path(..., description="Unique identifier for an design")):
    return "Design deleted"
