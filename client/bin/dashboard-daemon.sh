#!/bin/sh
# 后台守护：定时拉图 + 深休眠唤醒
# 启动后无限循环，每 INTERVAL 秒拉一次图

BIN="/mnt/us/kindle-dashboard/bin"
INTERVAL=${INTERVAL:-3600}  # 默认 1 小时

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [daemon] $*" >> "/mnt/us/kindle-dashboard/dashboard.log"
}

log "daemon start (interval=${INTERVAL}s)"

# === 抗烧屏：每 N 次拉图做一次反转脉冲 ===
CYCLE_FILE="/mnt/us/kindle-dashboard/.refresh_cycle"
COUNT=0
[ -f "$CYCLE_FILE" ] && COUNT=$(cat "$CYCLE_FILE")
FULL_REFRESH_EVERY=${FULL_REFRESH_EVERY:-12}

while true; do
    COUNT=$(( $COUNT + 1 ))
    if [ $COUNT -ge $FULL_REFRESH_EVERY ]; then
        log "anti-ghost pulse"
        # 全黑一帧 → 全白一帧
        eips -f -c
        eips -f -c  # 等价 fill white
        eips -f -g /mnt/us/kindle-dashboard/last.png 2>/dev/null || true
        COUNT=0
    else
        "$BIN/fetch-and-show.sh" once
    fi
    echo $COUNT > "$CYCLE_FILE"

    log "sleep ${INTERVAL}s"
    sleep "$INTERVAL"
done