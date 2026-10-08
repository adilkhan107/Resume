"""SQLite layer + seed data taken from Adil Khan's resume."""
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "portfolio.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS profile (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    name TEXT, title TEXT, tagline TEXT, objective TEXT,
    email TEXT, phone TEXT, location TEXT, github TEXT, roles TEXT
);
CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT, name TEXT, level INTEGER, position INTEGER
);
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT, subtitle TEXT, description TEXT, tech TEXT,
    badge TEXT, icon TEXT, link TEXT, position INTEGER
);
CREATE TABLE IF NOT EXISTS education (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    degree TEXT, level TEXT, institution TEXT, period TEXT, result TEXT,
    current INTEGER DEFAULT 0, position INTEGER
);
CREATE TABLE IF NOT EXISTS achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT, detail TEXT, icon TEXT, position INTEGER
);
CREATE TABLE IF NOT EXISTS hobbies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, icon TEXT, position INTEGER
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, email TEXT, message TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS stats (
    key TEXT PRIMARY KEY, value INTEGER DEFAULT 0
);
"""

PROFILE = dict(
    name="Adil Khan",
    title="B.Tech CSE (AI & ML) Student",
    tagline="Building intelligent solutions for real-world problems.",
    objective=(
        "Motivated and ambitious undergraduate student pursuing a B.Tech in CSE with AI & ML "
        "at Mind Power University. Eager to apply my academic knowledge, problem-solving and "
        "communication skills in a practical work environment. Looking for an internship or "
        "entry-level position to gain hands-on experience, grow professionally and contribute "
        "to the company's goals."
    ),
    email="sohilkhan07610760@gmail.com",
    phone="7983935099",
    location="Milak Amawati, Moradabad (UP)",
    github="adilkhan107",
    roles=json.dumps([
        "AI & ML Enthusiast",
        "Hackathon Winner",
        "Python Developer",
        "Problem Solver",
    ]),
)

# (category, name, level, position)
SKILLS = [
    ("Python Libraries", "Pandas", 80, 1),
    ("Python Libraries", "NumPy", 80, 2),
    ("Python Libraries", "Seaborn", 75, 3),
    ("Python Libraries", "OpenCV", 70, 4),
    ("Programming Languages", "C", 80, 5),
    ("Programming Languages", "C++ (basic)", 55, 6),
    ("Programming Languages", "Java (basic)", 50, 7),
    ("Web", "HTML", 80, 8),
    ("Web", "CSS", 75, 9),
    ("Core CS", "Data Structures (using C)", 75, 10),
]

PROJECTS = [
    ("AI HealthPredict",
     "AI-Powered Rural Healthcare Assistant",
     "An AI-powered healthcare assistant built for rural communities. "
     "Won 1st Prize at Hackathon 2026 (Rural Healthcare Track, Mind Power University).",
     ["Python", "AI / ML", "Healthcare"], "1st Prize · Hackathon 2026", "🩺",
     "https://github.com/adilkhan107", 1),
    ("Face Authentication System",
     "Secure identity verification",
     "A face-authentication system that recognises users from their facial features "
     "to provide contactless, secure access.",
     ["Python", "OpenCV", "Computer Vision"], "Computer Vision", "🧑‍💻",
     "https://github.com/adilkhan107", 2),
    ("Medi Nearby",
     "Find medical help close to you",
     "A utility that helps users quickly locate nearby medical facilities and "
     "healthcare services.",
     ["HTML", "CSS", "JavaScript"], "Web App", "📍",
     "https://github.com/adilkhan107", 3),
    ("AI Chatbot",
     "Conversational assistant",
     "A chatbot that understands user questions and replies conversationally.",
     ["Python", "NLP", "AI"], "AI / NLP", "🤖",
     "https://github.com/adilkhan107", 4),
]

EDUCATION = [
    ("B.Tech CSE with AI & ML", "Undergraduate", "Mind Power University",
     "2024 – 2028", "Pursuing", 1, 1),
    ("Intermediate", "Class 12", "B S M Inter College", "2023", "Passed · First Division", 0, 2),
    ("High School", "Class 10", "B S M Inter College", "2020 – 2021", "Passed · First Division", 0, 3),
]

ACHIEVEMENTS = [
    ("1st Prize — Hackathon 2026",
     "Rural Healthcare Track, Mind Power University", "🏆", 1),
    ("National Level Hackathon — Manthan'25",
     "Participated; organised by COER University", "🚀", 2),
    ("Kaggle & HackerRank",
     "Solved beginner-level problems", "📊", 3),
]

HOBBIES = [
    ("Learning new skills", "🌱", 1),
    ("Coding", "💻", 2),
    ("Online hackathons", "⚡", 3),
    ("College-level cricket", "🏏", 4),
]


def init_db() -> None:
    conn = get_conn()
    conn.executescript(SCHEMA)
    if conn.execute("SELECT COUNT(*) FROM profile").fetchone()[0] == 0:
        p = PROFILE
        conn.execute(
            "INSERT INTO profile VALUES (1,?,?,?,?,?,?,?,?,?)",
            (p["name"], p["title"], p["tagline"], p["objective"], p["email"],
             p["phone"], p["location"], p["github"], p["roles"]),
        )
        conn.executemany("INSERT INTO skills(category,name,level,position) VALUES (?,?,?,?)", SKILLS)
        conn.executemany(
            "INSERT INTO projects(title,subtitle,description,tech,badge,icon,link,position) "
            "VALUES (?,?,?,?,?,?,?,?)",
            [(t, s, d, json.dumps(te), b, i, l, pos) for t, s, d, te, b, i, l, pos in PROJECTS],
        )
        conn.executemany(
            "INSERT INTO education(degree,level,institution,period,result,current,position) "
            "VALUES (?,?,?,?,?,?,?)", EDUCATION)
        conn.executemany("INSERT INTO achievements(title,detail,icon,position) VALUES (?,?,?,?)", ACHIEVEMENTS)
        conn.executemany("INSERT INTO hobbies(name,icon,position) VALUES (?,?,?)", HOBBIES)
        conn.execute("INSERT OR IGNORE INTO stats(key,value) VALUES ('visits',0)")
    conn.execute("UPDATE profile SET github='adilkhan107' WHERE github='adilkhan1234556'")
    conn.execute("UPDATE projects SET link=REPLACE(link,'adilkhan1234556','adilkhan107')")
    conn.commit()
    conn.close()
