import json
from typing import Annotated

from core.database import get_db
from core.enums import ContractStatusEnum
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
from sqlalchemy.ext.asyncio import AsyncSession
from websocket.manager import ws_manager

router = APIRouter()


@router.websocket("/ws/chat/{contract_id}")
async def websocket_endpoint_token(
    websocket: WebSocket,
    Authorize: Annotated[JWTHarmonyWS[JWTUser], Depends(JWTHarmonyWebSocket)],
    db: Annotated[AsyncSession, Depends(get_db)],
    contract_id: int,
    token: str = Query(..., description="JWT access token"),
):
    try:
        # 1. Проверка токена
        Authorize.jwt_required(token)
        jwt_user = Authorize.user_claims

        if jwt_user is None:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

        # 2. Загрузка пользователя
        user: UserModel | None = await UserRepository.get_by_id(jwt_user.id, db)
        if user is None or not user.is_active:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

        # 3. Загрузка контракта
        contract = await ContractRepository.get_by_id(contract_id, db)
        if contract is None:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

        # 4. Проверка доступа
        if contract.customer_id != user.id and contract.freelancer_id != user.id:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

        # 5. Подключение
        await ws_manager.connect(contract_id, websocket)

        # 6. Цикл сообщений
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            text = data.get("message", "").strip()

            if not text:
                continue

            # Проверка активности контракта
            if contract.status != ContractStatusEnum.ACTIVE:
                await websocket.send_json(
                    {
                        "type": "error",
                        "detail": "Contract is not active",
                    }
                )
                continue

            # Сохранение
            message_data = await ChatRepository.create(
                MessageCreate(message=text),
                contract.id,
                user.id,
                db,
            )

            # Рассылка
            await ws_manager.broadcast(
                contract_id=contract_id,
                message=MessageResponse.model_validate(message_data),
            )

    except JWTHarmonyException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

    except WebSocketDisconnect:
        await ws_manager.disconnect(contract_id, websocket)

    except WebSocketException:
        await ws_manager.disconnect(contract_id, websocket)

    except Exception as e:  # noqa: BLE001
        print(f"WebSocket error: {e}")
        await ws_manager.disconnect(contract_id, websocket)
