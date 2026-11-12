FROM python:3.12-alpine

WORKDIR /srv/api

# Esta capa se reutiliza cuando cambia app/ pero no requirements.txt.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN addgroup -S api && adduser -S -G api api
COPY --chown=api:api app/ ./app/

USER api
EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import sys, urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health/ready', timeout=3).status == 200 else 1)"

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
