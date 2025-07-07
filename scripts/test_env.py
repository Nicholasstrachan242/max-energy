from dotenv import load_dotenv
import os

load_dotenv('.env.test', override=True)
print("Test env loaded with override.")
print("APP_ENV:", os.getenv("APP_ENV"))
print("DB_USER:", os.getenv("DB_USER"))
print("DB_NAME:", os.getenv("DB_NAME"))

load_dotenv('.env.prod', override=True)
print("Prod env loaded.")
print("APP_ENV:", os.getenv("APP_ENV"))
print("DB_USER:", os.getenv("DB_USER"))
print("DB_NAME:", os.getenv("DB_NAME"))

load_dotenv('.env.test', override=True)
print("Test env loaded again with override.")
print("APP_ENV:", os.getenv("APP_ENV"))
print("DB_USER:", os.getenv("DB_USER"))
print("DB_NAME:", os.getenv("DB_NAME"))
