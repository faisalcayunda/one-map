from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.factory import Factory
from app.core.params import CommonParams
from app.core.responses import PaginatedResponse
from app.schemas.credential_schema import (
    CredentialCreateSchema,
    CredentialSchema,
    CredentialUpdateSchema,
    CredentialWithSensitiveDataSchema,
)
from app.schemas.user_schema import UserSchema
from app.services import CredentialService

router = APIRouter()


@router.post(
    "/credentials",
    summary="Buat kredensial baru",
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_credential(
    data: CredentialCreateSchema,
    current_user: UserSchema = Depends(get_current_active_user),
    service: CredentialService = Depends(Factory().get_credential_service),
):
    """
    Buat kredensial baru dengan data yang terenkripsi.

    Endpoint ini hanya dapat diakses oleh admin.

    **Data sensitive yang didukung:**

    - Database:
        - host, port, username, password, database_name
    - MinIO:
        - endpoint, access_key, secret_key, secure, bucket_name
    - API:
        - base_url, api_key
    - SSH:
        - host, port, username, password (atau private_key)
    - SMTP:
        - host, port, username, password, use_tls
    - FTP:
        - host, port, username, password
    """
    result = await service.create_credential(
        name=data.name,
        credential_type=data.credential_type,
        sensitive_data=data.sensitive_data,
        credential_metadata=data.credential_metadata,
        description=data.description,
        is_default=data.is_default,
        user_id=current_user.id,
    )
    return result


@router.get(
    "/credentials",
    response_model=PaginatedResponse[CredentialSchema],
    summary="Dapatkan daftar kredensial",
    dependencies=[Depends(get_current_active_user)],
    include_in_schema=False,
)
async def get_credentials(
    credential_type: Optional[str] = Query(None, description="Filter berdasarkan tipe kredensial"),
    include_inactive: bool = Query(False, description="Sertakan kredensial yang tidak aktif"),
    params: CommonParams = Depends(),
    service: CredentialService = Depends(Factory().get_credential_service),
):
    """
    Dapatkan daftar kredensial dengan filtering and pagination.
    """
    filter_params = params.filter or []
    sort = params.sort
    search = params.search
    group_by = params.group_by
    limit = params.limit
    offset = params.offset

    if credential_type:
        filter_params.append(f"credential_type={credential_type}")

    if not include_inactive:
        filter_params.append(f"is_active=true")

    credentials, total = await service.get_list_of_decrypted_credentials(
        filters=filter_params, sort=sort, search=search, group_by=group_by, limit=limit, offset=offset
    )

    return PaginatedResponse(
        items=[CredentialSchema(**credential) for credential in credentials],
        total=total,
        limit=limit,
        offset=offset,
        has_more=offset + limit < total,
    )


@router.get(
    "/credentials/{credential_id}",
    response_model=CredentialSchema,
    summary="Dapatkan kredensial dengan data terdekripsi",
    dependencies=[Depends(get_current_active_user)],
    include_in_schema=False,
)
async def get_credential(
    credential_id: UUID = Path(..., description="ID kredensial"),
    service: CredentialService = Depends(Factory().get_credential_service),
):
    """
    Dapatkan kredensial dengan data sensitif yang sudah didekripsi.

    Endpoint ini hanya dapat diakses oleh admin.
    """
    credential = await service.find_by_id(credential_id)

    return credential


@router.get(
    "/credentials/{credential_id}/decrypted",
    response_model=CredentialWithSensitiveDataSchema,
    summary="Dapatkan kredensial dengan data terdekripsi",
    dependencies=[Depends(get_current_active_user)],
    include_in_schema=False,
)
async def get_credential_decrypted(
    credential_id: UUID = Path(..., description="ID kredensial"),
    service: CredentialService = Depends(Factory().get_credential_service),
):
    """
    Dapatkan kredensial dengan data sensitif yang sudah didekripsi.

    Endpoint ini hanya dapat diakses oleh admin.
    """
    credential = await service.get_credential_with_decrypted_data(credential_id)

    return credential


@router.patch(
    "/credentials/{credential_id}",
    summary="Update kredensial",
    include_in_schema=False,
)
async def update_credential(
    credential_id: UUID,
    data: CredentialUpdateSchema,
    current_user: UserSchema = Depends(get_current_active_user),
    service: CredentialService = Depends(Factory().get_credential_service),
):
    """
    Update kredensial.

    Data sensitif bisa diupdate secara parsial. Field yang tidak disebutkan
    dalam data.sensitive_data tidak akan diubah.

    Endpoint ini hanya dapat diakses oleh admin.
    """
    updated = await service.update_credential(credential_id, data.dict(exclude_unset=True), current_user.id)
    return updated


@router.delete(
    "/credentials/{credential_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_active_user)],
)
async def delete_credential(
    credential_id: UUID, service: CredentialService = Depends(Factory().get_credential_service)
):
    await service.delete(credential_id)


# @router.post(
#     "/{credential_id}/test",
#     response_model=CredentialTestResult,
#     summary="Test koneksi menggunakan kredensial"
# )
# async def test_credential(
#     credential_id: UUID,
#     current_user: UserSchema = Depends(get_current_active_user),
#     service: CredentialService = Depends(Factory().get_credential_service)
# ):
#     """
#     Test koneksi menggunakan kredensial.

#     Hasil test berisi flag sukses dan detail tambahan.
#     """
#     result = await service.test_credential(
#         service.db, credential_id, current_user.id
#     )
#     return result


# @router.delete(
#     "/{credential_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
#     summary="Hapus kredensial"
# )
# async def delete_credential(
#     credential_id: UUID,
#     current_user: UserSchema = Depends(get_current_admin_user),
#     service: CredentialService = Depends(Factory().get_credential_service)
# ):
#     """
#     Hapus kredensial secara permanen.

#     Endpoint ini hanya dapat diakses oleh admin.
#     """
#     credential = await service.find_by_id(service.db, credential_id)
#     if not credential:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Credential not found"
#         )

#     await service.delete(service.db, credential_id)

#     return None
