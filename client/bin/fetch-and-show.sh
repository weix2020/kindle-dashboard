#!/bin/sh
# 单次拉图并显示
# 由 dashboard.sh 或 crond 调用

set -e

# === 配置 ===
DASHBOARD_URL="https://YOUR-USER.github.io/YOUR-REPO/dashboard.png"  # ← 改成你的
IMAGE_PATH="/mnt/us/kindle-dashboard/last.png"
ARCHIVE_PATH="/mnt/us/kindle-dashboard/archive"
LOG="/mnt/us/kindle-dashboard/dashboard.log"

mkdir -p "$(dirname $IMAGE_PATH)" "$ARCHIVE_PATH"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG"
}

# === 1. WiFi 唤醒 ===
log "wake wifi"
lipc-set-prop com.lab126.cmd wirelessEnable 1
sleep 5

# 等待 wifi 连接，最多等 30 秒
for i in 1 2 3 4 5 6; do
    STATE=$(lipc-get-prop com.lab126.wifid cmState 2>/dev/null || echo "")
    if echo "$STATE" | grep -q "CONNECTED"; then
        log "wifi connected"
        break
    fi
    sleep 5
done

# === 2. 拉图 ===
TMPIMG="/tmp/dash-$$.png"
log "fetch $DASHBOARD_URL"
if curl -ksSL --max-time 30 "$DASHBOARD_URL" -o "$TMPIMG"; then
    SIZE=$(stat -c %s "$TMPIMG" 2>/dev/null || echo 0)
    log "fetched $SIZE bytes"
    if [ "$SIZE" -gt 1000 ]; then
        # 归档到时间戳命名
        cp "$TMPIMG" "$ARCHIVE_PATH/$(date '+%Y%m%d-%H%M%S').png" 2>/dev/null || true
        mv "$TMPIMG" "$IMAGE_PATH"
    else
        log "image too small, skip"
        rm -f "$TMPIMG"
    fi
else
    log "fetch failed"
    rm -f "$TMPIMG"
fi

# === 3. 显示 ===
if [ -f "$IMAGE_PATH" ]; then
    log "display"
    # -f 强制全刷清残影；每 12 次局刷后做一次全刷
    eips -f -g "$IMAGE_PATH"
fi

# === 4. WiFi 关 ===
log "wifi off"
lipc-set-prop com.lab126.cmd wirelessEnable 0

log "done"