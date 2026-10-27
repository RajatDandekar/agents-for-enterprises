# Bahi ERP sandbox + agent API + Temporal worker, one container (Lecture 7).
# Build context = the course root:   docker build -f deploy/Dockerfile -t bahi-agent:0.7.0 .
# In the course this is built on Modal (deploy/build_check.py), never on a laptop.
#
# Secrets are NOT baked in. They arrive as environment variables from the platform's secret store
# (Modal secret bahi-<env>, or your cluster's). The image is the same for dev, staging and prod;
# only deploy/env/<env>.env and the secrets differ.

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 \
    BAHI_ENV=dev BAHI_TEMPORAL=time_skipping BAHI_LLM_MODE=live PORT=8080

WORKDIR /app

# 1. dependencies first (cached layer): the package metadata only
COPY bahi/pyproject.toml /app/bahi/pyproject.toml
COPY bahi/bahi/__init__.py /app/bahi/bahi/__init__.py
RUN pip install --upgrade pip && pip install "/app/bahi[server,durable]" && pip uninstall -y bahi-erp

# 2. the code: the Bahi package (ERP, agent, durable workflow) and the deploy entrypoint
COPY bahi /app/bahi
COPY deploy /app/deploy
RUN pip install --no-deps -e /app/bahi \
 && python -c "import bahi, bahi.durable.workflow, deploy.versions" \
 && python -m deploy.versions --check

# Note: BAHI_TEMPORAL=time_skipping/local download a Temporal test/dev server binary on first start (dev only).
# Staging and prod use BAHI_TEMPORAL=connect (a real cluster at TEMPORAL_ADDRESS) and download nothing.

# One uvicorn worker: the sandbox ERP lives in this process's memory, and so does the Temporal worker.
RUN useradd --create-home --uid 10001 bahi && mkdir -p /var/bahi && chown bahi /var/bahi
USER bahi
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request,os; urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\",\"8080\")}/healthz', timeout=4)"

CMD ["sh", "-c", "uvicorn deploy.app:app --host 0.0.0.0 --port ${PORT} --workers 1"]
