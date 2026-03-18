import logging
import os
import threading
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import config
import database

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Only import heavy deps when running locally (not on Vercel)
if not config.IS_SERVERLESS:
    from apscheduler.schedulers.background import BackgroundScheduler
    import notifier
    import scraper

    scheduler = BackgroundScheduler()
    scrape_lock = threading.Lock()

    def run_scrape():
        """Run a scrape cycle with notification."""
        if not scrape_lock.acquire(blocking=False):
            logger.info("Scrape already in progress, skipping.")
            return 0
        try:
            before = datetime.now().isoformat()
            new_count = scraper.fetch_jobs()
            if new_count > 0 and notifier.is_configured():
                new_jobs = database.get_new_jobs_since(before)
                notifier.send_notification(new_jobs)
            return new_count
        finally:
            scrape_lock.release()


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    logger.info("Database initialized.")

    if not config.IS_SERVERLESS:
        logger.info("Running initial job scrape...")
        threading.Thread(target=run_scrape, daemon=True).start()

        scheduler.add_job(
            run_scrape,
            "interval",
            hours=config.REFRESH_INTERVAL_HOURS,
            id="job_scrape",
        )
        scheduler.start()
        logger.info(f"Scheduler started — refreshing every {config.REFRESH_INTERVAL_HOURS} hours.")

    yield

    if not config.IS_SERVERLESS:
        scheduler.shutdown()
        logger.info("Scheduler shut down.")


app = FastAPI(title="DBA Job Hunter", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/jobs")
async def api_jobs(
    status: str = Query("all"),
    source: str = Query("all"),
    favorite: bool = Query(False),
    search: str = Query(""),
    sort_by: str = Query("date_posted"),
    sort_order: str = Query("desc"),
    limit: int = Query(200),
    offset: int = Query(0),
):
    jobs = database.get_jobs(
        status=status,
        source=source,
        favorite_only=favorite,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset,
    )
    return JSONResponse(content=jobs)


@app.patch("/api/jobs/{job_id}/status")
async def api_update_status(job_id: int, request: Request):
    body = await request.json()
    status = body.get("status", "")
    if database.update_job_status(job_id, status):
        return {"ok": True}
    return JSONResponse(content={"error": "Invalid status"}, status_code=400)


@app.patch("/api/jobs/{job_id}/favorite")
async def api_toggle_favorite(job_id: int):
    database.toggle_favorite(job_id)
    return {"ok": True}


@app.post("/api/refresh")
async def api_refresh():
    if config.IS_SERVERLESS:
        return {"ok": True, "message": "Data synced from cloud database."}

    def _bg():
        count = run_scrape()
        logger.info(f"Manual refresh complete: {count} new jobs.")

    threading.Thread(target=_bg, daemon=True).start()
    return {"ok": True, "message": "Refresh started in background."}


@app.get("/api/stats")
async def api_stats():
    return JSONResponse(content=database.get_stats())


@app.get("/api/last-refresh")
async def api_last_refresh():
    # Read from metadata table (persists across serverless invocations)
    ts = database.get_metadata("last_scrape_time")
    if not ts and not config.IS_SERVERLESS:
        import scraper
        ts = scraper.get_last_scrape_time()
    return {"last_refresh": ts}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host=config.HOST, port=config.PORT, reload=False)
