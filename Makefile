# 打卡树一键部署（Linux/macOS 服务器，需要 make 与 docker compose）
# 用法: make dev / make test / make prod / make down / make logs

BASE := docker-compose.yml

.PHONY: dev test prod down logs build ps

dev:
	docker compose -f $(BASE) -f docker-compose.dev.yml up --build

test:
	docker compose -f $(BASE) -f docker-compose.test.yml up --build -d

prod:
	@test -f .env.prod || (echo "缺少 .env.prod，请先: cp .env.prod.example .env.prod 并修改密钥"; exit 1)
	docker compose -f $(BASE) -f docker-compose.prod.yml up --build -d

down:
	docker compose -f $(BASE) -f docker-compose.dev.yml -f docker-compose.test.yml -f docker-compose.prod.yml down

logs:
	docker compose logs -f

build:
	docker compose -f $(BASE) -f docker-compose.dev.yml build

ps:
	docker compose ps
