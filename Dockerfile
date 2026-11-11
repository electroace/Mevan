FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.lock ./
RUN apt-get update \
    && apt-get install -y --no-install-recommends fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/* \
    && test -f /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf \
    && pip install --no-cache-dir -r requirements.lock \
    && useradd --create-home mevan
COPY --chown=mevan:mevan server.py index.html diagnostic_engine.py data_quality_gate.py ./
COPY --chown=mevan:mevan mevan_*.py approved_reports.py diagnostic_review.html ./
COPY --chown=mevan:mevan project_*.py projects_ui.html dashboard_ui.html ./
COPY --chown=mevan:mevan fonts ./fonts
RUN mkdir -p /data && chown mevan:mevan /data
USER mevan
EXPOSE 8000
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "127.0.0.1"]
