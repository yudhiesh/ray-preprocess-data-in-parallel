from pathlib import Path

REAL_LIST = "real_list.json"
URL = "http://localhost:8000"
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
ENCODED_DIR = ROOT_DIR / "encoded"
ENCODED_DIR.mkdir(parents=True, exist_ok=True)

NAME_WEB_SCRAPING_RAY = "sync_ray_web_scraping"
DESCRIPTION_WEB_SCRAPING_RAY = "Run sync ray web scraping pipeline"

NAME_ASYNC_WEB_SCRAPING = "async_web_scraping"
DESCRIPTION_ASYNC_WEB_SCRAPING = "Run async web scraping pipeline"
FILENAME_ASYNC_WEB_SCRAPING = "time_results_async.json"

NAME_SYNC_WEB_SCRAPING = "sync_web_scraping"
DESCRIPTION_SYNC_WEB_SCRAPING = "Run sync web scraping pipeline"
FILENAME_TIME_RESULTS = "time_results.json"
