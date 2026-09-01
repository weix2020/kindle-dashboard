# Kindle 端 KUAL 插件

把整套脚本作为 KUAL 扩展安装到 Kindle。

## 安装步骤

1. 越狱后，Kindle 接 Mac，把整个 `client/` 目录复制到 Kindle 根目录：
   ```
   cp -r client /Volumes/Kindle/kindle-dashboard
   ```

2. 编辑 `bin/config.sh`，改成你的公开 `dashboard.png` URL。

3. 在 Kindle 搜索框输入 `;log mrpi`，按 MRPI 安装：
   - 把 `kindle-dashboard/bin/*` 软链到 `/mnt/us/extensions/dashboard/bin/`

   或者手动建符号链接：
   ```
   ssh root@kindle
   ln -s /mnt/us/kindle-dashboard/bin/dashboard.sh /mnt/us/extensions/dashboard/bin/
   ```

4. 把 `extensions/dashboard` 目录整个拷贝到 Kindle `/mnt/us/extensions/` 下，KUAL 启动后会看到 "Dashboard" 入口。

## 用法

搜索框输入 `;dashboard start` 启动后台守护
搜索框输入 `;dashboard stop` 停止
搜索框输入 `;dashboard once` 手动拉一次图（不进入循环）

## 文件说明

| 文件 | 作用 |
|---|---|
| `bin/dashboard.sh` | KUAL 入口脚本（start/stop/status/once） |
| `bin/fetch-and-show.sh` | 一次拉图 → 显示 → 关 WiFi |
| `bin/dashboard-daemon.sh` | 守护循环，定时调用 fetch-and-show |
| `bin/sleep-wake.sh` | KPW1 专用深度休眠（mxc_rtc） |
| `bin/ota-block.sh` | 禁用 OTA 防越狱被覆盖 |
| `bin/config.sh` | 配置 dashboard URL 和刷新间隔 |