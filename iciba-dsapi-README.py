# iciba-dsapi-README-0.6.0.py
# github.com/shenjuexiao
# 20261120

# iciba-dsapi-README.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
iciba-dsapi-README.py
功能：
    请求词霸每日一句 API，读取 JSON 响应中的 content / fenxiang_img 字段，
    生成 README.md（模板见文末）。
API:
    GET http://open.iciba.com/dsapi/?date={today}
JSON 字段：
    sid、tts、content、note、love、translation、picture、picture2、
    caption、dateline、s_pv、sp_pv、fenxiang_img、picture3、picture4、tags
用法：
    python iciba-dsapi-README.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

API_URL = "http://open.iciba.com/dsapi/?date={today}"
OUTPUT_FILE = Path("README.md")
TIMEOUT = 15
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

README_TEMPLATE = """# 词霸每日一句

![{content}]({fenxiang_img})

## 🚀 项目

[bingmen/iciba-dsapi](https://github.com/bingmen/iciba-dsapi)

## 😀 简介

📱 词霸每日一句，收集时间段 2018-01-01 ~ 今日，每日自动运行工作流。

## 📁 目录

- `.github/workflows/iciba-dsapi-json.yml` — 工作流
- `iciba-dsapi-json.py` — 每日更新 PY 脚本
- `dsapi-json-{year}/*.json` — 每日 JSON 对象
- `dsapi-json-{year}.json` — 年度  JSON 数组
- `dsapi-json-{year}.md` — 年度  MD 文件

## 🗂️ 归档

- 🐎 [2026](https://dsapi.bingmen.com/README-dsapi-2026.html)
- 🐍 [2025](https://dsapi.bingmen.com/README-dsapi-2025.html)
- 🐉 [2024](https://dsapi.bingmen.com/README-dsapi-2024.html)
- 🐇 [2023](https://dsapi.bingmen.com/README-dsapi-2023.html)
- 🐅 [2022](https://dsapi.bingmen.com/README-dsapi-2022.html)
- 🐂 [2021](https://dsapi.bingmen.com/README-dsapi-2021.html)
- 🐀 [2020](https://dsapi.bingmen.com/README-dsapi-2020.html)
- 🐖 [2019](https://dsapi.bingmen.com/README-dsapi-2019.html)
- 🐕 [2018](https://dsapi.bingmen.com/README-dsapi-2018.html)

## 📦 存储

- 🐎 [iciba-dsapi-2026](https://github.com/bingmen/iciba-dsapi-2026)
- 🐍 [iciba-dsapi-2025](https://github.com/bingmen/iciba-dsapi-2025)
- 🐉 [iciba-dsapi-2024](https://github.com/bingmen/iciba-dsapi-2024)
- 🐇 [iciba-dsapi-2023](https://github.com/bingmen/iciba-dsapi-2023)
- 🐅 [iciba-dsapi-2022](https://github.com/bingmen/iciba-dsapi-2022)
- 🐂 [iciba-dsapi-2021](https://github.com/bingmen/iciba-dsapi-2021)
- 🐀 [iciba-dsapi-2020](https://github.com/bingmen/iciba-dsapi-2020)
- 🐖 [iciba-dsapi-2019](https://github.com/bingmen/iciba-dsapi-2019)
- 🐕 [iciba-dsapi-2018](https://github.com/bingmen/iciba-dsapi-2018)

## 📚 参考

[金山词霸 · 开放平台](https://open.iciba.com/?c=wiki)

## 📄 许可证

[MIT](LICENSE)
"""


def today_shanghai() -> str:
    """返回 Asia/Shanghai 时区的今日日期，格式 YYYY-MM-DD。"""
    return datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d")


def fetch_dsapi(date: str) -> dict:
    """请求词霸每日一句 API，返回 JSON 对象。"""
    url = API_URL.format(today=date)
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=TIMEOUT) as resp:
        if resp.status != 200:
            raise RuntimeError(f"HTTP {resp.status}: {url}")
        raw = resp.read().decode("utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError(f"响应不是 JSON 对象: {data!r}")
    return data


def build_readme(data: dict) -> str:
    """用 JSON 字段 content / fenxiang_img 填充 README 模板。"""
    content = (data.get("content") or "").strip()
    fenxiang_img = (data.get("fenxiang_img") or "").strip()

    if not content:
        raise ValueError("JSON 响应缺少 content 字段")
    if not fenxiang_img:
        raise ValueError("JSON 响应缺少 fenxiang_img 字段")

    # 避免 content 中的方括号破坏 Markdown 图片替代文本
    safe_content = content.replace("[", "\\[").replace("]", "\\]")

    # README 模板中的 {year} 使用当前年份
    return README_TEMPLATE.format(
        content=safe_content,
        fenxiang_img=fenxiang_img,
        year=datetime.now(ZoneInfo("Asia/Shanghai")).year,
    )


def main() -> int:
    date = today_shanghai()
    print(f"[info] date  = {date}")
    print(f"[info] url   = {API_URL.format(today=date)}")

    try:
        data = fetch_dsapi(date)
        readme = build_readme(data)
    except Exception as exc:  # noqa: BLE001
        print(f"[error] {exc}", file=sys.stderr)
        return 1

    OUTPUT_FILE.write_text(readme, encoding="utf-8")
    print(f"[ok]   wrote {OUTPUT_FILE} ({len(readme)} chars)")
    print(f"[ok]   content     = {data.get('content')}")
    print(f"[ok]   fenxiang_img= {data.get('fenxiang_img')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
