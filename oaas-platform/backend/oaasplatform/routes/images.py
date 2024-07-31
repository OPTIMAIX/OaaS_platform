from fastapi import APIRouter, Path
from fastapi_pagination import Page
from fastapi_pagination.ext.tortoise import paginate

from oaasplatform.main import logger
import oaasplatform.crud.images as crud
from oaasplatform.schemas.status import Status
from oaasplatform.schemas.images import ImagesInSchema as InSchema
from oaasplatform.schemas.images import ImagesOutSchema as OutSchema
from oaasplatform.schemas.images import ImagesUpdate

router = APIRouter(tags=["Image Management module"])

@router.get("/images", 
            response_model=Page[OutSchema])
async def get_images() -> Page[OutSchema]:
    logger.info("Getting images")
    queryset = crud.get_images()
    paginated_query = await paginate(queryset)
    
    items = [OutSchema.from_orm(item) for item in paginated_query.items]
    paginated_query.items = items
    return paginated_query


@router.post("/images", response_model=OutSchema)
async def create_image(repository: InSchema):
    logger.info("Creating image")
    return await crud.create_image(repository)


@router.get("/images/{imageId}",
            response_model=OutSchema)
async def get_image(imageId: int = Path(..., description="Unique identifier for an image")) -> OutSchema:
    return await crud.get_image(imageId=imageId)


@router.put("/images/{imageId}",
            response_model=OutSchema)
async def update_image(image: ImagesUpdate,
                            imageId: int = Path(..., description="Unique identifier for an image")) -> OutSchema:
    return await crud.update_image(imageId=imageId, image=image)


@router.delete("/images/{imageId}",
               response_model=Status)
async def delete_image(imageId: int = Path(..., description="Unique identifier for an image")) -> Status:
    return await crud.delete_image(imageId=imageId)
