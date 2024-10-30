import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from src.entity.models import Contact
from src.schemas.contacts import (
    ContactValidationSchemaResponse,
    ContactValidationSchema,
)


def has_birthday_next_days(sa_col, next_days: int = 0):
    return age_years_at(sa_col, next_days) > age_years_at(sa_col)


def age_years_at(sa_col, next_days: int = 0):
    stmt = func.age(
        (sa_col - sa.func.cast(datetime.timedelta(next_days), sa.Interval))
        if next_days != 0
        else sa_col
    )
    stmt = func.date_part("year", stmt)
    return stmt


async def read_all_contacts(
    limit: int,
    offset: int,
    name: str,
    last_name: str,
    email: str,
    find_BD,
    db: AsyncSession,
    user_id: int,
):
    stmt = select(Contact).offset(offset).limit(limit)
    stmt = stmt.filter_by(user_id=user_id)
    if name:
        stmt = stmt.filter_by(name=name)
    if last_name:
        stmt = stmt.filter_by(lastName=last_name)
    if email:
        stmt = stmt.filter_by(email=email)

    if find_BD:
        stmt = stmt.filter(has_birthday_next_days(Contact.birth_date, 7))
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def read_contact(contact_id: int, db: AsyncSession, user_id: int):
    stmt = select(Contact).filter_by(id=contact_id)
    stmt = stmt.filter_by(user_id=user_id)
    contact = await db.execute(stmt)

    return contact.scalar_one_or_none()


async def add_contact(body: ContactValidationSchema, db: AsyncSession, user_id):
    contact = Contact(**body.model_dump(exclude_unset=True), user_id=user_id)

    db.add(contact)
    await db.commit()
    await db.refresh(contact)

    return contact


async def update_contact(
    body: ContactValidationSchemaResponse, contact_id: int, db: AsyncSession, user_id
):
    stmt = select(Contact).filter_by(id=contact_id)
    stmt = stmt.filter_by(user_id=user_id)
    result = await db.execute(stmt)

    contact = result.scalar_one_or_none()
    if contact:
        contact.name = body.name
        contact.lastName = body.last_name
        contact.email = body.email
        contact.phoneNumber = body.phone_number
        contact.birthDate = body.birth_date
        contact.rest = body.rest
        await db.commit()
        await db.refresh(contact)

    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user_id):
    stmt = select(Contact).filter_by(id=contact_id)
    stmt = stmt.filter_by(user_id=user_id)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()

    if contact:
        await db.delete(contact)
        await db.commit()

    return contact
