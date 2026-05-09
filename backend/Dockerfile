FROM python:3.12-slim

WORKDIR /app

RUN groupadd -r oco && useradd -r -g oco oco

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data/media && chown -R oco:oco /app/data

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER oco

EXPOSE 8000

CMD ["/entrypoint.sh"]
