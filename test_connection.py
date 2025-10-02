import os
from dotenv import load_dotenv
import psycopg

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("Testing database connection...")
print(
    f"Database URL: {DATABASE_URL[:50]}..."
    if DATABASE_URL
    else "No DATABASE_URL found!"
)

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not found in .env file")
    exit(1)

ssl_modes = ["require", "prefer", "allow", "disable"]

for ssl_mode in ssl_modes:
    try:
        # Modify URL with different SSL mode
        if "?" in DATABASE_URL:
            base_url = DATABASE_URL.split("?")[0]
        else:
            base_url = DATABASE_URL

        test_url = f"{base_url}?sslmode={ssl_mode}"

        print(f"\n⏳ Attempting connection with sslmode={ssl_mode}...")
        conn = psycopg.connect(test_url)
        print(f"✅ Connection successful with sslmode={ssl_mode}!")

        # Test a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL version: {version[0][:50]}...")

        cursor.close()
        conn.close()
        print(f"\n✅ SUCCESS! Use this in your .env:")
        print(f"DATABASE_URL={test_url}")
        break

    except Exception as e:
        print(f"❌ Failed with sslmode={ssl_mode}")
        print(f"   Error: {str(e)[:100]}...")

else:
    print("\n❌ All SSL modes failed!")
    print("\nPossible issues:")
    print("1. Your Neon database might be suspended - check Neon dashboard")
    print("2. Your IP might be blocked - check Neon IP allowlist")
    print("3. Database credentials might be wrong")
    print("4. Network/firewall blocking the connection")
