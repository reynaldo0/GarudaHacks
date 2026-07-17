import socket
import sys

host = "187.77.138.233"
port = 5432

print(f"Testing connection to {host}:{port}...")
s = socket.socket()
s.settimeout(8)
try:
    s.connect((host, port))
    print("Port 5432: OPEN - TCP connection successful")
    s.close()
except socket.timeout:
    print("Port 5432: TIMEOUT - server unreachable or firewall blocking")
    sys.exit(1)
except ConnectionRefusedError:
    print("Port 5432: REFUSED - port open but no service listening")
    sys.exit(1)
except Exception as e:
    print(f"Port 5432: ERROR - {e}")
    sys.exit(1)

print("\nTesting PostgreSQL with SQLAlchemy...")
try:
    from sqlalchemy import create_engine, text
    from app.config.settings import settings
    print(f"DATABASE_URL: {settings.DATABASE_URL}")
    e = create_engine(settings.DATABASE_URL, connect_args={"connect_timeout": 8})
    with e.connect() as conn:
        r = conn.execute(text("SELECT version()"))
        ver = r.fetchone()[0]
        print(f"PostgreSQL connected: {ver}")
        r2 = conn.execute(text("SELECT current_database()"))
        db = r2.fetchone()[0]
        print(f"Current database: {db}")
        r3 = conn.execute(text("SELECT current_user"))
        user = r3.fetchone()[0]
        print(f"Current user: {user}")
        r4 = conn.execute(text("SELECT schemaname, tablename FROM pg_tables WHERE schemaname='public'"))
        tables = r4.fetchall()
        print(f"Tables in public schema: {len(tables)}")
        for t in tables:
            print(f"  - {t[1]}")
    print("\nDatabase connection: OK")
except Exception as e:
    print(f"Database connection FAILED: {e}")
    sys.exit(1)
