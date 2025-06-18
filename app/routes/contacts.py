from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.db import get_db
from app.models.models import Contact
from app.schemas.schemas import ContactCreate, ContactResponse, ContactUpdate
from app.services.auth import auth_service

router = APIRouter(
    prefix="/api/contacts",
    tags=["Contacts"]
)


@router.post(
    "/",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_contact(
    payload: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(auth_service.get_current_user)
):
    new_contact = Contact(**payload.dict(), user_id=current_user.id)
    db.add(new_contact)
    await db.commit()
    await db.refresh(new_contact)
    return new_contact


@router.get(
    "/",
    response_model=List[ContactResponse]
)
async def read_contacts(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(auth_service.get_current_user)
):
    result = await db.execute(
        select(Contact).where(Contact.user_id == current_user.id)
    )
    return result.scalars().all()


@router.get(
    "/{contact_id}",
    response_model=ContactResponse
)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(auth_service.get_current_user)
):
    result = await db.execute(
        select(Contact)
        .where(Contact.id == contact_id, Contact.user_id == current_user.id)
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    return contact


@router.get(
    "/search",
    response_model=List[ContactResponse]
)
async def search_contacts(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(auth_service.get_current_user)
):
    query = select(Contact).where(Contact.user_id == current_user.id)
    if first_name:
        query = query.where(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.where(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.where(Contact.email.ilike(f"%{email}%"))

    result = await db.execute(query)
    return result.scalars().all()


@router.get(
    "/upcoming_birthdays",
    response_model=List[ContactResponse]
)
async def upcoming_birthdays(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(auth_service.get_current_user)
):
    today = datetime.today().date()
    in_seven = today + timedelta(days=7)

    result = await db.execute(
        select(Contact).where(Contact.user_id == current_user.id)
    )
    all_contacts = result.scalars().all()

    upcoming = []
    for c in all_contacts:
        if c.birthday:
            this_year = c.birthday.replace(year=today.year)
            if today <= this_year <= in_seven:
                upcoming.append(c)
    return upcoming


@router.put(
    "/{contact_id}",
    response_model=ContactResponse
)
async def update_contact(
    contact_id: int,
    payload: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(auth_service.get_current_user)
):
    result = await db.execute(
        select(Contact)
        .where(Contact.id == contact_id, Contact.user_id == current_user.id)
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    if payload.email:
        dup = await db.execute(
            select(Contact)
            .where(
                Contact.email == payload.email,
                Contact.id != contact_id,
                Contact.user_id == current_user.id
            )
        )
        if dup.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(contact, field, value)

    await db.commit()
    await db.refresh(contact)
    return contact


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(auth_service.get_current_user)
):
    result = await db.execute(
        select(Contact)
        .where(Contact.id == contact_id, Contact.user_id == current_user.id)
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    await db.delete(contact)
    await db.commit()
