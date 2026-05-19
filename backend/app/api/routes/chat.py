from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(tags=["chat"])
DbSession = Annotated[AsyncSession, Depends(get_db_session)]


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    session: DbSession,
) -> ChatResponse:
    return await ChatService(session).chat(payload)
