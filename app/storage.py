import json, os
from datetime import datetime, timezone
from sqlalchemy import create_engine, text

def _make_engine():
    url = os.getenv("DATABASE_URL", "sqlite:///./claims_demo.db")
    connect_args = {"check_same_thread":False} if url.startswith("sqlite") else {}
    return create_engine(url, future=True, pool_pre_ping=True, connect_args=connect_args)
engine = _make_engine()

def init_db():
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS claims (case_id VARCHAR(40) PRIMARY KEY, created_at VARCHAR(40) NOT NULL, status VARCHAR(40) NOT NULL, payload TEXT NOT NULL)"))

def save_case(case_id: str, status: str, payload: dict):
    with engine.begin() as conn:
        conn.execute(text("""INSERT INTO claims(case_id,created_at,status,payload) VALUES(:id,:created,:status,:payload)
        ON CONFLICT(case_id) DO UPDATE SET status=excluded.status,payload=excluded.payload"""), {"id":case_id,"created":datetime.now(timezone.utc).isoformat(),"status":status,"payload":json.dumps(payload, default=str)})

def get_case(case_id: str):
    with engine.begin() as conn:
        row=conn.execute(text("SELECT payload FROM claims WHERE case_id=:id"), {"id":case_id}).fetchone()
    return json.loads(row[0]) if row else None

def list_cases(limit: int=50):
    with engine.begin() as conn:
        rows=conn.execute(text("SELECT payload FROM claims ORDER BY created_at DESC LIMIT :lim"), {"lim":limit}).fetchall()
    return [json.loads(row[0]) for row in rows]
