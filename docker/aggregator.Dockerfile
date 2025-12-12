FROM python:3.11-slim

WORKDIR /app

COPY ../pyproject.toml ../setup.py /app/
RUN pip install --upgrade pip && pip install -e .

COPY ../polyscale_fl /app/polyscale_fl

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "polyscale_fl.aggregator.aggregator_node"]
