## ------------------------------- Build ------------------------------ ## 
FROM python:3.11-bookworm AS builder

RUN apt update && apt install --no-install-recommends -y \
        build-essential && \
    apt clean && rm -rf /var/lib/apt/lists/*


ADD https://astral.sh/uv/install.sh /install.sh
RUN chmod -R 655 /install.sh && /install.sh && rm /install.sh


ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

COPY ./pyproject.toml .

RUN uv sync


## ------------------------------- Production ------------------------------ ##
FROM python:3.11-slim-bookworm AS production


RUN adduser --disabled-password appuser
USER appuser

WORKDIR /app
COPY /app .

COPY --from=builder /app/.venv .venv

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["run.sh"]