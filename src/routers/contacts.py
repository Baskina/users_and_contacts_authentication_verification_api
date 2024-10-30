from fastapi import APIRouter, Depends, status, Path, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.schemas.contacts import (
    ContactValidationSchemaResponse,
    ContactValidationSchema,
)
from src.database.db import get_db

from src.repository import (
    contacts as repositories_contacts,
)
from src.services.auth import (
    auth_service,
)

routerContacts = APIRouter(prefix="/contacts", tags=["contacts"])


@routerContacts.get(
    "/",
    response_model=list[ContactValidationSchemaResponse],
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def read_all_contacts(
    limit: int = Query(default=10, ge=10, le=10),
    offset: int = Query(default=0, ge=0),
    name: str = Query(default=None),
    last_name: str = Query(default=None),
    email: str = Query(default=None),
    find_BD: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):

    contacts = await repositories_contacts.read_all_contacts(
        limit, offset, name, last_name, email, find_BD, db, current_user.id
    )
    return contacts


@routerContacts.get(
    "/{contact_id}",
    response_model=ContactValidationSchemaResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def read_contact(
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    contact = await repositories_contacts.read_contact(contact_id, db, current_user.id)

    return contact


@routerContacts.post(
    "/",
    response_model=ContactValidationSchemaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def add_contact(
    body: ContactValidationSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    contact = await repositories_contacts.add_contact(body, db, current_user.id)

    return contact


@routerContacts.put(
    "/{contact_id}", dependencies=[Depends(RateLimiter(times=1, seconds=20))]
)
async def update_contact(
    body: ContactValidationSchemaResponse,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    contact = await repositories_contacts.update_contact(
        body, contact_id, db, current_user.id
    )

    return contact


@routerContacts.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def delete_contact(
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    await repositories_contacts.delete_contact(contact_id, db, current_user.id)
