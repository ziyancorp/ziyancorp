#!/usr/bin/env bash
# Wrapper cron: set env dari vault, jalanin distribute_agent.py
cd "C:/Users/arija/ziyancorp/ziyan_archive_bot" || exit 1
export FB_PAGE_TOKEN="$(bash /c/Users/arija/bin/token_vault.sh get fb_page_token 2>/dev/null | tr -d '\n')"
export THREADS_USER_TOKEN="$(bash /c/Users/arija/bin/token_vault.sh get threads_user_token 2>/dev/null | tr -d '\n')"
export INSTAGRAM_USER_TOKEN="$(bash /c/Users/arija/bin/token_vault.sh get instagram_user_token 2>/dev/null | tr -d '\n')"
export CHANNEL_CELINE="-1004373452633"
export GOOGLE_CREDENTIALS_FILE="client_secret.json"
export HERMES_CUSTOM_9ROUTER_API_KEY="$HERMES_CUSTOM_9ROUTER_API_KEY"
cd /c/Users/arija/ziyancorp/ziyan_archive_bot
exec ./venv/Scripts/python.exe distribute_agent.py
