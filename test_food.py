import pytest
from app.Food.service import (
    create_food,
    get_food_by_id,
    update_food,
    delete_food,
    get_all_foods,
    get_food_by_org_id
)
from app.Food.schema import FoodCreate, FoodUpdate, FoodFilterParams
from app.Food.food import get_db
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
async def test_create_food():
    db = next(get_test_db())
    food_data = FoodCreate(
    org_id=9,
    name="Apple test",
    visible_for="only_me",
    brand="Brand A",
    category="cheese_eggs",  # Corrected value
    description="A fresh apple",
    total_nutrition=52.0,
    kcal=52.0,
    protein=0.3,
    fat=0.2,
    carbohydrates=14.0,
    created_by=1,
)
    user_id = 55
    result = await create_food(food_data, user_id, db)
    assert result is not None

@pytest.mark.asyncio
async def test_get_food_by_id():
    db = next(get_test_db())
    food_id = 40
    result = await get_food_by_id(food_id, db)
    assert result is not None

@pytest.mark.asyncio
async def test_update_food():
    db = next(get_test_db())
    food_id = 46
    user_id = 55
    food_data = FoodUpdate(
        id=food_id,
        name="Updated Apple",
        category="cheese_eggs",
        kcal=55.0,
        visible_for= "only_me"
    )
    result = await update_food(food_data, user_id, db)
    assert result is not None
    assert result.name == "Updated Apple"
    assert result.kcal == 55.0

@pytest.mark.asyncio
async def test_delete_food():
    db = next(get_test_db())
    food_id = 36
    result = await delete_food(food_id, db)
    assert result is not None

@pytest.mark.asyncio
async def test_get_all_foods():
    db = next(get_test_db())
    org_id = 9
    result = await get_all_foods(db, org_id)
    assert result is not None

@pytest.mark.asyncio
async def test_get_food_by_org_id():
    db = next(get_test_db())
    org_id = 9
    filter_params = FoodFilterParams(
        search_key="Apple test",
        category="cheese_eggs",
        sort_key="name",
        sort_order="asc",
        limit=10,
        offset=0
    )
    result = await get_food_by_org_id(db, org_id, filter_params)
    assert result is not None
    assert len(result['data']) > 0
