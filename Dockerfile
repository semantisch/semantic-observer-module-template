FROM python:3.12-slim
WORKDIR /module
COPY observer_module ./observer_module
COPY module.json ./module.json
USER 65532:65532
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "-m", "observer_module.main"]
