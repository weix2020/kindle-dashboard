# KPW1 信息屏改造完整手册

本工程把一台 Kindle Paperwhite 1（2012 款、E-Ink Pearl、758×1024）改造为一个低功耗可视化数据面板。

## 架构

```
┌──────────────────┐
│  公开 dashboard.png │
│ (GitHub Pages/R2/    │
│  Cloudflare Pages) │
└──────────┬───────────┘
           │ HTTPS GET /dashboard.png (每小时)
           ▼
┌──────────────────┐
│  KPW1 越狱 + KUAL  │
│  + fetch-and-show  │ ◀── mxc_rtc 深休眠（数周续航）
│  + eips 显示       │
└──────────────────┘
```

服务端渲染 758×1024、16 级灰度 PNG，Kindle 端定时拉图 → 显示 → 深休眠。

## 步骤概览

### Phase 1：服务端（无需 Kindle，先做）

1. 把 `server/` 推到 GitHub repo
2. 创建 `.github/workflows/dashboard.yml`，每小时跑一次：
   ```yaml
   on:
     schedule: [{ cron: '0 * * * *' }]
     workflow_dispatch:
   jobs:
     build:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-python@v5
           with: { python-version: '3.12' }
         - run: pip install -r server/requirements.txt
         - run: python server/dashboard.py
         - uses: actions/upload-pages-artifact@v3
           with:
             path: server/dashboard.png
     deploy:
       needs: build
       runs-on: ubuntu-latest
       environment:
         name: github-pages
         url: ${{ steps.deployment.outputs.page_url }}
       steps:
         - uses: actions/deploy-pages@v4
   ```

3. 把生成的 PNG 路径改成 `docs/dashboard.png` 并启用 Pages

### Phase 2：Kindle 端（等服务端跑起来再开始）

#### 2.1 降级固件到 5.3.5

KPW1 当前固件 `juno_16_yoshi`（约对应 5.6.x），必须降级到 **5.3.5** 才能用 Mesquite 越狱。

1. **开飞行模式**（防 OTA）
2. USB 连 Mac，下载 [`update_kindle_5.3.5.bin`](https://s3.amazonaws.com/G7G_FirmwareUpdates_WebDownloads/update_kindle_5.3.5.bin)
3. 拷到 Kindle 根目录
4. Kindle: 设置 → 三点菜单 → 更新您的 Kindle
5. 验证：设置 → 设备信息 → 固件版本应为 `5.3.5`

#### 2.2 越狱

参考 [ebook-reader-hacks KPW1 章节](https://github.com/Wladefant/ebook-reader-hacks/blob/main/jailbreaking-kindle.md#kindle-paperwhite-1-5th-generation)

1. 下载 [jailbreak-1.16.N-r18981.tar.xz](https://www.mobileread.com/forums/showthread.php?t=198446)
2. 解压后把：
   - `MOBI8_DEBUG` → 根目录
   - `jailbreak.sh` → 根目录
   - `jailbreak.mobi` → `documents/`
3. 弹出 Kindle，回到首页打开 `jailbreak.mobi`，点 "Jailbreak" 链接
4. 重启 Kindle

#### 2.3 安装 KUAL + USBNetwork

参考 [znjoa 教程](https://blog.znjoa.com/2023/07/25/installing-kual-and-mrpi-on-a-jailbroken-kindle-paperwhite-1/)

- 下载 KUAL-KDK-2.0.azw2 → `documents/`
- 安装 MRPI（MobileRead Package Installer）
- 安装 USBNetwork（SSH）：`update_usbnet_0.15.N_install_touch_pw.bin` → 根目录 → 设置中更新

#### 2.4 SSH 接入 + 装 Dashboard 插件

```bash
# Mac 通过 USB 接 Kindle，Kindle 搜索框输入 ;un 切换 USBNetwork 模式
# Mac 网络偏好设置新建 RNDIS/Ethernet: IP 192.168.15.1 / mask 255.255.255.0

ssh root@192.168.15.244  # 默认无密码

# 复制整个 client 目录到 Kindle
scp -r /Volumes/Kindle/kindle-dashboard/client root@192.168.15.244:/mnt/us/kindle-dashboard

# SSH 进去配置
ssh root@192.168.15.244
vi /mnt/us/kindle-dashboard/bin/config.sh   # 改成你的 dashboard URL
chmod +x /mnt/us/kindle-dashboard/bin/*.sh
ln -sf /mnt/us/kindle-dashboard/bin/dashboard.sh /mnt/us/extensions/dashboard/bin/dashboard
sh /mnt/us/kindle-dashboard/bin/ota-block.sh
```

#### 2.5 WiFi 配置 + 启动守护

在 Kindle 上：
- 设置 → WiFi → 连上你家 WiFi
- 设置 → 设备信息 → 记下 IP
- 搜索框输入 `;dashboard start`

验证日志：`/mnt/us/kindle-dashboard/dashboard.log`

## 显示效果

- **上 1/3**：大字体时间 + 日期 + 星期
- **中 1/3**：天气当前温度 + 4 天预报
- **下 1/3**：GitHub 贡献图 + 实时刷新的 Footer

整体 16 级灰度，758×1024 完美适配 KPW1。

## 调优建议

- **省电**：刷新间隔调到 3-6 小时，关闭背光
- **抗烧屏**：每 12 次自动做一次全屏反转脉冲
- **物理供电**：焊掉电池或加磁吸充电底座
- **夜间**：脚本里加 `lipc-set-prop com.lab126.powerd.flIntensity 0` 关背光

## 故障排查

| 现象 | 处理 |
|---|---|
| eips 命令 not found | 重新装 USBNetwork，里面有完整工具链 |
| WiFi 连不上 | KPW1 只支持 2.4GHz，别连 5G |
| curl SSL 失败 | 加 `-k` 参数跳过证书验证 |
| mxc_rtc 没找到 | KPW1 才有这个路径，PW2+ 用 rtcwake |
| 屏幕烧屏 | 调小 `FULL_REFRESH_EVERY` 值 |

## 不折腾的备选

如果越狱过程太痛苦，可以保留现在的多看系统直接用：
- 多看的屏保 / 锁屏可以显示自定义图片
- 把生成的 dashboard.png 转成 .png，按多看的图片格式放到 `pictures/` 目录
- 多看自己会定期刷新屏保

虽然显示逻辑和多看的看书模式冲突，但作为"摆桌上的常亮屏"够用。