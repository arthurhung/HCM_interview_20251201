# question_2/Dockerfile
FROM python:3.12.3-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    AIRFLOW_HOME=/opt/airflow

# === 安裝系統依賴 ===
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    default-libmysqlclient-dev \
    libsasl2-dev \
    libssl-dev \
    libffi-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# === 建 airflow 使用者 & 目錄 ===
RUN useradd -ms /bin/bash airflow && \
    mkdir -p ${AIRFLOW_HOME} && \
    mkdir -p ${AIRFLOW_HOME}/app && \
    mkdir -p ${AIRFLOW_HOME}/data && \
    chown -R airflow:airflow ${AIRFLOW_HOME}

WORKDIR ${AIRFLOW_HOME}

# === 先用 root 安裝 Python 套件（Airflow + 爬蟲依賴）===
# 這裡直接沿用 question_1/requirements.txt + question_2/requirements.txt
COPY question_1/requirements.txt /tmp/requirements_q1.txt
COPY question_2/requirements.txt /tmp/requirements_q2.txt

RUN pip install "apache-airflow[postgres]==2.10.2" && \
    pip install -r /tmp/requirements_q1.txt && \
    pip install -r /tmp/requirements_q2.txt

# === 切換為 airflow 使用者 ===
USER airflow

# === 把 question_1 整個程式碼包進容器 ===
COPY --chown=airflow:airflow question_1/ ${AIRFLOW_HOME}/app/

# === 讓 /opt/airflow/app 變成 Python 的 import path ===
ENV PYTHONPATH="${PYTHONPATH}:${AIRFLOW_HOME}/app"

# 關掉預設的範例 DAG
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
