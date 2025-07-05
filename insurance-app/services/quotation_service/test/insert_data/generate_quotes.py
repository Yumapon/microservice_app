# -*- coding: utf-8 -*-
import asyncio
import httpx
import random
from datetime import date

"""
実行コマンド
quotation_service/で実行すること

python3 test/insert_data/generate_quotes.py

"""

API_URL = "http://localhost:8000/api/v1/quotes/pension"
HEADERS = {
    "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJsbVVWYVViVEJ4TkV4M0l2djRlRjc5akU2SnhON2ZNVEVSRWI1SFV5RVhzIn0.eyJleHAiOjE3NTE1MTQyMzgsImlhdCI6MTc1MTUxMjQzOCwianRpIjoiOWEwOGY5NGYtMDdiMS00MTJlLTk5ZmUtNDkxODJlYThiNjk1IiwiaXNzIjoiaHR0cDovL2xvY2FsaG9zdDo4MDgwL3JlYWxtcy9pbnRlcm5ldC1zZXJ2aWNlLXJlbG0iLCJhdWQiOlsiaW5zdXJhbmNlLWFwcCIsImFjY291bnQiXSwic3ViIjoiYzI1ODQ4MGYtNjdmMy00ZmM5LWI2NTgtMzhkM2JlZjg2MmY2IiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiaW5zdXJhbmNlLWFwcCIsInNlc3Npb25fc3RhdGUiOiJmNGYxMzAxMy1kOGI3LTRlNDgtOTNhYy03NWZlNTc1YTdiYzciLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHA6Ly9sb2NhbGhvc3Q6ODA4MCJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiIsImRlZmF1bHQtcm9sZXMtaW50ZXJuZXQtc2VydmljZS1yZWxtIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiaW5zdXJhbmNlLWFwcCI6eyJyb2xlcyI6WyJhcHBsaWNhdGlvbl93cml0ZXIiLCJhcHBsaWNhdGlvbl9yZWFkZXIiLCJxdW90ZV93cml0ZXIiXX0sImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoicHJvZmlsZSBhcHBsaWNhdGlvbiBxdW90ZSBlbWFpbCIsInNpZCI6ImY0ZjEzMDEzLWQ4YjctNGU0OC05M2FjLTc1ZmU1NzVhN2JjNyIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwicHJlZmVycmVkX3VzZXJuYW1lIjoib2thbW90b3l1bWEiLCJlbWFpbCI6Imtlcm9wb24xMjc0QGdtYWlsLmNvbSJ9.B9ei-wbQW9_yUyV5Nl52GD4rxChiKM37VG7hFXl3WIET12Pe1OgZPyes8w1H74zPjoNEAe8p06nB8tzW-na3rv3FUYHr2xNNIXiIV_8KknViBbjZgkQsHlmMKk9DxZ2hdXATV3tbWfQh5IfZ-3h5TnRLQfwkL35Rqlk1Hbw9W5xz2QqXwwXmdyZf5Z72O5Fdu5ACujg_wZmJbG0Px354I-aj_hGA1k0wLEOt2NpGySKYQs5aWGCF8fytILuiSJu5sB2iwV1gT4RJ04nbIM6SVsD0TdLq_Rq0HqtW8fCf-_ik8DIyTQQuOiGhBmWpSptNfoas3JUZhuKq5U4elqmSfQ",  # ← 認証トークンをここに
    "Content-Type": "application/json"
}

# 条件を満たすデータのみ使用（validationに通るもの）
VALID_MONTHLY_PREMIUMS = [10000, 20000, 30000, 40000]
VALID_PAYMENT_PERIOD_YEARS = [15, 20, 25, 30]  # 必ず15以上
VALID_PENSION_PAYMENT_YEARS = [5, 10, 15]
VALID_GENDERS = ["male", "female"]

async def post_quote(client, idx):
    payload = {
        "birth_date": str(date(1990 + idx % 10, 1, 1)),
        "gender": random.choice(VALID_GENDERS),
        "monthly_premium": random.choice(VALID_MONTHLY_PREMIUMS),
        "payment_period_years": random.choice(VALID_PAYMENT_PERIOD_YEARS),
        "pension_payment_years": random.choice(VALID_PENSION_PAYMENT_YEARS),
        "tax_deduction_enabled": random.choice([True, False])
    }
    try:
        resp = await client.post(API_URL, json=payload, headers=HEADERS)
        if resp.status_code == 200:
            print(f"[{idx}] 成功: quote_id = {resp.json().get('quote_id')}")
        else:
            print(f"[{idx}] 失敗: status = {resp.status_code}, msg = {resp.text}")
    except Exception as e:
        print(f"[{idx}] エラー: {e}")

async def main():
    async with httpx.AsyncClient() as client:
        tasks = [post_quote(client, i) for i in range(1, 101)]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())