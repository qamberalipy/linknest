import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from app.Client import models, schema
from app.Client.service import (
    create_client,
    create_client_organization,
    create_client_membership,
    create_client_coach,
    authenticate_client,
    login_client,
    get_client_by_email,
    update_client,
    update_client_membership,
    update_client_coach,
    delete_client,
    get_filtered_clients,
    get_total_clients,
    get_list_clients,
    get_client_byid
)

# Mock the database session
@pytest.fixture
def db_session():
    session = MagicMock()
    yield session

@pytest.mark.asyncio
async def test_create_client(db_session):
    client_data = schema.RegisterClient(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        mobile_number="1234567890",
        # Add other fields as required
    )

    db_session.add = MagicMock()
    db_session.commit = MagicMock()
    db_session.refresh = MagicMock()

    result = await create_client(client_data, db_session)

    assert result.first_name == client_data.first_name
    assert result.last_name == client_data.last_name
    assert result.email == client_data.email
    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_create_client_organization(db_session):
    client_org_data = schema.CreateClientOrganization(
        client_id=1,
        org_id=2,
        client_status="active"
    )

    db_session.add = MagicMock()
    db_session.commit = MagicMock()
    db_session.refresh = MagicMock()

    result = await create_client_organization(client_org_data, db_session)

    assert result.client_id == client_org_data.client_id
    assert result.org_id == client_org_data.org_id
    assert result.client_status == client_org_data.client_status
    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_authenticate_client(db_session):
    db_session.query = MagicMock()
    db_session.query().filter().first.return_value = models.Client(
        email="john.doe@example.com"
    )

    result = await authenticate_client("john.doe@example.com", db_session)

    assert result.email == "john.doe@example.com"

@pytest.mark.asyncio
async def test_login_client(db_session):
    client = models.Client(
        id=1,
        email="john.doe@example.com",
        is_deleted=False
    )
    db_session.query = MagicMock()
    db_session.query().filter().first.return_value = client

    result = await login_client("john.doe@example.com", "wallet_address", db_session)

    assert result["is_registered"] is True
    assert result["client"]["email"] == client.email

@pytest.mark.asyncio
async def test_update_client(db_session):
    client_data = schema.ClientUpdate(
        first_name="John",
        last_name="Doe Updated",
        status="active",
        org_id=1
    )

    db_client = models.Client(id=1, first_name="John", last_name="Doe")
    db_client_status = models.ClientOrganization(client_id=1, org_id=1, client_status="inactive")

    db_session.query().filter().first.side_effect = [db_client, db_client_status]

    result = await update_client(1, client_data, db_session)

    assert result.last_name == "Doe Updated"
    assert db_client_status.client_status == "active"
    db_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_delete_client(db_session):
    db_client = models.Client(id=1, is_deleted=False)
    db_session.query().filter().first.return_value = db_client

    result = await delete_client(1, db_session)

    assert db_client.is_deleted is True
    assert result["status"] == "201"
    db_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_get_client_by_email(db_session):
    client = models.Client(id=1, email="john.doe@example.com")
    db_session.query().filter().first.return_value = client

    result = await get_client_by_email("john.doe@example.com", db_session)

    assert result.id == 1
    assert result.email == "john.doe@example.com"

@pytest.mark.asyncio
async def test_get_total_clients(db_session):
    db_session.query().join().filter().scalar.return_value = 10

    result = await get_total_clients(1, db_session)

    assert result == 10

@pytest.mark.asyncio
async def test_get_list_clients(db_session):
    clients = [
        models.Client(id=1, first_name="John", last_name="Doe"),
        models.Client(id=2, first_name="Jane", last_name="Smith"),
    ]
    db_session.query().join().filter().all.return_value = clients

    result = get_list_clients(1, db_session)

    assert len(result) == 2
    assert result[0].id == 1
    assert result[1].first_name == "Jane"

@pytest.mark.asyncio
async def test_get_filtered_clients(db_session):
    clients = [
        models.Client(id=1, first_name="John", last_name="Doe"),
        models.Client(id=2, first_name="Jane", last_name="Smith"),
    ]
    db_session.query().join().filter().group_by().offset().limit().all.return_value = clients

    params = schema.ClientFilterParams(
        offset=0,
        limit=10,
        member_name="John",
    )

    result = get_filtered_clients(db_session, 1, params)

    assert len(result["data"]) == 2
    assert result["data"][0].id == 1
    assert result["data"][1].first_name == "Jane"

@pytest.mark.asyncio
async def test_get_client_byid(db_session):
    client = models.Client(id=1, first_name="John", last_name="Doe")
    db_session.query().join().filter().group_by().first.return_value = client

    result = await get_client_byid(db_session, 1)

    assert result.id == 1
    assert result.first_name == "John"
