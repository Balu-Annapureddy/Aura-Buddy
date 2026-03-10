import psycopg2
import traceback

SUPABASE_URL = "postgresql://postgres:Aura@buddy@1@db.gvneccixeojhxwbbzsbz.supabase.co:5432/postgres"

try:
    print("Testing connection...")
    conn = psycopg2.connect(SUPABASE_URL, connect_timeout=5)
    print("SUCCESS! Connected to Supabase.")
    conn.close()
except psycopg2.OperationalError as e:
    print("OPERATIONAL ERROR:")
    print(e)
except Exception as e:
    print("OTHER ERROR:")
    traceback.print_exc()
