# Ledgerline ERP sandbox + agent API + Temporal worker, one container (Lecture 7).
# Build context = the course root:   docker build -f deploy/Dockerfile -t ledgerline-agent:0.7.0 .
# In the course this is built on Modal (deploy/build_check.py), never on a laptop.
#
# Secrets are NOT baked in. They arrive as environment variables from the platform's secret store
# (Modal secret ledgerline-<env>, or your cluster's). The image is the same for dev, staging and prod;
# only deploy/env/<env>.env and the secrets differ.

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 \
    LEDGER_ENV=dev LEDGER_TEMPORAL=time_skipping LEDGER_LLM_MODE=live PORT=8080

WORKDIR /app

# 1. dependencies first (cached layer): the package metadata only
COPY ledgerline/pyproject.toml /app/ledgerline/pyproject.toml
COPY ledgerline/ledgerline/__init__.py /app/ledgerline/ledgerline/__init__.py
RUN pip install --upgrade pip && pip install "/app/ledgerline[all]" && pip uninstall -y ledgerline-erp

# 2. the code: the Ledgerline package (ERP, agent, durable workflow) and the deploy entrypoint
COPY ledgerline /app/ledgerline
COPY deploy /app/deploy
RUN pip install --no-deps -e /app/ledgerline \
 && python -c "import ledgerline, ledgerline.durable.workflow, deploy.versions" \
 && python -m deploy.versions --check

# Note: LEDGER_TEMPORAL=time_skipping/local download a Temporal test/dev server binary on first start (dev only).
# Staging and prod use LEDGER_TEMPORAL=connect (a real cluster at TEMPORAL_ADDRESS) and download nothing.

# One uvicorn worker: the sandbox ERP lives in this process's memory, and so does the Temporal worker.
RUN useradd --create-home --uid 10001 ledgerline && mkdir -p /var/ledgerline && chown ledgerline /var/ledgerline
USER ledgerline
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request,os; urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\",\"8080\")}/healthz', timeout=4)"

CMD ["sh", "-c", "uvicorn deploy.app:app --host 0.0.0.0 --port ${PORT} --workers 1"]
