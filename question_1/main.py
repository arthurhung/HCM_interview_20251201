"""
爬取 衛生福利部國民健康署「保健闢謠」文章內容
- 第一次執行：初始化，抓前 10 篇文章寫入 CSV
- 之後執行：做增量更新，只抓 CSV 尚未存在的新文章，並 append

依賴套件：
    pip install requests beautifulsoup4
"""

import os
import csv
import re
import time
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.hpa.gov.tw"
TOPIC_LIST_URL = f"{BASE_URL}/Pages/TopicList.aspx?nodeid=127"
CSV_FILE = "./hpa_health_myths.csv"

REQUEST_SLEEP_SECONDS = 0.8
TIMEOUT_SECONDS = 10
DATE_PATTERN = re.compile(r"(\d{4}/\d{2}/\d{2})")
MAX_NEWS_ROWS = 1
MAX_READ_PAGES = 1

def fetch_html(url: str) -> str:
    """發送 HTTP GET 取得 HTML 文字."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=TIMEOUT_SECONDS)
    resp.raise_for_status()
    # 網站本身是 UTF-8，保險起見指定一下
    resp.encoding = resp.apparent_encoding
    time.sleep(REQUEST_SLEEP_SECONDS)
    return resp.text


def extract_date(base_node, label: str) -> str:
    """
    從 base_node 之後的文字節點中，找到包含指定 label 的文字，
    然後用正規表示式抓出 yyyy/mm/dd 日期。
    """
    node = base_node.find_next(string=lambda s: s and label in s)
    if not node:
        return ""

    text = node.get_text(strip=True) if hasattr(node, "get_text") else str(node)
    # 支援「發布日期：」「更新Ｆ日期:」等格式
    m = re.search(rf"{re.escape(label)}[:：]\s*{DATE_PATTERN.pattern}", text)
    return m.group(1) if m else ""


def parse_list_page(html: str) -> List[Dict]:
    """
    解析保健闢謠列表頁，回傳文章 metadata list：
    [
        {
            "pid": "18421",
            "title": "...",
            "url": "https://www.hpa.gov.tw/Pages/Detail.aspx?nodeid=127&pid=18421",
            "publish_date": "2025/11/25",
            "update_date": "2025/07/04",
        },
        ...
    ]
    """
    soup = BeautifulSoup(html, "html.parser")
    articles: List[Dict] = []

    # 1. 找出所有 Detail.aspx 連結
    for a in soup.find_all("a", href=True):
        # ex: <a href="/Pages/Detail.aspx?nodeid=127&pid=19182" title="乳房自我檢查無異常，就不用定期做乳房攝影篩檢？">
        href = a["href"]

        if "Pages/Detail.aspx" not in href:
            continue
        if "nodeid=127" not in href:
            continue

        title = a.get_text(strip=True)
        if not title:
            continue

        # 補成完整 URL
        if href.startswith("http"):
            url = href
        else:
            url = BASE_URL + href

        # 從 URL 抓出 pid
        pid_match = re.search(r"pid=(\d+)", href)
        pid = pid_match.group(1) if pid_match else None

        # 2. 找到緊接著的「發布日期：xxxx 更新日期：xxxx」那行文字
        publish_date = extract_date(a, "發布日期")
        update_date = extract_date(a, "更新日期")

        articles.append(
            {
                "pid": pid,
                "title": title,
                "url": url,
                "publish_date": publish_date,
                "update_date": update_date,
            }
        )

    # 3. 因為頁面上其他區塊也可能有 Detail 連結，去重（以 pid 為 key）並維持出現順序
    seen = set()
    unique_articles: List[Dict] = []
    for art in articles:
        key = art["pid"] or art["url"]
        if key in seen:
            continue
        seen.add(key)
        unique_articles.append(art)

    return unique_articles


def fetch_list_page(idx: int = 0) -> List[Dict]:
    """
    取得某一頁的列表資料：
    https://...TopicList.aspx?nodeid=127&idx={idx}
    """
    url = f"{TOPIC_LIST_URL}&idx={idx}"

    html = fetch_html(url)
    articles = parse_list_page(html)
    return articles


def extract_article_content(html: str, title: Optional[str] = None) -> str:
    """
    將文章內頁整頁文字取出，再用關鍵字做切分：
    - 從「發布日期：」後面開始
    - 到「您可能會喜歡」或「看完本篇主題後」之前
    這段視為實際文章內容。
    """
    soup = BeautifulSoup(html, "html.parser")
    full_text = soup.get_text("\n")
    # 把連續很多空行壓縮一下
    full_text = re.sub(r"\n{2,}", "\n", full_text)

    start_idx = 0

    # 優先以「發布日期：」當起點
    idx = full_text.find("發布日期：")
    if idx != -1:
        # 跳到下一行後開始算內容
        next_newline = full_text.find("\n", idx)
        start_idx = next_newline + 1 if next_newline != -1 else idx
    elif title and title in full_text:
        # fallback：找不到發布日期就從標題後開始
        start_idx = full_text.find(title) + len(title)

    # 結束點：嘗試切到「您可能會喜歡」或「看完本篇主題後」
    end_idx = full_text.find("上一則", start_idx)
    if end_idx == -1:
        end_idx = full_text.find("下一則", start_idx)
    if end_idx == -1:
        end_idx = len(full_text)

    content = full_text[start_idx:end_idx].strip()
    return content


def load_existing_csv(path: str) -> List[Dict]:
    """讀取現有 CSV（若不存在則回傳空 list）"""
    if not os.path.exists(path):
        return []
    rows: List[Dict] = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def save_csv(path: str, rows: List[Dict]) -> None:
    """覆寫 CSV（初始化用）"""
    if not rows:
        return
    fieldnames = [
        "pid",
        "title",
        "url",
        "publish_date",
        "update_date",
        "content",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def append_to_csv(path: str, rows: List[Dict]) -> None:
    """將新資料 append 到既有 CSV"""
    if not rows:
        return
    file_exists = os.path.exists(path)
    fieldnames = [
        "pid",
        "title",
        "url",
        "publish_date",
        "update_date",
        "content",
    ]
    mode = "a" if file_exists else "w"
    with open(path, mode, encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for r in rows:
            writer.writerow(r)


def initial_crawl_top10() -> None:
    """第一次執行：抓列表第 1 頁前 10 篇，含內文，寫入 CSV。"""
    print("=== 初始化：抓取保健闢謠前 10 篇文章 ===")
    articles = fetch_list_page(idx=0)
    top10 = articles[:MAX_NEWS_ROWS]

    rows: List[Dict] = []
    for art in top10:
        print(f"抓取文章：{art['title']} ({art['url']})")
        detail_html = fetch_html(art["url"])
        content = extract_article_content(detail_html, title=art["title"])

        row = {
            "pid": art["pid"],
            "title": art["title"],
            "url": art["url"],
            "publish_date": art["publish_date"],
            "update_date": art["update_date"],
            "content": content,
        }
        rows.append(row)

    save_csv(CSV_FILE, rows)
    print(f"完成，已寫入 {CSV_FILE}，共 {len(rows)} 筆。")


def incremental_update(max_pages: int = MAX_READ_PAGES) -> None:
    """
    增量更新：
    - 讀取現有 CSV 的 pid 集合
    - 從列表第 1 頁開始往後翻，找到 pid 尚未出現的文章
    - 對所有新文章抓內文並 append 到 CSV
    - max_pages：避免無限翻頁，這裡預設最多看前 5 頁
    """
    existing_rows = load_existing_csv(CSV_FILE)
    existing_ids = {row.get("pid") for row in existing_rows if row.get("pid")}
    print(f"現有 CSV 筆數：{len(existing_rows)}，distinct pid：{len(existing_ids)}")

    new_articles: List[Dict] = []

    for idx in range(0, max_pages):
        print(f"檢查列表第 {idx + 1} 頁...")
        page_articles = fetch_list_page(idx=idx)
        if not page_articles:
            print("此頁無資料，停止。")
            break
        print(max_pages)
        page_new = [a for a in page_articles if a["pid"] not in existing_ids]
        # 只要這頁所有文章都已存在，就可以合理判斷後面頁數也不會有更新版（最新在前）
        if not page_new:
            print("此頁所有文章都已在 CSV 中，停止往後翻頁。")
            break

        for a in page_new:
            print(f"發現新文章：{a['title']} ({a['url']})")
        new_articles.extend(page_new)

    if not new_articles:
        print("沒有發現新文章，CSV 無需更新。")
        return

    # 抓新文章內文並 append
    new_rows: List[Dict] = []
    for art in new_articles:
        print(f"抓取新文章內文：{art['title']}")
        detail_html = fetch_html(art["url"])
        content = extract_article_content(detail_html, title=art["title"])
        row = {
            "pid": art["pid"],
            "title": art["title"],
            "url": art["url"],
            "publish_date": art["publish_date"],
            "update_date": art["update_date"],
            "content": content,
        }
        new_rows.append(row)

    append_to_csv(CSV_FILE, new_rows)
    print(f"增量更新完成，新增 {len(new_rows)} 筆。")


def main():
    if not os.path.exists(CSV_FILE):
        # 第一次執行：初始化
        initial_crawl_top10()
    else:
        # 之後執行：增量
        incremental_update()


if __name__ == "__main__":
    main()
