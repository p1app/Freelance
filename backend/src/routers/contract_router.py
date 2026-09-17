from typing import Annotated

from core.database import get_db
from core.enums import ContractRoleUserEnum, ContractStatusEnum, RoleEnum
from core.exceptions import BusinessError
from core.security import get_current_user
from fastapi import APIRouter, Depends, Query, status
from models.user_model import User as UserModel
from schemas.contract_schema import ContractDetailResponse, ContractResponse
from schemas.pagination_schema import PaginatedResponse
from service.contract_service import ContractService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.get(
    path="/me",
    response_model=PaginatedResponse[ContractResponse],
    status_code=status.HTTP_200_OK,
)
async def get_my_contracts(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
    status_filter: Annotated[ContractStatusEnum | None, Query(alias="status")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[ContractResponse]:
    # Автоматически определяем сторону в контракте
    if current_user.role == RoleEnum.CLIENT:
        contract_role = ContractRoleUserEnum.CUSTOMER
    elif current_user.role == RoleEnum.FREELANCER:
        contract_role = ContractRoleUserEnum.FREELANCER
    else:
        raise BusinessError("Admin cannot have contracts")

    return await ContractService.get_my_contracts(
        session=db,
        current_user=current_user,
        role=contract_role,
        status=status_filter,
        page=page,
        page_size=page_size,
    )


@router.get(
    path="/{contract_id}",
    response_model=ContractDetailResponse,
    status_code=status.HTTP_200_OK,
)
async def get_contract(
    contract_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> ContractDetailResponse:
    return await ContractService.get_contract(
        session=db,
        current_user=current_user,
        contract_id=contract_id,
    )


@router.patch(
    path="/{contract_id}/complete",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK,
)
async def complete_contract(
    contract_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> ContractResponse:
    return await ContractService.complete_contract(
        session=db,
        current_user=current_user,
        contract_id=contract_id,
    )


@router.patch(
    path="/{contract_id}/cancel",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK,
)
async def cancel_contract(
    contract_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> ContractResponse:
    return await ContractService.cancel_contract(
        session=db,
        current_user=current_user,
        contract_id=contract_id,
    )
