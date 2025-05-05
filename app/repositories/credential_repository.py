from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi_async_sqlalchemy import db
from pytz import timezone
from sqlalchemy import select, update
from uuid6 import UUID

from app.core.config import settings
from app.models import CredentialModel

from . import BaseRepository


class CredentialRepository(BaseRepository[CredentialModel]):
    def __init__(self, model):
        super().__init__(model)

    async def create(self, data: Dict[str, Any]):
        credential = await super().create(data)
        if credential.is_default:
            await self.set_default(credential.id, credential.created_by)

        return credential

    async def get_by_type(self, credential_type: str, is_active: bool = True) -> List[CredentialModel]:
        """
        Mendapatkan semua kredensial berdasarkan tipe.

        Args:
            credential_type: Tipe kredensial ('database', 'api', 'minio', dll)
            is_active: Filter berdasarkan status aktif

        Returns:
            List dari credential models
        """
        query = select(self.model).where(self.model.credential_type == credential_type)

        if is_active is not None:
            query = query.where(self.model.is_active == is_active)

        query = query.order_by(self.model.created_at.desc())
        result = await db.session.execute(query)
        return result.scalars().all()

    async def get_default_by_type(self, credential_type: str, is_active: bool = True) -> Optional[CredentialModel]:
        """
        Mendapatkan kredensial default berdasarkan tipe.

        Args:
            credential_type: Tipe kredensial ('database', 'api', 'minio', dll)
            is_active: Filter berdasarkan status aktif

        Returns:
            Credential model atau None jika tidak ditemukan
        """
        query = select(self.model).where(self.model.credential_type == credential_type, self.model.is_default == True)

        if is_active is not None:
            query = query.where(self.model.is_active == is_active)

        result = await db.session.execute(query)
        return result.scalars().first()

    async def set_default(self, credential_id: UUID, updated_by: UUID) -> bool:
        """
        Set kredensial sebagai default untuk tipenya, dan unset default
        untuk kredensial lain dengan tipe yang sama.

        Args:
            credential_id: ID kredensial yang akan dijadikan default
            updated_by: ID user yang melakukan update

        Returns:
            Boolean yang menunjukkan keberhasilan operasi
        """
        # Dapatkan kredensial yang akan diset sebagai default
        cred = await self.find_by_id(credential_id)
        if not cred:
            return False

        # Reset default flag untuk semua kredensial dengan tipe yang sama
        reset_query = (
            update(self.model)
            .where(self.model.credential_type == cred.credential_type)
            .values(is_default=False, updated_by=updated_by)
        )
        await db.session.execute(reset_query)

        # Set sebagai default
        set_query = (
            update(self.model).where(self.model.id == credential_id).values(is_default=True, updated_by=updated_by)
        )
        await db.session.execute(set_query)
        await db.session.commit()

        return True

    async def update_last_used(self, credential_id: UUID, user_id: UUID) -> bool:
        """
        Update timestamp penggunaan terakhir.

        Args:
            db: Database session
            credential_id: ID kredensial yang digunakan
            user_id: ID user yang menggunakan

        Returns:
            Boolean yang menunjukkan keberhasilan operasi
        """
        update_query = (
            update(self.model)
            .where(self.model.id == credential_id)
            .values(last_used_at=datetime.now(timezone(settings.TIMEZONE)), last_used_by=user_id)
        )

        await db.session.execute(update_query)
        await db.session.commit()

        return True
