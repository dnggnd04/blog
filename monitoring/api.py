from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import subprocess
import json
import os
import time
import platform
from datetime import datetime
from pathlib import Path

app = FastAPI(title="Blog Server Monitor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (dashboard HTML/CSS/JS)
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

START_TIME = time.time()


def run_cmd(cmd: list[str], timeout: int = 5) -> str:
    """Chạy lệnh shell an toàn, trả về output."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip()
    except Exception:
        return ""


def get_cpu_info() -> dict:
    try:
        load = os.getloadavg()
        cores = os.cpu_count() or 1
        cpu_pct = round(load[0] / cores * 100, 1)
        return {
            "load_1m": round(load[0], 2),
            "load_5m": round(load[1], 2),
            "load_15m": round(load[2], 2),
            "cores": cores,
            "usage_pct": min(cpu_pct, 100),
        }
    except Exception:
        return {"usage_pct": 0, "cores": 1}


def get_memory_info() -> dict:
    try:
        with open("/proc/meminfo") as f:
            lines = f.readlines()
        info = {}
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                info[parts[0].rstrip(":")] = int(parts[1])

        total = info.get("MemTotal", 0)
        available = info.get("MemAvailable", 0)
        used = total - available
        return {
            "total_mb": round(total / 1024, 1),
            "used_mb": round(used / 1024, 1),
            "available_mb": round(available / 1024, 1),
            "usage_pct": round(used / total * 100, 1) if total > 0 else 0,
        }
    except Exception:
        return {"total_mb": 0, "used_mb": 0, "usage_pct": 0}


def get_disk_info() -> dict:
    try:
        stat = os.statvfs("/")
        total = stat.f_blocks * stat.f_frsize
        free = stat.f_bfree * stat.f_frsize
        used = total - free
        return {
            "total_gb": round(total / 1024**3, 1),
            "used_gb": round(used / 1024**3, 1),
            "free_gb": round(free / 1024**3, 1),
            "usage_pct": round(used / total * 100, 1) if total > 0 else 0,
        }
    except Exception:
        return {"total_gb": 0, "used_gb": 0, "usage_pct": 0}


def get_containers() -> list[dict]:
    output = run_cmd([
        "docker", "ps", "-a",
        "--format", "{{.Names}}\t{{.Status}}\t{{.Image}}\t{{.Ports}}"
    ])
    containers = []
    for line in output.splitlines():
        parts = line.split("\t")
        if len(parts) >= 3:
            name = parts[0]
            status_raw = parts[1]
            image = parts[2]
            ports = parts[3] if len(parts) > 3 else ""

            if "Up" in status_raw:
                state = "running"
            elif "Exited" in status_raw:
                state = "stopped"
            elif "Restarting" in status_raw:
                state = "restarting"
            else:
                state = "unknown"

            containers.append({
                "name": name,
                "state": state,
                "status": status_raw,
                "image": image,
                "ports": ports,
            })
    return containers


def get_docker_stats() -> list[dict]:
    output = run_cmd([
        "docker", "stats", "--no-stream",
        "--format", "{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}"
    ], timeout=10)
    stats = []
    for line in output.splitlines():
        parts = line.split("\t")
        if len(parts) >= 6:
            stats.append({
                "name": parts[0],
                "cpu_pct": parts[1],
                "mem_usage": parts[2],
                "mem_pct": parts[3],
                "net_io": parts[4],
                "block_io": parts[5],
            })
    return stats


def get_deploy_history(limit: int = 10) -> list[dict]:
    log_file = "/app/logs/deploy_history.log"
    if not os.path.exists(log_file):
        log_file = "/home/github-runner/blog/logs/deploy_history.log"

    history = []
    if os.path.exists(log_file):
        with open(log_file) as f:
            lines = f.readlines()
        for line in reversed(lines[-limit:]):
            parts = line.strip().split("|")
            if len(parts) >= 4:
                history.append({
                    "timestamp": parts[0],
                    "commit": parts[1],
                    "status": parts[2],
                    "duration": parts[3],
                })
    return history


def get_recent_logs(service: str = None, lines: int = 50) -> list[str]:
    svc_map = {
        "backend": "blog_be",
        "frontend": "blog_fe",
        "db": "blog-db"
    }
    
    if service and service != "all":
        target = svc_map.get(service, service)
        cmd = ["docker", "logs", "--tail", str(lines), target]
        output = run_cmd(cmd, timeout=8)
        return output.splitlines()[-lines:] if output else []
    
    # Nếu lấy "all", lấy 20 lines từ mọi container đang chạy
    output = run_cmd(["docker", "ps", "--format", "{{.Names}}"])
    all_logs = []
    if output:
        for c in output.splitlines():
            out = run_cmd(["docker", "logs", "--tail", "20", c])
            if out:
                all_logs.extend([f"[{c}] " + l for l in out.splitlines()[-20:]])
    return all_logs[-lines:] if all_logs else []


# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/")
async def root():
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/api/health")
async def health():
    uptime_secs = int(time.time() - START_TIME)
    return {
        "status": "ok",
        "service": "blog-monitoring",
        "uptime_seconds": uptime_secs,
        "timestamp": datetime.now().isoformat(),
        "host": platform.node(),
    }


@app.get("/api/metrics")
async def metrics():
    """Tổng hợp toàn bộ metrics hệ thống."""
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu": get_cpu_info(),
        "memory": get_memory_info(),
        "disk": get_disk_info(),
        "system_uptime": run_cmd(["uptime", "-p"]),
        "os": platform.version(),
        "hostname": platform.node(),
    }


@app.get("/api/containers")
async def containers():
    """Danh sách và trạng thái containers."""
    return {
        "timestamp": datetime.now().isoformat(),
        "containers": get_containers(),
        "stats": get_docker_stats(),
    }


@app.get("/api/logs")
async def logs(service: str = None, lines: int = 50):
    """Lấy log gần nhất từ Docker containers."""
    return {
        "service": service or "all",
        "lines": get_recent_logs(service, lines),
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/deploys")
async def deploys(limit: int = 10):
    """Lịch sử deploy."""
    return {
        "history": get_deploy_history(limit),
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/overview")
async def overview():
    """Endpoint tổng hợp — Dashboard gọi endpoint này để lấy mọi thứ cùng lúc."""
    return {
        "timestamp": datetime.now().isoformat(),
        "health": "ok",
        "cpu": get_cpu_info(),
        "memory": get_memory_info(),
        "disk": get_disk_info(),
        "containers": get_containers(),
        "recent_deploys": get_deploy_history(5),
        "uptime": run_cmd(["uptime", "-p"]),
        "hostname": platform.node(),
    }
