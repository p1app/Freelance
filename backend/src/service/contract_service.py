from core.enums import ContractRoleUserEnum, ContractStatusEnum, ProposalStatusEnum
from core.exceptions import (
    BusinessError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)
from models.user_model import User as UserModel
from repository.contract_repo import ContractRepository
from repository.project_repo import ProjectRepository
from repository.proposal_repo import ProposalRepository
from repository.user_repo import UserRepository
from schemas.contract_schema import (
    ContractCreate,
    ContractDetailResponse,
    ContractResponse,
)
from schemas.pagination_schema import PaginatedResponse
from service.milestone_service import MilestonService
from sqlalchemy.ext.asyncio import AsyncSession


class ContractService:
    @classmethod
    async def create_contract(
        cls, session: AsyncSession, contract_data: ContractCreate
    ) -> ContractResponse:
        # Проверка, что отклик существует и принят
        proposal = await ProposalRepository.get_by_id(
            session=session, proposal_id=contract_data.proposal_id
        )
        if proposal is None:
            raise NotFoundError("Proposal not found")
        if proposal.status != ProposalStatusEnum.ACCEPTED:
            raise BusinessError("Only accepted proposals can create a contract")

        if contract_data.final_price <= 0:
            raise ValidationError("final_price must be greater than 0")

        contract = await ContractRepository.create(
            session=session, contract_data=contract_data
        )
        return ContractResponse.model_validate(contract)

    @classmethod
    async def get_contract(
        cls, session: AsyncSession, current_user: UserModel, contract_id: int
    ) -> ContractDetailResponse:
        contract = await ContractRepository.get_by_id(
            session=session, contract_id=contract_id
        )
        if contract is None:
            raise NotFoundError("Contract not found")

        if (
            current_user.id != contract.freelancer_id
            and current_user.id != contract.customer_id
        ):
            raise ForbiddenError("You do not have access to this contract")

        return ContractDetailResponse.model_validate(contract)

    @classmethod
    async def get_my_contracts(
        cls,
        session: AsyncSession,
        current_user: UserModel,
        role: ContractRoleUserEnum,
        status: ContractStatusEnum | None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse[ContractResponse]:
        contracts, total = await ContractRepository.list_by_user(
            session=session,
            user_id=current_user.id,
            role=role,
            status=status,
            page=page,
            page_size=page_size,
        )

        if not contracts:
            return PaginatedResponse(
                items=[],
                total=0,
                page=page,
                page_size=page_size,
                pages=0,
            )

        validate_data = [
            ContractResponse.model_validate(contract) for contract in contracts
        ]

        if total is None:
            raise ConflictError("total is none")

        return PaginatedResponse(
            items=validate_data,
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size,
        )

    @classmethod
    async def get_active_contracts(
        cls,
        session: AsyncSession,
        current_user: UserModel,
        role: ContractRoleUserEnum,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse[ContractResponse]:
        contracts, total = await ContractRepository.get_active_by_user(
            session=session,
            user_id=current_user.id,
            role=role,
            page=page,
            page_size=page_size,
        )

        if not contracts:
            return PaginatedResponse(
                items=[],
                total=0,
                page=page,
                page_size=page_size,
                pages=0,
            )

        validate_data = [
            ContractResponse.model_validate(contract) for contract in contracts
        ]

        if total is None:
            raise ConflictError("total is none")

        return PaginatedResponse(
            items=validate_data,
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size,
        )

    @classmethod
    async def complete_contract(
        cls, session: AsyncSession, current_user: UserModel, contract_id: int
    ) -> ContractResponse:
        contract = await ContractRepository.get_by_id(
            session=session, contract_id=contract_id
        )
        if contract is None:
            raise NotFoundError("Contract not found")
        if current_user.id != contract.customer_id:
            raise ForbiddenError(
                "It is impossible to complete a contract without being a customer"
            )
        if contract.status != ContractStatusEnum.ACTIVE:
            raise BusinessError(
                "The contract cannot be completed if the status is not active"
            )
        result = await MilestonService.check_all_approved(
            session=session, contract_id=contract_id
        )
        if not result:
            raise BusinessError(
                "You will not be able to complete into a contract until the status of all stages has been approved."
            )
        compeleted_contract = await ContractRepository.complete(
            contract_id, session=session
        )
        if compeleted_contract is None:
            raise ConflictError("new contract is none")
        await ProjectRepository.complete(
            session=session, project_id=contract.project_id
        )

        await UserRepository.increment_completed_projects(
            session=session, user_id=contract.freelancer_id
        )

        return ContractResponse.model_validate(compeleted_contract)

    @classmethod
    async def cancel_contract(
        cls,
        session: AsyncSession,
        current_user: UserModel,
        contract_id: int,
    ) -> ContractResponse:
        contract = await ContractRepository.get_by_id(
            session=session, contract_id=contract_id
        )
        if contract is None:
            raise NotFoundError("Contract not found")

        if (
            current_user.id != contract.customer_id
            and current_user.id != contract.freelancer_id
        ):
            raise ForbiddenError(
                "You cannot cancel a contract without being its creator or freelancer"
            )

        if contract.status != ContractStatusEnum.ACTIVE:
            raise BusinessError(
                "You cannot cancel a contract with status other than 'active'"
            )

        canceled_contract = await ContractRepository.cancel(
            session=session, contract_id=contract_id
        )
        return ContractResponse.model_validate(canceled_contract)
