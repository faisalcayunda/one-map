from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.factory import Factory
from app.core.params import CommonParams
from app.core.responses import PaginatedResponse
from app.models import UserModel
from app.schemas.file_schema import FileSchema
from app.services import FileService

router = APIRouter()


@router.get("/files", response_model=PaginatedResponse[FileSchema], dependencies=[Depends(get_current_active_user)])
async def get_files(params: CommonParams = Depends(), service: FileService = Depends(Factory().get_file_service)):
    filter = params.filter
    sort = params.sort
    search = params.search
    group_by = params.group_by
    limit = params.limit
    offset = params.offset
    files, total = await service.find_all(filter, sort, search, group_by, limit, offset)

    return PaginatedResponse(
        items=[FileSchema.model_validate(file) for file in files],
        total=total,
        limit=limit,
        offset=offset,
        has_more=total > (offset + limit),
    )


@router.get("/files/{id}", response_model=FileSchema)
async def get_file(id: str, service: FileService = Depends(Factory().get_file_service)):
    file = await service.find_by_id(id)
    return file


@router.post("/files", response_model=FileSchema, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    current_user: UserModel = Depends(get_current_active_user),
    service: FileService = Depends(Factory().get_file_service),
):
    result = await service.upload_file(file=file, description=description, user_id=current_user.id)
    return result


@router.get(
    "/files/{file_id}",
    response_model=FileSchema,
    summary="Dapatkan metadata file",
    dependencies=[Depends(get_current_active_user)],
)
async def get_file_info(file_id: str, service: FileService = Depends(Factory().get_file_service)):
    file = await service.find_by_id(file_id)
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File tidak ditemukan")
    return file


@router.get("/files/{file_id}/download", summary="Download file", dependencies=[Depends(get_current_active_user)])
async def download_file(file_id: str, service: FileService = Depends(Factory().get_file_service)):
    file_content, object_info, file_model = await service.get_file_content(file_id)

    async def iterfile():
        try:
            chunk = await file_content.content.read(8192)
            while chunk:
                yield chunk
                chunk = await file_content.content.read(8192)
        finally:
            await file_content.release()

    return StreamingResponse(
        iterfile(),
        media_type=file_model.content_type,
        headers={"Content-Disposition": f'attachment; filename="{file_model.filename}"'},
    )


@router.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Hapus file")
async def delete_file(
    file_id: str,
    current_user: UserModel = Depends(get_current_active_user),
    service: FileService = Depends(Factory().get_file_service),
):
    await service.delete_file_with_content(file_id, str(current_user.id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
