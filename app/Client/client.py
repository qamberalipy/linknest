from typing import Annotated, List, Optional
from fastapi import Header,FastAPI, APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.exc import IntegrityError, DataError
import app.Client.schema as _schemas
import sqlalchemy.orm as _orm
import app.Client.models as _models
import app.Client.service as _services
import app.Client.schema as _schemas
from app.Shared.dependencies import get_user
import app.user.service as _user_service
import app.Shared.helpers as _helpers
# from main import logger
import app.core.db.session as _database
import pika
import logging
import datetime
from app.Client.models import ClientStatus
from app.Shared.schema import SharedCreateSchema,SharedModifySchema

router = APIRouter()

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler())


def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.post("/member", response_model=SharedCreateSchema, tags=["Member Router"])
async def register_client(
    client: _schemas.ClientCreate, 
    request: Request, 
    db: _orm.Session = Depends(get_db)
):
    try:
        if not _helpers.validate_email(client.email):
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        user_id = request.state.user.get('id')
        client_data = client.dict()
        
        # Extracting fields from client_data
        organization_id = client_data.pop('org_id')
        status = client_data.pop('client_status')
        coach_ids = client_data.pop('coach_id', [])
        membership_id = client_data.pop('membership_plan_id')
        prolongation_period = client_data.pop('prolongation_period')
        auto_renew_days = client_data.pop('auto_renew_days')
        inv_days_cycle = client_data.pop('inv_days_cycle')
        auto_renewal = client_data.pop('auto_renewal')
        own_member_id = client_data.pop('own_member_id')
        
        # Setting audit fields
        client_data.update({
            'created_by': user_id,
            'updated_by': user_id,
            'created_at': datetime.datetime.now(),
            'updated_at': datetime.datetime.now(),
        })

        # Check if client already exists
        db_client = await _services.get_client_by_email(client.email, db)
        
        if db_client:
            if organization_id in db_client.org_ids:
                logger.info("Client exists within the same organization")
                raise HTTPException(status_code=400, detail="Email already registered")
            else:
                logger.info("Client does not exist within the same organization")
                updated_client = await _services.update_app_client(db_client.id, client, db)
                
                # Create new associations for the existing client
                await _services.create_client_organization(
                    _schemas.CreateClientOrganization(
                        client_id=updated_client.id, org_id=organization_id, 
                        client_status=status, own_member_id=own_member_id
                    ), db
                )

                await _services.create_client_membership(
                    _schemas.CreateClientMembership(
                        client_id=updated_client.id, membership_plan_id=membership_id,
                        auto_renewal=auto_renewal, prolongation_period=prolongation_period, 
                        auto_renew_days=auto_renew_days, inv_days_cycle=inv_days_cycle
                    ), db
                )

                if coach_ids:
                    await _services.create_client_coach(updated_client.id, coach_ids, db)

                return {
                    "status_code": "201",
                    "id": updated_client.id,
                    "message": "Member created successfully"
                }

        # If client does not exist, create a new one
        logger.info("Creating a new client")
        new_client = await _services.create_client(_schemas.RegisterClient(**client_data), db)
        
        # Create associations for the new client
        await _services.create_client_organization(
                    _schemas.CreateClientOrganization(
                        client_id=new_client.id, org_id=organization_id, 
                        client_status=status, own_member_id=own_member_id
                    ), db
        )

        await _services.create_client_membership(
            _schemas.CreateClientMembership(
                client_id=new_client.id, membership_plan_id=membership_id,
                auto_renewal=auto_renewal, prolongation_period=prolongation_period, 
                auto_renew_days=auto_renew_days, inv_days_cycle=inv_days_cycle
            ), db
        )

        if coach_ids:
            await _services.create_client_coach(new_client.id, coach_ids, db)

        return {
            "status_code": "201",
            "id": new_client.id,
            "message": "Member created successfully"
        }

    except IntegrityError as e:
        db.rollback()
        logger.error(f"IntegrityError: {e}")
        raise HTTPException(status_code=400, detail="Duplicate entry or integrity constraint violation")
        
    except DataError as e:
        db.rollback()
        logger.error(f"DataError: {e}")
        raise HTTPException(status_code=400, detail="Data error occurred, check your input")



    
@router.put("/member",response_model = _schemas.ClientUpdate, tags=["Member Router"])
async def update_client(client: _schemas.ClientUpdate,request:Request, db: _orm.Session = Depends(get_db)):
    try:

        user_id=request.state.user.get('id')
        updated_client = await _services.update_client(client.id, client,user_id,db)
        
        if client.membership_plan_id is not None:
            membership = _schemas.ClientMembership(
            client_id=client.id,
            membership_plan_id=client.membership_plan_id,
            auto_renewal=client.auto_renewal,
            prolongation_period=client.prolongation_period,
            auto_renew_days=client.auto_renew_days,
            inv_days_cycle=client.inv_days_cycle
            )
            await _services.update_client_membership(membership, db)

        if client.coach_id:
            await _services.update_client_coach(client.id, client.coach_id, db)
        
        return updated_client

    except IntegrityError as e:
        db.rollback()
        logger.error(f"IntegrityError: {e}")
        raise HTTPException(status_code=400, detail="Duplicate entry or integrity constraint violation")

    except DataError as e:
        db.rollback()
        logger.error(f"DataError: {e}")
        raise HTTPException(status_code=400, detail="Data error occurred, check your input")
    

