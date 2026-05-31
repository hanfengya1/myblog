from fastapi import APIRouter

router = APIRouter(prefix="/orders", tags=["订单相关接口"])

@router.get("/")
async def list_orders():
    return [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ]