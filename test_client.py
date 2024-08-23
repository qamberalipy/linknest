import pytest
from app.Client.service import (
    create_client,
    create_client_for_app,
    create_client_organization,
    create_client_membership,
    create_client_coach,
    get_client_organzation,
    generate_own_member_id,
    authenticate_client,
    login_client,
    get_client_by_email,
    get_business_clients,
    update_client,
    update_client_membership,
    update_client_coach,
    delete_client,
    get_list_clients,
    get_total_clients
)
from app.Client.schema import RegisterClient, RegisterClientApp, CreateClientOrganization, CreateClientMembership, ClientUpdate, ClientStatus
from app.Client.client import get_db
from sqlalchemy.orm import Session

# Helper function to get a database session
def get_test_db():
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()

@pytest.mark.asyncio
async def test_create_database():
    db = next(get_test_db())
    assert db is not None

@pytest.mark.asyncio
async def test_get_db():
    db = next(get_test_db())
    assert isinstance(db, Session)

@pytest.mark.asyncio
async def test_get_client_organization():
    db = next(get_test_db())
    email = "test@example.com"
    result = await get_client_organzation(email, db)
    assert result is not None

@pytest.mark.asyncio
async def test_generate_own_member_id():
    member_id = generate_own_member_id()
    assert len(member_id) == 13  # Assuming the generated ID is 13 characters long

@pytest.mark.asyncio
async def test_create_client():
    db = next(get_test_db())
    client_data = RegisterClient(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="1234567890",
        mobile_number="1234567890",
        password="yourpassword",
        own_member_id="JD123",
        gender="Male",
        dob="1990-01-01",
        created_by=1,
        updated_by=1
    )
    result = await create_client(client_data, db)
    assert result is not None

@pytest.mark.asyncio
async def test_create_client_for_app():
    db = next(get_test_db())
    client_data = RegisterClientApp(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="1234567890",
        mobile_number="1234567890",
        app_version="1.0.0",
        own_member_id="JD123",
        gender="Male",
        dob="1990-01-01"
    )
    result = await create_client_for_app(client_data, db)
    assert result is not None

@pytest.mark.asyncio
async def test_create_client_organization():
    db = next(get_test_db())
    client_org_data = CreateClientOrganization(
        client_id=59,
        org_id=9,
        client_status="active"
    )
    result = await create_client_organization(client_org_data, db)
    assert result is not None

@pytest.mark.asyncio
async def test_create_client_membership():
    db = next(get_test_db())
    client_membership_data = CreateClientMembership(
        client_id=59,
        membership_plan_id=1,
        auto_renewal=True,
        prolongation_period=12,
        auto_renew_days=30,
        inv_days_cycle=30
    )
    result = await create_client_membership(client_membership_data, db)
    assert result is not None

@pytest.mark.asyncio
async def test_create_client_coach():
    db = next(get_test_db())
    client_id = 59
    coach_ids = [1, 2]
    result = await create_client_coach(client_id, coach_ids, db)
    assert result is not None

@pytest.mark.asyncio
async def test_authenticate_client():
    db = next(get_test_db())
    email_address = "test@example.com"
    result = await authenticate_client(email_address, db)
    assert result is not None

@pytest.mark.asyncio
async def test_login_client():
    db = next(get_test_db())
    email_address = "test@example.com"
    wallet_address = "0x1234567890"
    result = await login_client(email_address, wallet_address, db)
    assert result is not None

@pytest.mark.asyncio
async def test_get_client_by_email():
    db = next(get_test_db())
    email_address = "shahzadfahad64@gmail.com"
    result = await get_client_by_email(email_address, db)
    assert result is not None

@pytest.mark.asyncio
async def test_get_business_clients():
    db = next(get_test_db())
    org_id = 9
    result = await get_business_clients(org_id, db)
    assert result is not None

@pytest.mark.asyncio
async def test_update_client():
    db = next(get_test_db())
    
    client_id = 59
    user_id = 55
    client_data = ClientUpdate(
        id=client_id,
        first_name="Jane",
        last_name="Doe",
        email="jane.doe@example.com",
        phone="1234567890",
        mobile_number="1234567890",
        org_id=9,  # Example organization ID
        client_status=ClientStatus.active # Example client status
    )
    
    result = await update_client(client_id, client_data, user_id, db)
    assert result is not None


@pytest.mark.asyncio
async def test_update_client_membership():
    db = next(get_test_db())
    
    # Assuming the membership_plan_id and client_id are valid
    client_id = 59
    membership_plan_id = 1
    
    # Create membership data
    membership_data = CreateClientMembership(
        client_id=client_id,
        membership_plan_id=membership_plan_id,
        auto_renewal=True,
        prolongation_period=12,
        auto_renew_days=30,
        inv_days_cycle=30
    )
    
    # Call the function with the created membership data
    result = await update_client_membership(membership_data, db)
    
    # Assertions to ensure the result is as expected
    assert result is not None
    assert result.client_id == client_id
    assert result.membership_plan_id == membership_plan_id
    assert result.auto_renewal == True
    assert result.prolongation_period == 12
    assert result.auto_renew_days == 30
    assert result.inv_days_cycle == 30

@pytest.mark.asyncio
async def test_update_client_coach():
    db = next(get_test_db())
    client_id = 59
    coach_ids = [1, 2]
    result = await update_client_coach(client_id, coach_ids, db)
    assert result is not None

@pytest.mark.asyncio
async def test_delete_client():
    db = next(get_test_db())
    client_id = 59
    user_id = 61  # Assuming there's a user_id to pass
    result = await delete_client(client_id, user_id, db)
    assert result is not None

@pytest.mark.asyncio
async def test_get_list_clients():
    db = next(get_test_db())
    org_id = 9
    result = get_list_clients(org_id, db)
    assert result is not None

@pytest.mark.asyncio
async def test_get_total_clients():
    db = next(get_test_db())
    org_id = 9
    result = await get_total_clients(org_id, db)
    assert result is not None
