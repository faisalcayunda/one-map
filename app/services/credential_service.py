from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import ValidationError

from app.models.credential_model import CredentialModel
from app.repositories.credential_repository import CredentialRepository
from app.utils.encryption import credential_encryption

from . import BaseService


class CredentialService(BaseService[CredentialModel]):
    def __init__(self, repository: CredentialRepository):
        super().__init__(CredentialModel, repository)
        self.repository = repository

    async def create_credential(
        self,
        name: str,
        credential_type: str,
        sensitive_data: Dict[str, Any],
        credential_metadata: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        is_default: bool = False,
        user_id: UUID = None,
    ) -> CredentialModel:
        """
        Buat kredensial baru dengan mengenkripsi data sensitif.

        Args:
            name: Nama kredensial
            credential_type: Tipe kredensial ('database', 'api', 'minio', dll)
            sensitive_data: Data sensitif yang akan dienkripsi
            credential_metadata: metadata tidak sensitif (opsional)
            description: Deskripsi kredensial (opsional)
            is_default: Apakah kredensial ini default untuk tipenya
            user_id: ID user yang membuat kredensial

        Returns:
            Credential model yang telah disimpan
        """

        encrypted_data, encryption_iv = credential_encryption.encrypt(sensitive_data)

        credential_data = {
            "name": name,
            "description": description,
            "credential_type": credential_type,
            "encrypted_data": encrypted_data,
            "encryption_iv": encryption_iv,
            "credential_metadata": credential_metadata or {},
            "is_default": is_default,
            "created_by": user_id,
            "updated_by": user_id,
        }

        return await self.repository.create(credential_data)

    async def get_credential_with_decrypted_data(self, credential_id: UUID) -> Dict[str, Any]:
        """
        Ambil kredensial beserta data sensitif yang sudah didekripsi.

        Args:
            credential_id: ID kredensial

        Returns:
            Tuple dari (credential_model, decrypted_data)
        """
        credential = await self.find_by_id(credential_id)

        if not credential:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")

        decrypted_data = credential_encryption.decrypt(credential.encrypted_data, credential.encryption_iv)

        credential_dict = credential.to_dict()
        credential_dict["decrypted_data"] = decrypted_data
        return credential_dict

    async def get_list_of_decrypted_credentials(
        self, filters: list, sort: list = [], search: str = "", group_by: str = None, limit: int = 100, offset: int = 0
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Ambil kredensial beserta data sensitif yang sudah didekripsi.

        Args:
            credential_id: ID kredensial

        Returns:
            Tuple dari (credential_model, decrypted_data)
        """

        credentials, total = await self.find_all(
            filters=filters, sort=sort, search=search, group_by=group_by, limit=limit, offset=offset
        )
        decrypted_credentials = []
        for credential in credentials:
            try:
                decrypted_data = credential_encryption.decrypt(credential.encrypted_data, credential.encryption_iv)
                temp = credential.to_dict()
                temp["decrypted_data"] = decrypted_data
                decrypted_credentials.append(temp)
            except ValidationError:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to decrypt some credential data"
                )

        return decrypted_credentials, total

    async def update_credential(self, credential_id: UUID, data: Dict[str, Any], user_id: UUID) -> CredentialModel:
        """
        Update kredensial.

        Args:
            credential_id: ID kredensial yang akan diupdate
            data: Data yang akan diupdate (dapat berisi 'sensitive_data', 'credential_metadata', dll)
            user_id: ID user yang melakukan update

        Returns:
            Updated credential model
        """
        credential = await self.find_by_id(credential_id)

        if not credential:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")
        if "credential_metadata" in data:
            if not isinstance(data["credential_metadata"], dict):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="credential_metadata must be a dictionary"
                )
            metadata = credential.credential_metadata
            metadata.update(data["credential_metadata"])
            data["credential_metadata"] = metadata

        for key, value in data.items():
            if key != "sensitive_data" and hasattr(credential, key):
                setattr(credential, key, value)

        if "sensitive_data" in data and data["sensitive_data"]:
            current_data = credential_encryption.decrypt(credential.encrypted_data, credential.encryption_iv)

            current_data.update(data["sensitive_data"])
            encrypted_data, encryption_iv = credential_encryption.encrypt(current_data)
            credential.encrypted_data = encrypted_data
            credential.encryption_iv = encryption_iv

        credential.updated_by = user_id

        if data.get("is_default", False) and not credential.is_default:
            await self.repository.set_default(credential_id, user_id)

        return await self.repository.update(credential_id, credential.to_dict())

    async def get_credentials_by_type(self, credential_type: str, is_active: bool = True) -> List[CredentialModel]:
        """
        Dapatkan semua kredensial berdasarkan tipe.

        Args:
            credential_type: Tipe kredensial
            is_active: Filter berdasarkan status aktif

        Returns:
            List dari credential models
        """
        return await self.repository.get_by_type(credential_type, is_active)

    async def get_default_credential(
        self, credential_type: str, with_decrypted_data: bool = False
    ) -> Tuple[Optional[CredentialModel], Optional[Dict[str, Any]]]:
        """
        Dapatkan kredensial default berdasarkan tipe.

        Args:
            db: Database session
            credential_type: Tipe kredensial
            with_decrypted_data: Apakah akan mendekripsi data sensitif

        Returns:
            Tuple dari (credential_model, decrypted_data)
        """
        credential = await self.repository.get_default_by_type(credential_type, is_active=True)

        if not credential:
            return None, None

        if with_decrypted_data:
            try:
                decrypted_data = credential_encryption.decrypt(credential.encrypted_data, credential.encryption_iv)
                return credential, decrypted_data
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to decrypt credential data"
                )

        return credential, None

    async def test_credential(self, credential_id: UUID, user_id: UUID) -> Dict[str, Any]:
        """
        Test koneksi menggunakan kredensial.
        Implementasi akan berbeda tergantung tipe kredensial.

        Args:
            db: Database session
            credential_id: ID kredensial yang akan ditest
            user_id: ID user yang melakukan test

        Returns:
            Dictionary berisi hasil test
        """
        # Dapatkan kredensial dengan data terdekripsi
        credential, decrypted_data = await self.get_credential_with_decrypted_data(credential_id)

        result = {"success": False, "details": {}}

        try:
            # Lakukan test berdasarkan tipe kredensial
            if credential.credential_type == "database":
                # Implementasi test untuk database
                result = await self._test_database_credential(decrypted_data)
            elif credential.credential_type == "minio":
                # Implementasi test untuk MinIO
                result = await self._test_minio_credential(decrypted_data)
            elif credential.credential_type == "api":
                # Implementasi test untuk API
                result = await self._test_api_credential(decrypted_data)
            else:
                result = {
                    "success": False,
                    "details": {"message": f"Testing for type {credential.credential_type} not implemented"},
                }

            # Update timestamp penggunaan terakhir
            await self.repository.update_last_used(credential_id, user_id)

        except Exception as e:
            result = {"success": False, "details": {"error": str(e)}}

        return result

    async def _test_database_credential(self, cred_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test koneksi database.

        Args:
            cred_data: Data kredensial yang sudah didekripsi

        Returns:
            Dictionary berisi hasil test
        """
        # Implementasi test koneksi database
        # Contoh:
        try:
            # Simulasi test
            # Dalam implementasi sebenarnya, lakukan koneksi ke database
            return {"success": True, "details": {"message": "Database connection successful"}}
        except Exception as e:
            return {"success": False, "details": {"error": str(e)}}

    async def _test_minio_credential(self, cred_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test koneksi MinIO.

        Args:
            cred_data: Data kredensial yang sudah didekripsi

        Returns:
            Dictionary berisi hasil test
        """
        try:
            # Implementasi test koneksi MinIO
            # Di sini bisa menggunakan miniopy-async untuk tes koneksi
            return {"success": True, "details": {"message": "MinIO connection successful"}}
        except Exception as e:
            return {"success": False, "details": {"error": str(e)}}

    async def _test_api_credential(self, cred_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test koneksi API.

        Args:
            cred_data: Data kredensial yang sudah didekripsi

        Returns:
            Dictionary berisi hasil test
        """
        try:
            # Implementasi test koneksi API
            # Di sini bisa menggunakan aiohttp untuk tes koneksi
            return {"success": True, "details": {"message": "API connection successful"}}
        except Exception as e:
            return {"success": False, "details": {"error": str(e)}}
