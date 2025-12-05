# Jednoduchý Dockerfile pro Browser Use + Gradio UI na Renderu

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Základní systémové balíčky (můžeš ubrat/přidat podle potřeby)
RUN apt-get update -qq \
    && apt-get install -y --no-install-recommends \
        curl \
        wget \
        ca-certificates \
        chromium \
        fonts-liberation \
        fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/chromium /usr/bin/chromium-browser || true

WORKDIR /app

# Zkopíruj celý projekt (kvůli gradio_demo.py)
COPY . /app

# Nainstaluj python závislosti:
# - browser-use (z PyPI)
# - gradio (UI)
# - python-dotenv, rich (používá je gradio_demo)
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir \
        "browser-use[cli]" \
        gradio \
        python-dotenv \
        rich

# Render ti předá PORT env var, ale fallback je 7860
ENV PORT=7860

EXPOSE 7860

# Spustíme Gradio demo UI
CMD ["python", "examples/ui/gradio_demo.py"]
