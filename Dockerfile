FROM python:3.11-alpine as builder


WORKDIR /app


RUN apk add --no-cache build-base postgresql-dev

RUN pip install wheel


COPY requirements.txt .


RUN pip wheel --no-cache-dir --wheel-dir=/app/wheels -r requirements.txt



FROM python:3.11-alpine

WORKDIR /app


RUN addgroup -S appgroup && adduser -S appuser -G appgroup

COPY --from=builder /app/wheels /app/wheels


RUN pip install --no-cache-dir /app/wheels/*


COPY main.py .


USER appuser


EXPOSE 8000


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]