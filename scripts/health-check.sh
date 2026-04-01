#!/usr/bin/env bash
# =============================================================================
# health-check.sh — Kiểm tra sức khỏe toàn bộ hệ thống Blog App
# Trả về: exit 0 nếu OK, exit 1 nếu có lỗi
# Cách dùng: ./scripts/health-check.sh [--quiet] [--json]
# =============================================================================

set -euo pipefail

# ─── Màu sắc ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

# ─── Flags ────────────────────────────────────────────────────────────────────
QUIET=false; JSON_OUTPUT=false
for arg in "$@"; do
  case $arg in
    --quiet) QUIET=true ;;
    --json)  JSON_OUTPUT=true ;;
  esac
done

# ─── Cấu hình ─────────────────────────────────────────────────────────────────
BACKEND_URL="http://localhost:8000/health"
FRONTEND_URL="http://localhost:80"
MONITORING_URL="http://localhost:8080/api/health"
TIMEOUT=10
RETRIES=3
RETRY_DELAY=5

# ─── Biến theo dõi kết quả ────────────────────────────────────────────────────
CHECKS_TOTAL=0
CHECKS_PASSED=0
CHECKS_FAILED=0
RESULTS_JSON="{"

log()     { [ "${QUIET}" = false ] && echo -e "${CYAN}[CHECK]${NC} $*"; }
pass()    { echo -e "${GREEN}  ✅ $*${NC}"; CHECKS_PASSED=$((CHECKS_PASSED+1)); }
fail()    { echo -e "${RED}  ❌ $*${NC}"; CHECKS_FAILED=$((CHECKS_FAILED+1)); }
warn()    { echo -e "${YELLOW}  ⚠️  $*${NC}"; }

# ─── Hàm HTTP check ───────────────────────────────────────────────────────────
check_http() {
  local name="$1"
  local url="$2"
  local expected_code="${3:-200}"
  CHECKS_TOTAL=$((CHECKS_TOTAL+1))

  log "Kiểm tra ${name}: ${url}"
  for i in $(seq 1 $RETRIES); do
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
      --connect-timeout $TIMEOUT --max-time $TIMEOUT "${url}" 2>/dev/null) || RESPONSE="000"

    if [ "${RESPONSE}" = "${expected_code}" ]; then
      # Đo response time
      RT=$(curl -s -o /dev/null -w "%{time_total}" \
        --connect-timeout $TIMEOUT --max-time $TIMEOUT "${url}" 2>/dev/null) || RT="N/A"
      pass "${name} → HTTP ${RESPONSE} (${RT}s)"
      RESULTS_JSON+="\"${name}\":{\"status\":\"ok\",\"http\":${RESPONSE},\"response_time\":\"${RT}s\"},"
      return 0
    fi
    [ $i -lt $RETRIES ] && { warn "Lần ${i}/${RETRIES} thất bại (HTTP ${RESPONSE}), thử lại..."; sleep $RETRY_DELAY; }
  done

  fail "${name} → HTTP ${RESPONSE} (expected ${expected_code})"
  RESULTS_JSON+="\"${name}\":{\"status\":\"fail\",\"http\":${RESPONSE}},"
  return 1
}

# ─── Hàm kiểm tra Docker container ───────────────────────────────────────────
check_container() {
  local name="$1"
  local container="$2"
  CHECKS_TOTAL=$((CHECKS_TOTAL+1))

  log "Kiểm tra container: ${container}"
  STATUS=$(docker inspect --format='{{.State.Status}}' "${container}" 2>/dev/null || echo "not_found")
  HEALTH=$(docker inspect --format='{{.State.Health.Status}}' "${container}" 2>/dev/null || echo "N/A")

  if [ "${STATUS}" = "running" ]; then
    pass "${name} → running (health: ${HEALTH})"
    RESULTS_JSON+="\"${name}_container\":{\"status\":\"ok\",\"state\":\"${STATUS}\",\"health\":\"${HEALTH}\"},"
    return 0
  else
    fail "${name} container → ${STATUS}"
    RESULTS_JSON+="\"${name}_container\":{\"status\":\"fail\",\"state\":\"${STATUS}\"},"
    return 1
  fi
}

