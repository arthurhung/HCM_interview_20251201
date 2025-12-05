本專案將 **試題一的爬蟲服務容器化** ，並使用 **Apache Airflow** 建立排程，

使系統能每日自動抓取「衛福部國民健康署 – 保健闢謠」最新文章並更新 CSV。

---

# 📁 專案結構

<pre class="overflow-visible!" data-start="216" data-end="710"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-text"><span><span>project_root/
├── question_1/               # 試題一的爬蟲程式
│   ├── crawler.py
│   ├── csv_helper.py
│   ├── logger_setup.py
│   ├── requirements.txt
│   └── ...
└── question_2/
    ├── dags/
    │   └── hpa_crawler_dag.py     # Airflow 排程 DAG
    ├── data/                      # ← CSV 輸出目錄（本機可看）
    ├── logs/                      # Airflow 執行 Log
    ├── plugins/
    ├── Dockerfile                 # Airflow 自訂 Image（Python 3.12.3）
    ├── docker-compose.yml
    └── requirements.txt
</span></span></code></div></div></pre>

---

# 🚀 一、環境啟動方式

進入 `question_2/` 資料夾後：

<pre class="overflow-visible!" data-start="756" data-end="809"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>docker compose build
docker compose up -d
</span></span></code></div></div></pre>

服務會啟動：

* Postgres（Airflow metadata DB）
* Airflow Webserver（UI）
* Airflow Scheduler（定時排程執行爬蟲）

---

# 🌐 二、Airflow UI 登入

瀏覽器開啟：

<pre class="overflow-visible!" data-start="941" data-end="970"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>http:</span><span>//localhost:8080</span><span>
</span></span></code></div></div></pre>

登入：

* **Username:** `admin`
* **Password:** `admin`

（docker-compose 已自動建立管理者帳號）

---

# ⏰ 三、排程說明（DAG）

DAG 位置：

<pre class="overflow-visible!" data-start="1088" data-end="1130"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>question_2/dags/hpa_crawler_dag.py
</span></span></code></div></div></pre>

排程設定：

* 每天 **03:00** 自動執行
* 首次啟動可手動點擊 Airflow UI 的「▶ Trigger」

DAG 會執行：

1. 從 CSV 載入既有資料
2. 分析是否有新文章（增量更新）
3. 如有新文章 → 抓取內文並附加至 CSV
4. 如無新文章 → 任務成功結束

---

# 📦 四、產出資料位置

產出的 CSV 會寫入本機：

<pre class="overflow-visible!" data-start="1319" data-end="1363"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>question_2/data/hpa_health_myths.csv
</span></span></code></div></div></pre>

Docker volume 已設定對應，因此不會消失。

---

# 🐳 五、容器化說明

## 1. Dockerfile

`question_2/Dockerfile` 做了以下事情：

* 基於 `python:3.12.3-slim`
* 安裝 Airflow（含 postgres provider）
* 安裝爬蟲所需套件
* **把 question_1 的爬蟲程式完整複製到容器 `/opt/airflow/app`**
* 設定 `PYTHONPATH` 讓 DAG 可 import 該模組

## 2. docker-compose.yml

docker-compose 設定包括：

* Postgres 作為 Airflow metadata DB
* Airflow 使用 LocalExecutor
* 自動建立 admin 使用者
* 將本機 `dags/`, `logs/`, `data/` 掛載到容器中
* CSV 寫回本機 `data/`

---

# 🔍 六、如何驗證爬蟲成功

啟動後可執行：

<pre class="overflow-visible!" data-start="1840" data-end="1882"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>docker compose logs -f airflow
</span></span></code></div></div></pre>

DAG 執行後查看：

<pre class="overflow-visible!" data-start="1896" data-end="1940"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>question_2/data/hpa_health_myths.csv
</span></span></code></div></div></pre>

檔案應包含：

* pid
* title
* url
* publish_date
* update_date
* content（文章內文）

並會隨著網站更新產生增量資料。

---

# 🧹 七、停止與清除服務

<pre class="overflow-visible!" data-start="2054" data-end="2085"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>docker compose down
</span></span></code></div></div></pre>

如需清除 Postgres 資料：

<pre class="overflow-visible!" data-start="2106" data-end="2140"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>docker compose down -v</span></span></code></div></div></pre>
