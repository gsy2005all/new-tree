# 容器化部署说明（Docker Compose 多环境）

基于 Docker Compose 实现**一键部署**，并用「基础文件 + 环境覆盖文件」的方式统一管理 **开发 / 测试 / 生产** 三套配置。

## 一、文件结构

| 文件 | 作用 |
|---|---|
| `Dockerfile` | 后端镜像（FastAPI + 静态前端） |
| `.dockerignore` | 构建镜像时排除 .venv / mobile / 密钥 / 日志等 |
| `docker-compose.yml` | **基础**：所有环境共用的服务定义、健康检查、数据卷写入 |
| `docker-compose.dev.yml` | 开发：挂载源码 + 热重载，端口 8000 |
| `docker-compose.test.yml` | 测试：独立数据卷与端口 8001 |
| `docker-compose.prod.yml` | 生产：4 进程、始终重启，端口 8080 |
| `.env.dev` / `.env.test` | 各环境变量（非敏感，已入库） |
| `.env.prod.example` | 生产环境变量模板（真实的 `.env.prod` 不入库） |
| `deploy.ps1` / `Makefile` | 一键启动脚本（Windows / Linux） |

设计要点：每个环境共用同一个基础镜像与服务骨架，差异（端口、命令、数据卷、变量文件）全部放在各自的覆盖文件里，避免重复、互不干扰，三套环境可同时运行。

## 二、一键启动

### Windows（PowerShell）
```powershell
.\deploy.ps1 dev      # 开发：热重载，前台，http://localhost:8000
.\deploy.ps1 test     # 测试：后台，http://localhost:8001
.\deploy.ps1 prod     # 生产：后台，http://localhost:8080
.\deploy.ps1 down     # 停止并清理所有环境
.\deploy.ps1 logs     # 看日志
```

### Linux / macOS 服务器
```bash
make dev | make test | make prod | make down | make logs
```

### 不想用脚本，直接用原生命令
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml  up --build       # 开发
docker compose -f docker-compose.yml -f docker-compose.test.yml up --build -d    # 测试
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d    # 生产
```

## 三、生产环境部署步骤

```bash
# 1) 准备生产环境变量（务必改密钥）
cp .env.prod.example .env.prod
python -c "import secrets; print(secrets.token_urlsafe(48))"   # 生成 JWT_SECRET 填进去

# 2) 启动
make prod      # 或 .\deploy.ps1 prod

# 3) 设置管理员（容器内执行）
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec api python manage.py set-admin <用户名>
```

## 四、说明与注意

- **数据持久化**：数据库写在各环境独立的命名卷（`dev-db` / `test-db` / `prod-db`）里，容器重建数据不丢。数据库路径由环境变量 `DB_FILE` 控制（容器内为 `/app/data/database.db`）。
- **密钥安全**：`.env`、`.env.prod` 已在 `.gitignore` 中，不会上传；生产请用 `.env.prod.example` 复制后修改。
- **健康检查**：基础文件对 `/app/version` 做 healthcheck，`docker compose ps` 可看到健康状态。
- **关于数据库**：当前为 SQLite，适合中小流量；生产高并发写入建议改用 PostgreSQL（需要相应改 `db/db.py` 的连接串，并在 compose 里加一个 `db` 服务）。
- **移动端 (mobile/)** 是 Expo 开发工具，不进服务端镜像；它通过 WebView 访问本服务的网页。
- 本机未安装 Docker 时，先安装 Docker Desktop（Windows）或 Docker Engine（Linux）。
