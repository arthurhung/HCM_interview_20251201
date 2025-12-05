# HCM_interview_20251201

本專案從衛生福利部國民健康署網站的 **「保健闢謠」專區** 自動擷取文章內容，並輸出為  **CSV 檔** 。

同時支援：

* **初始化蒐集** （抓取前 N 篇文章）
* **增量更新** （只抓 CSV 中沒有的新文章）

---

## 功能說明

### ✔ 初始化蒐集

第一次執行時（CSV 尚不存在）會：

1. 讀取列表頁
2. 抓取前 N 篇（預設 10 篇）
3. 逐篇解析內文與 metadata
4. 寫入 `hpa_health_myths.csv`

---

### ✔ 增量更新

再次執行時（CSV 已存在）會：

1. 讀取現有 CSV
2. 比對 `pid` 是否已存在
3. 只蒐集網站上的 **新文章**
4. append 寫入 CSV，不覆蓋舊資料

---

## 輸出欄位（CSV）

* `pid`
* `title`
* `url`
* `publish_date`
* `update_date`
* `content`（已移除發布日期、點閱數、上一則/下一則等 meta 行）

---

## 專案結構

<pre class="overflow-visible!" data-start="579" data-end="719"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>csv_helper.py           </span><span># CSV 工具</span><span>
health_myth_crawler.py  </span><span># 核心爬蟲</span><span>
logger_setup.py         </span><span># Logger 設定（可選）</span><span>
main.py                 </span><span># 入口</span><span>
</span></span></code></div></div></pre>

執行後會產生：

<pre class="overflow-visible!" data-start="730" data-end="775"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>hpa_health_myths.csv
logs/crawler.log
</span></span></code></div></div></pre>

---

## 安裝與執行

## Python版本

```
3.12.3
```

### 安裝套件

```
pip install -r requirements.txt
```

### 執行爬蟲

<pre class="overflow-visible!" data-start="859" data-end="885"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>python main.py
</span></span></code></div></div></pre>

---

## 可調整參數

在 `main.py`：

<pre class="overflow-visible!" data-start="1088" data-end="1140"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-python"><span><span>crawler.run(initial_n=</span><span>10</span><span>, max_pages=</span><span>5</span><span>)
</span></span></code></div></div></pre>

* `initial_n`：首次抓取篇數(最大10筆)
* `max_pages`：增量更新時最多掃描的列表頁數
