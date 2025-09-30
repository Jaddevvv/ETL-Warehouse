from dotenv import load_dotenv
import os, sys

load_dotenv()
pem = os.getenv("SNOWFLAKE_PRIVATE_KEY")
if pem is None:
    sys.exit("SNOWFLAKE_PRIVATE_KEY not set")

print("First 60 chars:", repr(pem[:60]))
