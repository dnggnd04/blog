#!/usr/bin/env bash
# =============================================================================
# setup-runner.sh — Cài đặt GitHub Actions Self-hosted Runner trên Ubuntu 24.04
# Chạy 1 lần trên Proxmox VM sau khi SSH vào máy
# Cách dùng: sudo ./scripts/setup-runner.sh
# =============================================================================

set -euo pipefail

# Màu sắc
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

log()     { echo -e "${CYAN}[SETUP]${NC} $*"; }
success() { echo -e "${GREEN}✅ $*${NC}"; }
warn()    { echo -e "${YELLOW}⚠️  $*${NC}"; }
error()   { echo -e "${RED}❌ $*${NC}"; exit 1; }
header()  { echo -e "\n${BOLD}${CYAN}══ $* ══${NC}\n"; }

# ─── Kiểm tra quyền ──────────────────────────────────────────────────────────
[ "$(id -u)" != "0" ] && error "Cần chạy với quyền root (sudo)!"

# ─── Nhập thông tin ───────────────────────────────────────────────────────────
header "⚙️  GITHUB ACTIONS RUNNER SETUP"
read -p "Nhập GitHub Repo URL (vd: https://github.com/username/blog): " REPO_URL
read -p "Nhập Runner Registration Token (lấy từ Settings > Actions > Runners): " RUNNER_TOKEN
read -p "Runner name (Enter để dùng hostname): " RUNNER_NAME
RUNNER_NAME="${RUNNER_NAME:-$(hostname)}"

RUNNER_USER="github-runner"
RUNNER_HOME="/home/${RUNNER_USER}"
RUNNER_DIR="${RUNNER_HOME}/actions-runner"
RUNNER_VERSION="2.322.0"

# ─── Bước 1: Cài Docker ───────────────────────────────────────────────────────
header "🐳 Bước 1: Cài Docker Engine"
if ! command -v docker &>/dev/null; then
  log "Cài Docker..."
  apt-get update -qq
  apt-get install -y -qq ca-certificates curl gnupg lsb-release
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  chmod a+r /etc/apt/keyrings/docker.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
    https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
    tee /etc/apt/sources.list.d/docker.list > /dev/null
  apt-get update -qq
  apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin
  systemctl enable docker
  systemctl start docker
  success "Docker đã cài xong"
else
  success "Docker đã có: $(docker --version)"
fi

# ─── Bước 2: Cài các công cụ cần thiết ──────────────────────────────────────
header "🔧 Bước 2: Cài dependencies"
apt-get install -y -qq git curl wget jq bc python3 python3-pip python3-venv

# ─── Bước 3: Tạo user chạy runner ────────────────────────────────────────────
header "👤 Bước 3: Tạo user runner"
if ! id "${RUNNER_USER}" &>/dev/null; then
  useradd -m -s /bin/bash "${RUNNER_USER}"
  success "Tạo user ${RUNNER_USER}"
fi

# Thêm vào group docker
usermod -aG docker "${RUNNER_USER}"
success "User ${RUNNER_USER} có quyền Docker"

# ─── Bước 4: Tải GitHub Actions Runner ────────────────────────────────────────
header "📥 Bước 4: Tải GitHub Runner v${RUNNER_VERSION}"
sudo -u "${RUNNER_USER}" bash -c "mkdir -p ${RUNNER_DIR}"
ARCH="linux-x64"
RUNNER_PKG="actions-runner-${ARCH}-${RUNNER_VERSION}.tar.gz"
RUNNER_URL="https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/${RUNNER_PKG}"

if [ ! -f "${RUNNER_DIR}/config.sh" ]; then
  log "Tải runner từ GitHub..."
  sudo -u "${RUNNER_USER}" bash -c "
    cd ${RUNNER_DIR}
    curl -sL '${RUNNER_URL}' -o runner.tar.gz
    tar xzf runner.tar.gz
    rm runner.tar.gz
  "
  success "Runner đã giải nén"
else
  success "Runner đã được cài trước đó"
fi

# ─── Bước 5: Cài dependencies của runner ──────────────────────────────────────
header "📦 Bước 5: Cài runner dependencies"
"${RUNNER_DIR}/bin/installdependencies.sh" 2>/dev/null || true

# ─── Bước 6: Đăng ký runner với GitHub ────────────────────────────────────────
header "🔗 Bước 6: Đăng ký runner với GitHub"
sudo -u "${RUNNER_USER}" bash -c "
  cd ${RUNNER_DIR}
  ./config.sh \
    --url '${REPO_URL}' \
    --token '${RUNNER_TOKEN}' \
    --name '${RUNNER_NAME}' \
    --labels 'self-hosted,linux,x64,proxmox,ubuntu-24.04' \
    --work '_work' \
    --unattended \
    --replace
"
success "Runner đã đăng ký: ${RUNNER_NAME}"

# ─── Bước 7: Cài service systemd ──────────────────────────────────────────────
header "⚙️  Bước 7: Cài systemd service"
cd "${RUNNER_DIR}"
./svc.sh install "${RUNNER_USER}"
./svc.sh start

# Override service để inject env vars
cat > /etc/systemd/system/actions.runner.override.conf <<'EOF'
[Service]
Restart=always
RestartSec=5
TimeoutStartSec=90
EOF

systemctl daemon-reload
systemctl enable "$(./svc.sh status 2>/dev/null | grep -oP 'actions\.runner\.\S+' | head -1)" 2>/dev/null || true

success "Runner service đã chạy!"

# ─── Bước 8: Tạo thư mục app trên VM ──────────────────────────────────────────
header "📁 Bước 8: Chuẩn bị thư mục project"
APP_DIR="/home/${RUNNER_USER}/blog"
sudo -u "${RUNNER_USER}" mkdir -p "${APP_DIR}/logs" "${APP_DIR}/scripts"
chown -R "${RUNNER_USER}:${RUNNER_USER}" "${APP_DIR}"
success "Thư mục project: ${APP_DIR}"

# ─── Hoàn tất ─────────────────────────────────────────────────────────────────
echo -e "\n${GREEN}${BOLD}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║        ✅ SETUP HOÀN TẤT!                           ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo -e "  🏷️  Runner name  : ${CYAN}${RUNNER_NAME}${NC}"
echo -e "  🔖 Labels       : ${CYAN}self-hosted, linux, x64, proxmox, ubuntu-24.04${NC}"
echo -e "  👤 User          : ${CYAN}${RUNNER_USER}${NC}"
echo -e "  📁 Runner dir   : ${CYAN}${RUNNER_DIR}${NC}"
echo ""
echo -e "  📋 Kiểm tra trạng thái:"
echo -e "  ${YELLOW}  systemctl status actions.runner.*${NC}"
echo ""
echo -e "  📋 Bước tiếp theo:"
echo -e "  ${YELLOW}  1. Vào GitHub > Settings > Actions > Runners${NC}"
echo -e "  ${YELLOW}  2. Xác nhận runner '${RUNNER_NAME}' đang 'Idle'${NC}"
echo -e "  ${YELLOW}  3. Push code lên master để trigger deploy!${NC}"
echo ""
echo -e "  ⚠️  Nhớ thêm GitHub Secrets:"
echo -e "     DB_USER, DB_PASSWORD, DB_ROOT_PASSWORD, DATABASE_URL"
