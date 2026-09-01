#!/bin/sh
# 禁用 OTA 自动更新 - 避免越狱被覆盖
# 安装方法: ssh root@kindle 后执行一次

# 创建只读占位文件阻止 OTA
touch /mnt/us/update.bin.tmp.partial
chattr +i /mnt/us/update.bin.tmp.partial 2>/dev/null || chmod 555 /mnt/us/update.bin.tmp.partial

# 停用 otaupd 后台任务
stop otaupd 2>/dev/null || true

# 禁用 otaupd 服务
if [ -f /etc/upstart/otaupd.conf ]; then
    mv /etc/upstart/otaupd.conf /etc/upstart/otaupd.conf.disabled 2>/dev/null
fi

echo "OTA disabled"