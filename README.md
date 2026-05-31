
```shell
# https://docs.astral.sh/uv/getting-started/installation/ 
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

uv init -p 3.14

#安装fastapi
uv add fastapi uvicorn

```

```shell
# 1. 添加修改的文件
git add .

# 2. 提交修改
git commit -m "描述你做了什么修改"

# 3. 推送到 GitHub
git push
```