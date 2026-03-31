#!/usr/bin/env bash
# =============================================================================
# deploy.sh — Script tự động build & triển khai Blog App
# OS: Ubuntu 24.04 LTS | Stack: Docker Compose + FastAPI + React + MySQL
# Cách dùng: ./scripts/deploy.sh [--rollback] [--skip-build]
# =============================================================================

set -euo pipefail

# ─── Màu sắc terminal ────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ─── Cấu hình ─────────────────────────────────────────────────────────────────
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${APP_DIR}/logs"
DEPLOY_LOG="${LOG_DIR}/deploy.log"
BACKUP_DIR="${APP_DIR}/.backups"
HEALTH_ENDPOINT="http://localhost:8000/health"
FRONTEND_ENDPOINT="http://localhost:80"
MONITORING_ENDPOINT="http://localhost:8080/api/health"
HEALTH_RETRIES=10
HEALTH_WAIT=5   # giây

# ─── Flags ─────────────────────────────────────────────────────────────────────
ROLLBACK=false
SKIP_BUILD=false
for arg in "$@"; do
  case $arg in
    --rollback)   ROLLBACK=true  ;;
    --skip-build) SKIP_BUILD=true ;;
  esac
done

# ─── Hàm tiện ích ─────────────────────────────────────────────────────────────
log()     { echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $*" | tee -a "${DEPLOY_LOG}"; }
success() { echo -e "${GREEN}[$(date '+%H:%M:%S')] ✅ $*${NC}" | tee -a "${DEPLOY_LOG}"; }
warn()    { echo -e "${YELLOW}[$(date '+%H:%M:%S')] ⚠️  $*${NC}" | tee -a "${DEPLOY_LOG}"; }
error()   { echo -e "${RED}[$(date '+%H:%M:%S')] ❌ $*${NC}" | tee -a "${DEPLOY_LOG}"; }
header()  { echo -e "\n${BOLD}${CYAN}══════════════════════════════════════════${NC}"; \
            echo -e "${BOLD}${CYAN}  $*${NC}"; \
            echo -e "${BOLD}${CYAN}══════════════════════════════════════════${NC}\n"; }

# ─── Khởi tạo thư mục ──────────────────────────────────────────────────────────
mkdir -p "${LOG_DIR}" "${BACKUP_DIR}"

# ─── Rollback mode ─────────────────────────────────────────────────────────────
if [ "${ROLLBACK}" = true ]; then
  header "🔄 ROLLBACK MODE"
  LAST_BACKUP=$(ls -t "${BACKUP_DIR}"/*.env 2>/dev/null | head -1)
  if [ -z "${LAST_BACKUP}" ]; then
    error "Không tìm thấy backup để rollback!"
    exit 1
  fi
  log "Khôi phục từ backup: ${LAST_BACKUP}"
  cp "${LAST_BACKUP}" "${APP_DIR}/.env"

  # Rollback Docker images
  for svc in blog_be blog_fe; do
    if docker image inspect "${svc}:rollback" &>/dev/null; then
      docker tag "${svc}:rollback" "${svc}:latest"
      log "Rollback image ${svc} thành công"
    fi
  done

  cd "${APP_DIR}"
  docker compose up -d --no-build
  success "Rollback hoàn tất!"
  exit 0
fi

# =============================================================================
header "🚀 BLOG APP DEPLOYMENT — $(date '+%Y-%m-%d %H:%M:%S')"
# =============================================================================

# ─── Bước 1: Kiểm tra môi trường ──────────────────────────────────────────────
log "Bước 1/7: Kiểm tra môi trường..."
cd "${APP_DIR}"

command -v docker >/dev/null 2>&1 || { error "Docker chưa được cài đặt!"; exit 1; }
command -v docker compose >/dev/null 2>&1 || command -v docker-compose >/dev/null 2>&1 \
  || { error "Docker Compose chưa được cài đặt!"; exit 1; }

DOCKER_VER=$(docker --version)
COMPOSE_VER=$(docker compose version 2>/dev/null || docker-compose --version)
log "  Docker: ${DOCKER_VER}"
log "  Compose: ${COMPOSE_VER}"

# Kiểm tra file .env
if [ ! -f "${APP_DIR}/.env" ]; then
  warn ".env không tồn tại, tạo từ .env.example..."
  if [ -f "${APP_DIR}/.env.example" ]; then
    cp "${APP_DIR}/.env.example" "${APP_DIR}/.env"
    error "⚠️ Vui lòng điền đầy đủ thông tin vào .env rồi chạy lại!"
    exit 1
  fi
fi

success "Môi trường OK"

# ─── Bước 2: Backup trạng thái hiện tại ────────────────────────────────────────
log "Bước 2/7: Tạo backup snapshot..."
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
BACKUP_FILE="${BACKUP_DIR}/${TIMESTAMP}.env"

cp "${APP_DIR}/.env" "${BACKUP_FILE}"

# Tag images cũ để rollback
for svc in blog_be blog_fe; do
  if docker image inspect "${svc}:latest" &>/dev/null; then
    docker tag "${svc}:latest" "${svc}:rollback"
    log "  Backup image: ${svc}:rollback"
  fi
done

# Giữ tối đa 5 bản backup
ls -t "${BACKUP_DIR}"/*.env 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null || true
success "Backup tại: ${BACKUP_FILE}"

# ─── Bước 3: Pull code mới nhất ────────────────────────────────────────────────
log "Bước 3/7: Cập nhật source code..."
CURRENT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
log "  Commit hiện tại: ${CURRENT_COMMIT}"

# Fetch để xem có gì mới
git fetch origin master --quiet 2>/dev/null || warn "Không thể fetch từ remote (deploy từ local)"

NEW_COMMIT=$(git rev-parse --short origin/master 2>/dev/null || echo "${CURRENT_COMMIT}")
log "  Commit mới nhất: ${NEW_COMMIT}"

success "Source code sẵn sàng"

# ─── Bước 4: Build Docker images ────────────────────────────────────────────────
if [ "${SKIP_BUILD}" = false ]; then
  log "Bước 4/7: Build Docker images..."
  BUILD_START=$(date +%s)

  docker compose build --no-cache --parallel 2>&1 | while IFS= read -r line; do
    echo "  [BUILD] ${line}" | tee -a "${DEPLOY_LOG}"
  done

  BUILD_END=$(date +%s)
  BUILD_TIME=$((BUILD_END - BUILD_START))
  success "Build hoàn tất trong ${BUILD_TIME}s"
else
  log "Bước 4/7: Bỏ qua build (--skip-build)"
fi

# ─── Bước 5: Deploy ───────────────────────────────────────────────────────────
log "Bước 5/7: Triển khai containers..."
DEPLOY_START=$(date +%s)

# Graceful shutdown — chờ request hiện tại xử lý xong
log "  Graceful shutdown services cũ..."
docker compose stop backend frontend 2>/dev/null || true
sleep 2

# Khởi động lại tất cả services
docker compose up -d --remove-orphans

DEPLOY_END=$(date +%s)
DEPLOY_TIME=$((DEPLOY_END - DEPLOY_START))
success "Containers đã khởi động trong ${DEPLOY_TIME}s"

# ─── Bước 6: Chạy Database Migration ───────────────────────────────────────────
log "Bước 6/7: Chạy database migration (Alembic)..."
sleep 5  # Chờ MySQL sẵn sàng

RETRY=0
MAX_RETRY=5
while [ $RETRY -lt $MAX_RETRY ]; do
  if docker compose exec -T backend alembic upgrade head 2>&1 | tee -a "${DEPLOY_LOG}"; then
    success "Migration hoàn tất"
    break
  else
    RETRY=$((RETRY + 1))
    warn "Migration thất bại, thử lại lần ${RETRY}/${MAX_RETRY}..."
    sleep 5
  fi
done

if [ $RETRY -eq $MAX_RETRY ]; then
  error "Migration thất bại sau ${MAX_RETRY} lần thử!"
  error "Đang rollback..."
  ./scripts/deploy.sh --rollback
  exit 1
fi

# ─── Bước 7: Health Check ─────────────────────────────────────────────────────
log "Bước 7/7: Kiểm tra sức khỏe hệ thống..."
chmod +x "${APP_DIR}/scripts/health-check.sh"
"${APP_DIR}/scripts/health-check.sh"
HEALTH_STATUS=$?

if [ $HEALTH_STATUS -ne 0 ]; then
  error "Health check thất bại! Đang rollback..."
  "${APP_DIR}/scripts/deploy.sh" --rollback
  exit 1
fi

# ─── Hoàn tất ─────────────────────────────────────────────────────────────────
TOTAL_TIME=$(( $(date +%s) - BUILD_START ))
header "🎉 DEPLOY THÀNH CÔNG"
echo -e "${GREEN}"
echo "  📦 Commit   : ${NEW_COMMIT}"
echo "  ⏱️  Thời gian : ${TOTAL_TIME}s"
echo "  🌐 Frontend  : http://localhost:80"
echo "  🔌 Backend   : http://localhost:8000"
echo "  📊 Dashboard : http://localhost:8080"
echo "  📝 Log deploy: ${DEPLOY_LOG}"
echo -e "${NC}"

# Ghi lịch sử deploy
echo "${TIMESTAMP}|${NEW_COMMIT}|success|${TOTAL_TIME}s" >> "${LOG_DIR}/deploy_history.log"

log "Deploy hoàn tất. Chúc mừng! 🎊"
