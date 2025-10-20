# AAVE Arbitrum Monitor

Мониторит позиции на AAVE V3 в Arbitrum для заданных адресов. Выводит HF, коллатерал, долги и детали токенов. Отправляет отчёты в Telegram.

## Установка
1. `pip install -r requirements.txt`
2. Замени адреса, BOT_TOKEN, CHAT_ID в `aave_monitor.py`.
3. `python aave_monitor.py` — тест.

## Автоматизация
GitHub Actions: cron 2 раза/день (7:00/19:00 MSK). Секрет: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID.

## Локальный cron (Linux)
`crontab -e`: `0 4,16 * * * /usr/bin/python3 /path/to/aave_monitor.py >> /path/to/log.txt 2>&1`
