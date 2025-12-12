FROM python:3.11-slim

WORKDIR /app

COPY ../pyproject.toml ../setup.py /app/
RUN pip install --upgrade pip && pip install -e .

COPY ../polyscale_fl /app/polyscale_fl

ENV PYTHONUNBUFFERED=1

ARG CLIENT_ID=0
ENV CLIENT_ID=${CLIENT_ID}

CMD ["python", "-m", "polyscale_fl.client.client_node"]
