import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "jobs.db"

# Turso / libsql settings (set env vars for cloud deployment)
TURSO_DATABASE_URL = os.environ.get("TURSO_DATABASE_URL", "")
TURSO_AUTH_TOKEN = os.environ.get("TURSO_AUTH_TOKEN", "")

# Detect serverless environment (Vercel sets VERCEL=1)
IS_SERVERLESS = bool(TURSO_DATABASE_URL) or bool(os.environ.get("VERCEL", ""))

# Job search settings
SEARCH_TERMS = [
    "DBA",
    "Database Administrator",
    "Database Engineer",
    "Data Engineer",
    "Support Engineer",
    "SRE",
    "Site Reliability Engineer",
]
SITES = ["indeed", "linkedin", "glassdoor", "google", "zip_recruiter"]
IS_REMOTE = True
HOURS_OLD = 336  # 14 days
RESULTS_WANTED = 50  # per search term per site
COUNTRY_INDEED = "USA"
LOCATION = "USA"

# Title filtering — reject jobs that are clearly irrelevant
TITLE_EXCLUDE_PATTERNS = [
    r"frontend",
    r"react",
    r"angular",
    r"vue\.?js",
    r"full[\s\-]?stack",
    r"ios\s+developer",
    r"android\s+developer",
    r"ui/?ux",
    r"mobile\s+dev",
    r"web\s+developer",
    r"java\s+developer",
    r"ruby",
    r"php\s+developer",
    r"\.net\s+developer",
    r"scrum\s+master",
    r"product\s+manager",
    r"project\s+manager",
    r"sales\s+engineer",
    r"marketing",
    r"recruiter",
    r"graphic\s+design",
    r"machine\s+learning",
    r"ml\s+engineer",
    r"ai\s+engineer",
    r"security\s+analyst",
    r"penetration\s+test",
    r"network\s+engineer",
    r"help\s+desk",
]

# Title keywords that always indicate a relevant job
TITLE_INCLUDE_KEYWORDS = [
    "database", "data", "dba", "support engineer", "sre",
    "reliability", "infrastructure", "devops", "platform",
    "sql", "postgres", "oracle", "mysql", "mongo", "redis",
    "snowflake", "admin", "etl", "warehouse", "pipeline",
    "airflow", "spark", "hadoop", "bigquery", "redshift",
    "databricks", "terraform", "kubernetes", "k8s", "docker",
    "linux", "systems engineer", "cloud engineer",
]

# Scheduler settings
REFRESH_INTERVAL_HOURS = 4

# Email notification settings (optional — set env vars to enable)
GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", "")

# Dashboard URL (for email notifications)
DASHBOARD_URL = os.environ.get("DASHBOARD_URL", "")

# Server settings
HOST = "0.0.0.0"
PORT = 8888
