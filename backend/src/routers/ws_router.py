import json
from typing import Annotated

from core.database import get_db
from core.enums import ContractStatusEnum, NotificationTypeEnum
from core.security import JWTUser
from fastapi import (
    APIRouter,
    Depends,
    Query,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
    status,
)
from fastapi_jwt_harmony import JWTHarmonyException, JWTHarmonyWebSocket, JWTHarmonyWS
from models.user_model import User as UserModel
from repository.chat_repo import ChatRepository
from repository.contract_repo import ContractRepository
from repository.user_repo import UserRepository
from schemas.chat_schema import MessageCreate, MessageResponse
from schemas.notification_schema import (
    NotificationCreateMessage,
)
from service.notification_service import NotificationService
from sqlalchemy.ext.asyncio import AsyncSession
from websocket.chat_manager import ws_manager_chat
from websocket.notifications_manager import ws_manager_notifications

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/me")
async def ws_notificatons(
    websocket: WebSocket,
    Authorize: Annotated[JWTHarmonyWS[JWTUser], Depends(JWTHarmonyWebSocket)],
    db: Annotated[AsyncSession, Depends(get_db)],
    token: str = Query(..., description="JWT access token"),
):

    Authorize.jwt_required(token)
    jwt_user = Authorize.user_claims

    if jwt_user is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    user: UserModel | None = await UserRepository.get_by_id(jwt_user.id, db)
    if user is None or not user.is_active:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    await ws_manager_notifications.connect(user.id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except JWTHarmonyException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

    except WebSocketDisconnect:
        await ws_manager_notifications.disconnect(user.id, websocket)

    except WebSocketException:
        await ws_manager_notifications.disconnect(user.id, websocket)

    except Exception as e:  # noqa: BLE001
        print(f"WebSocket error: {e}")
        await ws_manager_notifications.disconnect(user.id, websocket)


@router.websocket("/ws/chat/{contract_id}")
async def websocket_endpoint_chat(
    websocket: WebSocket,
    Authorize: Annotated[JWTHarmonyWS[JWTUser], Depends(JWTHarmonyWebSocket)],
    db: Annotated[AsyncSession, Depends(get_db)],
    contract_id: int,
    token: str = Query(..., description="JWT access token"),
):
    try:
        Authorize.jwt_required(token)
        jwt_user = Authorize.user_claims

        if jwt_user is None:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

        user: UserModel | None = await UserRepository.get_by_id(jwt_user.id, db)
        if user is None or not user.is_active:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

        contract = await ContractRepository.get_by_id(contract_id, db)
        if contract is None:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

        if contract.customer_id != user.id and contract.freelancer_id != user.id:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

        await ws_manager_chat.connect(contract_id, websocket)

        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            text = data.get("message", "").strip()

            if not text:
                continue

            if contract.status != ContractStatusEnum.ACTIVE:
                await websocket.send_json(
                    {
                        "type": "error",
                        "detail": "Contract is not active",
                    }
                )
                continue

            message_data = await ChatRepository.create(
                MessageCreate(message=text),
                contract.id,
                user.id,
                db,
            )
            await NotificationService.create_for_contract(
                session=db,
                data=NotificationCreateMessage(
                    type=NotificationTypeEnum.MESSAGE,
                    to_user_id=user.id,
                    contract_id=contract.id,
                    description="Вам пришло новое сообщение",
                ),
            )
            await ws_manager_chat.broadcast(
                contract_id=contract_id,
                message=MessageResponse.model_validate(message_data),
            )

    except JWTHarmonyException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

    except WebSocketDisconnect:
        await ws_manager_chat.disconnect(contract_id, websocket)

    except WebSocketException:
        await ws_manager_chat.disconnect(contract_id, websocket)

    except Exception as e:  # noqa: BLE001
        print(f"WebSocket error: {e}")
        await ws_manager_chat.disconnect(contract_id, websocket)
