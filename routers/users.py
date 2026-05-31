from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["用户相关接口"])

@router.get("/") 
async def list_users():
    return [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
    ]

@router.get("/{id}") 
async def get_user(id: int):
    return "查询单个用户"

@router.post("/") 
async def create_user():
    return "创建用户"

@router.put("/{id}") 
async def update_user():
    return "修改用户"

@router.delete("/{id}") 
async def delete_user(id: int):
    return "删除用户"