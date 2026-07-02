# 打卡树一键部署脚本（Windows PowerShell）
# 用法:
#   .\deploy.ps1 dev      启动开发环境(热重载, 端口 8000, 前台)
#   .\deploy.ps1 test     启动测试环境(端口 8001, 后台)
#   .\deploy.ps1 prod     启动生产环境(端口 8080, 后台, 4 进程)
#   .\deploy.ps1 down     停止并移除所有环境的容器
#   .\deploy.ps1 logs     查看日志
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("dev", "test", "prod", "down", "logs")]
    [string]$Env
)

$base = "docker-compose.yml"

switch ($Env) {
    "dev"  { docker compose -f $base -f docker-compose.dev.yml up --build }
    "test" { docker compose -f $base -f docker-compose.test.yml up --build -d }
    "prod" {
        if (-not (Test-Path ".env.prod")) {
            Write-Host "缺少 .env.prod，请先复制模板并修改密钥：" -ForegroundColor Yellow
            Write-Host "  Copy-Item .env.prod.example .env.prod" -ForegroundColor Yellow
            return
        }
        docker compose -f $base -f docker-compose.prod.yml up --build -d
    }
    "down" {
        docker compose -f $base -f docker-compose.dev.yml -f docker-compose.test.yml -f docker-compose.prod.yml down
    }
    "logs" { docker compose logs -f }
}
