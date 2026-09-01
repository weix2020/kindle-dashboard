# Kindle Paperwhite 1 信息屏

把 KPW1（2012 款、E-Ink Pearl、758×1024）改造为低功耗可视化数据面板。

## 路线 B'：TRMNL 思路 + KPW1 适配

借用了 [TRMNL](https://trmnl.app/) 的核心思路：**服务端渲染 → 设备拉图 → 显示**。
但跳过 KOReader（对 KPW1 兼容性差），用 KUAL + 原生 shell 脚本实现客户端。

## 目录

```
kindle-dashboard/
├── server/                  # Python 服务端，生成 758x1024 PNG
│   ├── dashboard.py
│   ├── requirements.txt
│   └── README.md
├── client/                  # Kindle 端 KUAL 插件
│   ├── bin/
│   │   ├── dashboard.sh     # 入口 (start/stop/status/once)
│   │   ├── fetch-and-show.sh # 拉图+显示+关 WiFi
│   │   ├── dashboard-daemon.sh # 后台守护循环
│   │   ├── sleep-wake.sh    # mxc_rtc 深休眠（KPW1 专用）
│   │   ├── ota-block.sh     # 禁用 OTA
│   │   └── config.sh
│   ├── extensions/dashboard/ # KUAL 菜单
│   └── README.md
├── docs/
│   └── INSTALL.md           # 完整安装手册
└── firmware/                # 放 .bin 固件（不放在 git 里）
```

## 快速上手

1. 服务端推到 GitHub，配 Pages → 拿到 dashboard.png URL
2. 编辑 `client/bin/config.sh` 填入 URL
3. 越狱 KPW1（参考 `docs/INSTALL.md`）
4. 复制 `client/` 到 Kindle，启动 KUAL → Dashboard → Start

## 进度

- [x] 服务端 dashboard 生成脚本
- [x] KUAL 客户端拉图脚本
- [x] KPW1 深度休眠脚本（mxc_rtc）
- [x] 完整安装手册
- [ ] 字体文件（Noto Sans + CJK）
- [ ] GitHub Actions workflow 模板
- [ ] Vercel 部署版本