@router.delete("/member/{id}",response_model=SharedModifySchema, tags=["Member Router"])
async def delete_client(id:int,org_id: Annotated[int, Query(title="Organization id")],request:Request,db: _orm.Session = Depends(get_db)):
    try:
        # user_id=request.state.user.get('id')
        deleted_client = await _services.delete_client(id,org_id,db)
        return deleted_client

    except IntegrityError as e:
        db.rollback()
        logger.error(f"IntegrityError: {e}")
        raise HTTPException(status_code = 400, detail="Integrity constraint violation")

    except DataError as e:
        db.rollback()
        logger.error(f"DataError: {e}")
        raise HTTPException(status_code = 400, detail="Data error occurred, check your input")

@router.get("/member/{id}", response_model=_schemas.ClientByID, tags=["Member Router"])
async def get_client_by_id(id: int,org_id: Annotated[int, Query(title="Organization id")], db:  _orm.Session = Depends(get_db)):
    try:    
        client = await _services.get_client_byid(db=db, client_id=id,org_id=org_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        return client    
    
    except IntegrityError as e:
        logger.error(f"IntegrityError: {e}")
        raise HTTPException(status_code=400, detail="Integrity error occurred")
    except DataError as e:
        logger.error(f"DataError: {e}")
        raise HTTPException(status_code=400, detail="Data error occurred, check your input")


def get_filters(

    search_key: Annotated[str | None, Query(title="Search Key")] = None,
    member_name: Annotated[str, Query(description="Member First/Last Name")] = None,
    status: Annotated[ClientStatus | None, Query(title="status")] = None,
    coach_assigned: Annotated[int, Query(description="Coach ID")] = None,
    membership_plan: Annotated[int, Query(description="Membership ID")] = None,
    sort_order: Annotated[str,Query(title="Sorting Order")] = 'desc',
    sort_key:Annotated[str,Query(title="Sort Key")] =None,
    limit: Annotated[int, Query(description="Pagination Limit")] = None,
    offset: Annotated[int, Query(description="Pagination offset")] = None
):
    return _schemas.ClientFilterParams(
        search_key=search_key,
        member_name=member_name,
        status=status,
        coach_assigned=coach_assigned,
        membership_plan=membership_plan,
        sort_order = sort_order,
        sort_key = sort_key,
        limit=limit,
        offset = offset
    )

@router.get("/member",tags=["Member Router"])
async def get_client( 
    org_id: Annotated[int, Query(title="Organization id")],
    filters: Annotated[_schemas.ClientFilterParams, Depends(get_filters)] = None,
    db: _orm.Session = Depends(get_db)):

    try:
        clients = _services.get_filtered_clients(db=db,org_id=org_id,params=filters)

        if clients:
            return clients
        else:
            raise HTTPException(status_code=404, detail="No clients found")

    except IntegrityError as e:
        logger.error(f"IntegrityError: {e}")
        raise HTTPException(status_code=400, detail="Integrity error occurred")
    except DataError as e:
        logger.error(f"DataError: {e}")
        raise HTTPException(status_code=400, detail="Data error occurred, check your input")

@router.get("/member/list/{org_id}", response_model=List[_schemas.ClientList], tags=["Member Router"])
async def get_client_list(org_id: int,db: _orm.Session = Depends(get_db)):
    
    try:
        clients = _services.get_list_clients(org_id=org_id, db=db)
        
        if clients:
            return clients
        else:
            raise HTTPException(status_code=404, detail="Client not found")

    except IntegrityError as e:
        logger.error(f"IntegrityError: {e}")
        raise HTTPException(status_code=400, detail="Integrity error occurred")
    except DataError as e:
        logger.error(f"DataError: {e}")
        raise HTTPException(status_code=400, detail="Data error occurred, check your input")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

    

@router.get("/member/business/{org_id}", response_model=List[_schemas.ClientBusinessRead], tags=["Member Router"])
async def get_business_clients(org_id: int,db: _orm.Session = Depends(get_db)):
    try:
        
        clients = await _services.get_business_clients(org_id, db)
        if not clients:
            return []
        return clients
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    

@router.get("/member/count/{org_id}", response_model=_schemas.ClientCount, tags=["Member Router"])
async def get_total_clients(org_id: int, db: _orm.Session = Depends(get_db)):
    try:
        
        total_clients = await _services.get_total_clients(org_id, db)
        return {"total_members": total_clients}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
