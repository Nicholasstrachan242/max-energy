from dotenv import load_dotenv
import os

load_dotenv('.env.test', override=True)
print("Test env loaded.")
print("DB_USER:", os.getenv("DB_USER"))
print("DB_NAME:", os.getenv("DB_NAME"))

load_dotenv('.env.prod', override=True)
print("Prod env loaded.")
print("DB_USER:", os.getenv("DB_USER"))
print("DB_NAME:", os.getenv("DB_NAME"))

load_dotenv('.env.test', override=True)
print("Test env loaded again with override.")
print("DB_USER:", os.getenv("DB_USER"))
print("DB_NAME:", os.getenv("DB_NAME"))

# TODO:
# Using override seems to help with making sure the correct env variables are loaded.
# Next steps: 
# - get the server test db working and be able to establish connection to the test and prod predictably
# - import and create the users in the server test db