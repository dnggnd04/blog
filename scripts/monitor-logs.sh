#!/usr/bin/env bash
# =============================================================================
# monitor-logs.sh — Script giám sát log realtime cho Blog App
# Cách dùng:
#   ./scripts/monitor-logs.sh                # Xem tất cả services
#   ./scripts/monitor-logs.sh backend        # Chỉ xem backend
#   ./scripts/monitor-logs.sh --errors       # Chỉ hiển thị lỗi
#   ./scripts/monitor-logs.sh --save         # Lưu ra file
#   ./scripts/monitor-logs.sh --report       # Báo cáo tổng hợp
# =============================================================================

set -euo pipefail

# ─── Màu sắc ──────────────────────────────────────────────────────────────────
RED='\033[0;31m';    GREEN='\033[0;32m';  YELLOW='\033[1;33m'
BLUE='\033[0;34m';   CYAN='\033[0;36m';  MAGENTA='\033[0;35m'
BOLD='\033[1m';      DIM='\033[2m';      NC='\033[0m'

# ─── Cấu hình ─────────────────────────────────────────────────────────────────
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${APP_DIR}/logs"
MONITOR_LOG="${LOG_DIR}/monitor_$(date '+%Y%m%d').log"
ALERT_LOG="${LOG_DIR}/alerts.log"
LINES=100           # Số dòng log hiển thị khi start
TAIL_LINES=50       # Số dòng tail lịch sử

mkdir -p "${LOG_DIR}"

# ─── Parse arguments ──────────────────────────────────────────────────────────
SERVICE=""
ERRORS_ONLY=false
SAVE_LOG=false
REPORT_MODE=false
FOLLOW=true

for arg in "$@"; do
  case $arg in
    backend|frontend|db|monitoring) SERVICE="$arg" ;;
    --errors)    ERRORS_ONLY=true ;;
    --save)      SAVE_LOG=true ;;
    --report)    REPORT_MODE=true; FOLLOW=false ;;
    --no-follow) FOLLOW=false ;;
  esac
done

# ─── Màu theo service ─────────────────────────────────────────────────────────
color_line() {
  local line="$1"
  # Màu theo level log
  if echo "${line}" | grep -qiE "(error|exception|critical|fatal|traceback)"; then
    echo -e "${RED}${line}${NC}"
  elif echo "${line}" | grep -qiE "(warning|warn|deprecated)"; then
    echo -e "${YELLOW}${line}${NC}"
  elif echo "${line}" | grep -qiE "(success|started|ready|connected|ok\b)"; then
    echo -e "${GREEN}${line}${NC}"
  elif echo "${line}" | grep -qiE "(info\b|GET |POST |PUT |DELETE |PATCH )"; then
    echo -e "${CYAN}${line}${NC}"
  else
    echo -e "${DIM}${line}${NC}"
  fi
}

# ─── Hàm alert khi phát hiện lỗi nghiêm trọng ────────────────────────────────
check_alert() {
  local line="$1"
  local service_name="$2"
  
  if echo "${line}" | grep -qiE "(critical|fatal|out of memory|oom|connection refused|database error)"; then
    local alert_msg="[$(date '+%Y-%m-%d %H:%M:%S')] 🚨 CRITICAL | ${service_name} | ${line}"
    echo "${alert_msg}" >> "${ALERT_LOG}"
    echo -e "\n${RED}${BOLD}🚨 ALERT: ${alert_msg}${NC}\n"
    
    # Gửi Telegram nếu có cấu hình
    if [ -f "${APP_DIR}/.env" ]; then
      source <(grep -E "^TELEGRAM_" "${APP_DIR}/.env" 2>/dev/null || true)
      if [ -n "${TELEGRAM_BOT_TOKEN:-}" ] && [ -n "${TELEGRAM_CHAT_ID:-}" ]; then
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
          -d "chat_id=${TELEGRAM_CHAT_ID}" \
          -d "text=🚨 ALERT từ ${service_name}: ${line}" \
          -d "parse_mode=Markdown" >/dev/null 2>&1 || true
      fi
    fi
  fi
}

# ─── Hàm xem log 1 service ───────────────────────────────────────────────────
watch_service() {
  local svc="$1"
  local color="$2"
  local prefix="$3"
  
  docker compose logs --tail="${TAIL_LINES}" -f "${svc}" 2>/dev/null | \
  while IFS= read -r line; do
    # Filter lỗi nếu cần
    if [ "${ERRORS_ONLY}" = true ]; then
      echo "${line}" | grep -qiE "(error|exception|critical|warning)" || continue
    fi
    
    # Thêm prefix service
    formatted="${color}[${prefix}]${NC} ${line}"
    
    # Hiển thị với màu
    color_line "${prefix}: ${line}"
    
    # Lưu log nếu cần
    if [ "${SAVE_LOG}" = true ]; then
      echo "[$(date '+%H:%M:%S')] [${prefix}] ${line}" >> "${MONITOR_LOG}"
    fi
    
    # Kiểm tra alert
    check_alert "${line}" "${prefix}"
  done
}

