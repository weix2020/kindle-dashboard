# 服务端：生成 758×1024 dashboard.png

输出适配 KPW1 的 16 级灰度 PNG。

## 本地运行

```bash
pip install -r requirements.txt
python dashboard.py
```

输出 `dashboard.png`。

## GitHub Actions 自动部署到 Pages

1. 把本目录（含字体）推到一个 repo
2. 启用 Pages
3. workflow 每小时跑一次 `python dashboard.py && cp dashboard.png docs/dashboard.png && git push`
4. Kindle 拉 `https://<user>.github.io/<repo>/dashboard.png`

## Vercel / Cloudflare Pages

部署一个最小 Serverless Function：每天定时刷新 PNG 到 KV / R2，Kindle 直接拉静态 URL。

## 字体

去 [Google Fonts Noto](https://fonts.google.com/noto/specimen/Noto+Sans) 下载：
- NotoSans-Regular.ttf
- NotoSans-Bold.ttf
- NotoSansCJK-Regular.ttc（中文支持）
- Hack-Regular.ttf（GitHub 贡献图等宽显示）

放到 `fonts/` 目录。