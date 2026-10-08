"""FastAPI backend. From the portfolio directory, run: uvicorn backend.main:app --reload."""
import json
import os
import time
import urllib.request
from collections import Counter
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .database import get_conn, init_db

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"

app = FastAPI(title="Adil Khan Portfolio API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
def _startup() -> None:
    init_db()


def rows(sql: str, args: tuple = ()) -> list[dict]:
    conn = get_conn()
    try:
        return [dict(r) for r in conn.execute(sql, args).fetchall()]
    finally:
        conn.close()


@app.get("/api/profile")
def profile():
    data = rows("SELECT * FROM profile WHERE id=1")
    if not data:
        raise HTTPException(404, "Profile not found")
    p = data[0]
    p["roles"] = json.loads(p["roles"])
    p["has_resume"] = (FRONTEND / "assets" / "resume.pdf").exists()
    return p


@app.get("/api/skills")
def skills():
    grouped: dict[str, list] = {}
    for s in rows("SELECT category,name,level FROM skills ORDER BY position"):
        grouped.setdefault(s["category"], []).append({"name": s["name"], "level": s["level"]})
    return [{"category": k, "items": v} for k, v in grouped.items()]


@app.get("/api/projects")
def projects():
    out = rows("SELECT * FROM projects ORDER BY position")
    for p in out:
        p["tech"] = json.loads(p["tech"])
    return out


@app.get("/api/education")
def education():
    return rows("SELECT * FROM education ORDER BY position")


@app.get("/api/achievements")
def achievements():
    return rows("SELECT * FROM achievements ORDER BY position")


@app.get("/api/hobbies")
def hobbies():
    return rows("SELECT * FROM hobbies ORDER BY position")


_cache: dict = {}


def gh_get(path: str):
    """Fetch from the GitHub API with a 10-minute cache (set GITHUB_TOKEN to raise rate limits)."""
    hit = _cache.get(path)
    if hit and time.time() - hit[0] < 600:
        return hit[1]
    headers = {"User-Agent": "portfolio", "Accept": "application/vnd.github+json"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    try:
        data = json.load(urllib.request.urlopen(urllib.request.Request("https://api.github.com" + path, headers=headers), timeout=8))
    except Exception:
        if hit:
            return hit[1]
        raise HTTPException(502, "GitHub unavailable")
    _cache[path] = (time.time(), data)
    return data


@app.get("/api/github")
def github():
    user = rows("SELECT github FROM profile WHERE id=1")[0]["github"]
    u = gh_get(f"/users/{user}")
    repos = [r for r in gh_get(f"/users/{user}/repos?per_page=100&sort=pushed") if not r["fork"]]
    top = sorted(repos, key=lambda r: (r["stargazers_count"], r["pushed_at"]), reverse=True)[:6]
    keep = ("name", "description", "html_url", "language", "stargazers_count", "forks_count", "pushed_at", "homepage")
    return {
        "user": {k: u.get(k) for k in ("login", "name", "bio", "avatar_url", "html_url", "public_repos", "followers", "following")},
        "stars": sum(r["stargazers_count"] for r in repos),
        "languages": Counter(r["language"] for r in repos if r["language"]).most_common(6),
        "repos": [{k: r.get(k) for k in keep} for r in top],
    }


@app.get("/api/stats")
def stats():
    return {
        "projects": rows("SELECT COUNT(*) c FROM projects")[0]["c"],
        "skills": rows("SELECT COUNT(*) c FROM skills")[0]["c"],
        "hackathons": rows("SELECT COUNT(*) c FROM achievements WHERE title LIKE '%Hackathon%'")[0]["c"],
        "visits": rows("SELECT value FROM stats WHERE key='visits'")[0]["value"],
    }


@app.post("/api/visit")
def visit():
    conn = get_conn()
    conn.execute("UPDATE stats SET value = value + 1 WHERE key='visits'")
    conn.commit()
    v = conn.execute("SELECT value FROM stats WHERE key='visits'").fetchone()[0]
    conn.close()
    return {"visits": v}


class Message(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    email: str = Field(min_length=3, max_length=120, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    message: str = Field(min_length=3, max_length=2000)


@app.post("/api/contact", status_code=201)
def contact(msg: Message):
    conn = get_conn()
    conn.execute("INSERT INTO messages(name,email,message) VALUES (?,?,?)",
                 (msg.name.strip(), msg.email.strip(), msg.message.strip()))
    conn.commit()
    conn.close()
    return {"ok": True, "detail": "Thanks! Your message has been saved."}


@app.get("/api/messages")
def messages(x_token: str = Header(default="")):
    """Inbox for the owner. Set ADMIN_TOKEN and send it as an X-Token header."""
    if not os.environ.get("ADMIN_TOKEN") or x_token != os.environ["ADMIN_TOKEN"]:
        raise HTTPException(403, "Forbidden")
    return rows("SELECT * FROM messages ORDER BY id DESC")


app.mount("/css", StaticFiles(directory=FRONTEND / "css"), name="css")
app.mount("/assets", StaticFiles(directory=FRONTEND / "assets"), name="assets")
app.mount("/js", StaticFiles(directory=FRONTEND / "js"), name="js")


@app.get("/resume.pdf")
def resume():
    f = FRONTEND / "assets" / "resume.pdf"
    if not f.exists():
        raise HTTPException(404, "No resume uploaded")
    return FileResponse(f, filename="Adil_Khan_Resume.pdf")


@app.get("/")
def index():
    return FileResponse(FRONTEND / "index.html")