# ─── Chế độ báo cáo tổng hợp ─────────────────────────────────────────────────
generate_report() {
  echo -e "\n${BOLD}${CYAN}╔════════════════════════════════════════════╗${NC}"
  echo -e "${BOLD}${CYAN}║      📊 LOG REPORT — $(date '+%Y-%m-%d %H:%M')       ║${NC}"
  echo -e "${BOLD}${CYAN}╚════════════════════════════════════════════╝${NC}\n"

  local services=("backend" "frontend" "db")
  [ -n "${SERVICE}" ] && services=("${SERVICE}")

  for svc in "${services[@]}"; do
    echo -e "${BOLD}─── 📦 Service: ${svc} ───${NC}"
    
    # Tổng số request (chỉ backend)
    if [ "${svc}" = "backend" ]; then
      TOTAL_REQ=$(docker compose logs --tail=1000 "${svc}" 2>/dev/null | grep -cE "^[0-9]" || echo "0")
      ERR_COUNT=$(docker compose logs --tail=1000 "${svc}" 2>/dev/null | grep -ciE "(error|exception)" || echo "0")
      WARN_COUNT=$(docker compose logs --tail=1000 "${svc}" 2>/dev/null | grep -ciE "warning" || echo "0")
      echo -e "  📈 Requests (1000 dòng gần nhất): ${CYAN}${TOTAL_REQ}${NC}"
      echo -e "  ❌ Lỗi: ${RED}${ERR_COUNT}${NC}"
      echo -e "  ⚠️  Cảnh báo: ${YELLOW}${WARN_COUNT}${NC}"
    fi

    echo -e "\n  ${DIM}=== 5 dòng log cuối ===${NC}"
    docker compose logs --tail=5 --no-log-prefix "${svc}" 2>/dev/null | \
      while IFS= read -r line; do color_line "  ${line}"; done || echo "  (Không có log)"
    echo ""
  done

  # Alerts
  if [ -f "${ALERT_LOG}" ]; then
    echo -e "${BOLD}─── 🚨 Cảnh báo nghiêm trọng gần đây ───${NC}"
    tail -n 10 "${ALERT_LOG}" | while IFS= read -r line; do
      echo -e "  ${RED}${line}${NC}"
    done
  fi

  # Container stats
  echo -e "\n${BOLD}─── 🐳 Docker Resource Usage ───${NC}"
  docker stats --no-stream --format \
    "  {{.Name}}\t CPU: {{.CPUPerc}}\t MEM: {{.MemUsage}}\t NET: {{.NetIO}}" \
    2>/dev/null || echo "  (Không thể lấy stats)"

  echo -e "\n${DIM}Report tạo lúc: $(date)${NC}"
}

# =============================================================================
#  MAIN
# =============================================================================
if [ "${REPORT_MODE}" = true ]; then
  generate_report
  exit 0
fi

echo -e "${BOLD}${CYAN}"
echo "╔════════════════════════════════════════════════╗"
echo "║          📋 BLOG APP LOG MONITOR               ║"
echo "║  Nhấn Ctrl+C để thoát                         ║"
echo "╚════════════════════════════════════════════════╝"
echo -e "${NC}"
echo -e "  📁 Lưu log: ${SAVE_LOG}"
echo -e "  🔴 Chỉ lỗi: ${ERRORS_ONLY}"
echo -e "  📦 Service : ${SERVICE:-all}\n"

[ "${SAVE_LOG}" = true ] && echo -e "${DIM}  → Đang ghi log vào: ${MONITOR_LOG}${NC}\n"

# Xem theo từng service hoặc tất cả
if [ -n "${SERVICE}" ]; then
  case "${SERVICE}" in
    backend)    watch_service "backend"    "${BLUE}"    "BACKEND" ;;
    frontend)   watch_service "frontend"   "${GREEN}"   "FRONTEND" ;;
    db)         watch_service "db"         "${MAGENTA}" "DATABASE" ;;
    monitoring) watch_service "monitoring" "${CYAN}"    "MONITOR" ;;
  esac
else
  # Xem tất cả services đồng thời với màu sắc
  docker compose logs --tail="${TAIL_LINES}" -f 2>/dev/null | \
  while IFS= read -r line; do
    if [ "${ERRORS_ONLY}" = true ]; then
      echo "${line}" | grep -qiE "(error|exception|critical|warning)" || continue
    fi
    
    # Xác định service từ prefix
    if echo "${line}" | grep -q "^backend"; then
      color_line "${BLUE}[BE]${NC} ${line}"
    elif echo "${line}" | grep -q "^frontend"; then
      color_line "${GREEN}[FE]${NC} ${line}"
    elif echo "${line}" | grep -q "^db"; then
      color_line "${MAGENTA}[DB]${NC} ${line}"
    elif echo "${line}" | grep -q "^monitoring"; then
      color_line "${CYAN}[MON]${NC} ${line}"
    else
      color_line "${line}"
    fi

    [ "${SAVE_LOG}" = true ] && echo "[$(date '+%H:%M:%S')] ${line}" >> "${MONITOR_LOG}"
    check_alert "${line}" "system"
  done
fi
