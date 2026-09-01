#!/usr/bin/env python3
"""
KPW1 信息屏 - 服务端生成脚本
- 输出 758x1024 16级灰度 PNG
- 适配 GitHub Actions / Vercel / Cloudflare Pages
- 无外部字体时使用 PIL 默认位图字体也能跑

依赖: pip install Pillow requests
"""
import io
import json
import os
import time
from datetime import datetime, timezone, timedelta

import requests
from PIL import Image, ImageDraw, ImageFont

# ============== 配置 ==============
CONFIG = {
    "LAT": 31.2304,
    "LON": 121.4737,
    "TIMEZONE_OFFSET": 8,  # UTC+8
    "GITHUB_USER": "octocat",
    "CITY": "Shanghai",
}

W, H = 758, 1024
BLACK = 0
WHITE = 255

FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")

# 按优先级尝试字体，size 是字号，name 仅用于日志
def load_font(size, bold=False, cjk=False, mono=False):
    candidates = []
    if cjk:
        candidates = [
            "NotoSansCJK-Regular.ttc",
            "NotoSansCJK.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/Library/Fonts/PingFang.ttc",
        ]
    elif mono:
        candidates = [
            "Hack-Regular.ttf",
            "DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        ]
    elif bold:
        candidates = [
            "NotoSans-Bold.ttf",
            "DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial Bold.ttf",
        ]
    else:
        candidates = [
            "NotoSans-Regular.ttf",
            "DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial.ttf",
        ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    # 兜底：PIL 默认位图字体（忽略 size，但至少能渲染）
    return ImageFont.load_default()


# ============== 数据源 ==============
def fetch_weather():
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={CONFIG['LAT']}&longitude={CONFIG['LON']}"
            f"&current=temperature_2m,weather_code,relative_humidity_2m,wind_speed_10m"
            f"&daily=temperature_2m_max,temperature_2m_min,weather_code"
            f"&forecast_days=4&timezone=auto"
        )
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[weather] failed: {e}")
        return None


def fetch_github_contrib():
    try:
        url = f"https://github-contributions-api.joblk.dev/?user={CONFIG['GITHUB_USER']}"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[github] failed: {e}")
        return None


# ============== 天气码 → 文本 ==============
def weather_code_to_text(code):
    return {
        0: "Clear", 1: "Mostly Clear", 2: "Partly Cloudy", 3: "Overcast",
        45: "Fog", 48: "Rime Fog",
        51: "Light Drizzle", 53: "Drizzle", 55: "Heavy Drizzle",
        61: "Light Rain", 63: "Rain", 65: "Heavy Rain",
        71: "Light Snow", 73: "Snow", 75: "Heavy Snow",
        80: "Rain Shower", 81: "Heavy Shower", 82: "Violent Shower",
        95: "Thunderstorm", 96: "T-Storm + Hail", 99: "Severe T-Storm",
    }.get(code, f"Code {code}")


# ============== 绘制组件 ==============
def draw_clock(draw, x, y, w, h, f_time, f_date):
    """上半部分：大时钟 + 日期"""
    tz = timezone(timedelta(hours=CONFIG["TIMEZONE_OFFSET"]))
    now = datetime.now(tz)
    time_str = now.strftime("%H:%M")
    weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][now.weekday()]
    date_str = f"{now.strftime('%Y-%m-%d')}  {weekday}"

    # 大时钟（居中）
    bbox = draw.textbbox((0, 0), time_str, font=f_time)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((x + (w - tw) // 2, y + 40), time_str, font=f_time, fill=BLACK)

    # 日期
    bbox = draw.textbbox((0, 0), date_str, font=f_date)
    dw = bbox[2] - bbox[0]
    draw.text((x + (w - dw) // 2, y + 40 + th + 20), date_str, font=f_date, fill=BLACK)


def draw_weather(draw, x, y, w, h, weather, f_temp, f_label, f_small):
    """中部分：天气"""
    # 分割线
    draw.line([(x, y), (x + w, y)], fill=BLACK, width=1)
    draw.text((x, y + 10), "WEATHER", font=f_label, fill=BLACK)

    if not weather:
        draw.text((x, y + 50), "Offline", font=f_small, fill=BLACK)
        return

    current = weather["current"]
    daily = weather["daily"]

    # 大温度
    temp_str = f"{current['temperature_2m']:.0f}°"
    draw.text((x, y + 50), temp_str, font=f_temp, fill=BLACK)

    # 描述 + 湿度 + 风
    desc = weather_code_to_text(current["weather_code"])
    info = f"{desc}   Humidity {current['relative_humidity_2m']}%   Wind {current['wind_speed_10m']}km/h"
    draw.text((x, y + 230), info, font=f_small, fill=BLACK)

    # 4天预报
    row_y = y + 280
    for i in range(4):
        date = daily["time"][i]
        hi = daily["temperature_2m_max"][i]
        lo = daily["temperature_2m_min"][i]
        wd = weather_code_to_text(daily["weather_code"][i])
        line = f"{date[5:]}   {wd:<16}   {lo:.0f}° / {hi:.0f}°"
        draw.text((x, row_y + i * 30), line, font=f_small, fill=BLACK)


def draw_github(draw, x, y, w, h, data, f_label, f_small, f_tiny):
    """下部分：GitHub 贡献图"""
    draw.line([(x, y), (x + w, y)], fill=BLACK, width=1)
    draw.text((x, y + 10), "GITHUB", font=f_label, fill=BLACK)

    if not data:
        draw.text((x, y + 50), "Offline", font=f_small, fill=BLACK)
        return

    contribs = data.get("contributions", [])
    total = sum(c.get("count", 0) for c in contribs)
    last_30 = sum(c.get("count", 0) for c in contribs[-30:])
    draw.text((x, y + 50), f"@{CONFIG['GITHUB_USER']}  last 30d: {last_30}  total: {total}", font=f_small, fill=BLACK)

    # 简单 52 周 x 7 天 网格
    cell = 6
    ox, oy = x, y + 90
    weeks = data.get("contributions", [])
    # 用所有 weeks，每天 7 格；只画最后 52 周
    for w_idx in range(min(52, len(weeks))):
        week = weeks[-52 + w_idx] if len(weeks) >= 52 else weeks[w_idx]
        days = week.get("days", [])
        for d_idx in range(7):
            if d_idx >= len(days):
                continue
            count = days[d_idx].get("count", 0)
            level = min(4, count // 5) if count > 0 else 0
            shade = [250, 220, 170, 100, 30][level]
            cx = ox + w_idx * cell
            cy = oy + d_idx * cell
            if cx + cell <= x + w and cy + cell <= y + h:
                draw.rectangle([cx, cy, cx + cell - 1, cy + cell - 1], fill=shade)


def draw_footer(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(((W - tw) // 2, H - th - 20), text, font=font, fill=BLACK)


# ============== 主流程 ==============
def generate():
    print("[*] fetching data...")
    weather = fetch_weather()
    github = fetch_github_contrib()

    print("[*] rendering...")
    img = Image.new("L", (W, H), WHITE)
    draw = ImageDraw.Draw(img)

    M = 40  # margin

    # 字体
    f_time = load_font(140, bold=True)
    f_temp = load_font(160, bold=True)
    f_date = load_font(32)
    f_label = load_font(20, bold=True)
    f_small = load_font(22)
    f_tiny = load_font(16)

    # 1) 时钟  0~310 (310 高)
    draw_clock(draw, M, 30, W - 2 * M, 310, f_time, f_date)

    # 2) 天气  330~720 (390 高)
    draw_weather(draw, M, 350, W - 2 * M, 400, weather, f_temp, f_label, f_small)

    # 3) GitHub  760~960 (200 高)
    draw_github(draw, M, 760, W - 2 * M, 200, github, f_label, f_small, f_tiny)

    # 4) Footer
    tz = timezone(timedelta(hours=CONFIG["TIMEZONE_OFFSET"]))
    ts = datetime.now(tz).strftime("Updated %Y-%m-%d %H:%M UTC%z")
    draw_footer(draw, ts, f_tiny)

    # 16 级灰度 + dither
    img = img.convert("L").quantize(colors=16, dither=Image.Dither.FLOYDSTEINBERG)

    out_path = os.path.join(os.path.dirname(__file__), "dashboard.png")
    img.save(out_path, "PNG", optimize=True)
    print(f"[+] saved: {out_path} ({os.path.getsize(out_path)} bytes)")
    return out_path


if __name__ == "__main__":
    generate()