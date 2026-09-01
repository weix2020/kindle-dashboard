#!/bin/sh
# KPW1 深度休眠 + RTC 唤醒
# KPW1 (Yoshime/Celeste) 的 rtc0/rtc1 和标准 rtcwake 都不可用
# 必须用 Freescale i.MX508 特有的 mxc_rtc.0 接口

# 用法: sleep-wake.sh <seconds>

WAKE_AFTER=${1:-3600}

# 1. 关 WiFi
lipc-set-prop com.lab126.cmd wirelessEnable 0 2>/dev/null

# 2. 关闭 framework 防止干扰
stop framework 2>/dev/null || true
stop ota 2>/dev/null || true

# 3. 设置 mxc_rtc 唤醒（秒数）
echo -n "$WAKE_AFTER" > /sys/devices/platform/mxc_rtc.0/wakeup_enable

# 4. 进入 deep sleep
echo mem > /sys/power/state

# 唤醒后会从这里继续
echo "[wakeup] $(date)" >> /mnt/us/kindle-dashboard/dashboard.log