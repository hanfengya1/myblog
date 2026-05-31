from fastapi import FastAPI
from routers.users import router as users_router
from routers.orders import router as orders_router

# 创建 FastAPI 实例
app = FastAPI()

# 注册路由
app.include_router(users_router,prefix="/api")
app.include_router(orders_router,prefix="/api")

@app.get("/")
async def root():
    return {"message": "Hello FastAPI"} 

if __name__ == "__main__":
    # 启动服务
    import uvicorn
    uvicorn.run(app, host="0.0.0.0",port=8000)
