#!/bin/sh
# 客户端配置 - 改这里

# 你的 dashboard.png 公开地址
# 选项 A: GitHub Pages
DASHBOARD_URL="https://YOUR-USER.github.io/YOUR-REPO/dashboard.png"

# 选项 B: Vercel / Cloudflare Pages
# DASHBOARD_URL="https://dash.example.com/dashboard.png"

# 选项 C: Cloudflare R2 / S3 公开桶
# DASHBOARD_URL="https://pub-xxx.r2.dev/dashboard.png"

# 选项 D: 自托管服务器（需要 Kindle 端能直连）
# DASHBOARD_URL="http://192.168.1.100:8080/dashboard.png"

# 刷新间隔（秒）默认 1 小时
INTERVAL=3600

# 每 N 次局刷后做一次全刷清残影
FULL_REFRESH_EVERY=12

export DASHBOARD_URL INTERVAL FULL_REFRESH_EVERY