# ─── Hàm kiểm tra tài nguyên hệ thống ───────────────────────────────────────
check_resources() {
  CHECKS_TOTAL=$((CHECKS_TOTAL+1))
  log "Kiểm tra tài nguyên hệ thống..."

  # CPU load
  CPU_LOAD=$(cat /proc/loadavg | awk '{print $1}')
  CPU_CORES=$(nproc)
  CPU_PCT=$(echo "scale=1; ${CPU_LOAD} / ${CPU_CORES} * 100" | bc 2>/dev/null || echo "N/A")

  # RAM
  RAM_TOTAL=$(free -m | awk '/^Mem:/{print $2}')
  RAM_USED=$(free -m | awk '/^Mem:/{print $3}')
  RAM_PCT=$(echo "scale=1; ${RAM_USED} / ${RAM_TOTAL} * 100" | bc 2>/dev/null || echo "N/A")

  # Disk
  DISK_PCT=$(df -h / | awk 'NR==2{print $5}' | tr -d '%')

  local resource_ok=true
  [ "${DISK_PCT}" -gt 90 ] 2>/dev/null && { fail "Disk gần đầy: ${DISK_PCT}%"; resource_ok=false; }
  [ "$(echo "${RAM_PCT} > 95" | bc -l 2>/dev/null || echo 0)" = "1" ] && { fail "RAM quá tải: ${RAM_PCT}%"; resource_ok=false; }

  if [ "${resource_ok}" = true ]; then
    pass "Tài nguyên OK — CPU: ${CPU_PCT}% | RAM: ${RAM_PCT}% (${RAM_USED}/${RAM_TOTAL}MB) | Disk: ${DISK_PCT}%"
    RESULTS_JSON+="\"resources\":{\"status\":\"ok\",\"cpu_pct\":\"${CPU_PCT}\",\"ram_pct\":\"${RAM_PCT}\",\"disk_pct\":\"${DISK_PCT}\"},"
    return 0
  fi
  RESULTS_JSON+="\"resources\":{\"status\":\"warn\",\"cpu_pct\":\"${CPU_PCT}\",\"ram_pct\":\"${RAM_PCT}\",\"disk_pct\":\"${DISK_PCT}\"},"
  return 1
}

# ─── Hàm kiểm tra Database ────────────────────────────────────────────────────
check_database() {
  CHECKS_TOTAL=$((CHECKS_TOTAL+1))
  log "Kiểm tra kết nối Database..."

  if docker compose exec -T db mysqladmin ping -h localhost --silent 2>/dev/null; then
    pass "MySQL đang hoạt động"
    RESULTS_JSON+="\"database\":{\"status\":\"ok\"},"
    return 0
  else
    fail "MySQL không phản hồi!"
    RESULTS_JSON+="\"database\":{\"status\":\"fail\"},"
    return 1
  fi
}

# =============================================================================
echo -e "\n${BOLD}${CYAN}══════════════════════════════════════════${NC}"
echo -e "${BOLD}${CYAN}  🏥 HEALTH CHECK — $(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo -e "${BOLD}${CYAN}══════════════════════════════════════════${NC}\n"

OVERALL_STATUS=0

# Chạy các kiểm tra
check_container "Backend"    "blog_be"   || OVERALL_STATUS=1
check_container "Frontend"   "blog_fe"   || OVERALL_STATUS=1
check_container "Database"   "blog-db"   || OVERALL_STATUS=1   # Đã fix thành blog-db cho chuẩn với compose

check_http "Backend API"      "${BACKEND_URL}"    "200" || OVERALL_STATUS=1
check_http "Frontend"         "${FRONTEND_URL}"   "200" || OVERALL_STATUS=1
check_http "Monitoring"       "${MONITORING_URL}" "200" || true  # non-critical

check_database  || OVERALL_STATUS=1
check_resources || OVERALL_STATUS=1

# ─── Kết quả tổng hợp ─────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}══════════════════════════════════════════${NC}"
if [ $OVERALL_STATUS -eq 0 ]; then
  echo -e "${GREEN}${BOLD}  ✅ TẤT CẢ CHECKS PASSED: ${CHECKS_PASSED}/${CHECKS_TOTAL}${NC}"
else
  echo -e "${RED}${BOLD}  ❌ CHECKS FAILED: ${CHECKS_FAILED}/${CHECKS_TOTAL}${NC}"
fi
echo -e "${BOLD}══════════════════════════════════════════${NC}\n"

# JSON output mode
if [ "${JSON_OUTPUT}" = true ]; then
  RESULTS_JSON="${RESULTS_JSON%,}}"
  echo "${RESULTS_JSON}" | python3 -m json.tool 2>/dev/null || echo "${RESULTS_JSON}"
fi

exit $OVERALL_STATUS
