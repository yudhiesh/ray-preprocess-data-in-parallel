import json
import logging
from pathlib import Path
from typing import Dict, List
from urllib.error import HTTPError
import urllib.request

from src.web_scraper.async_web_scraping import extract_text
import typer

from src.constants import (
    DATA_DIR,
    ROOT_DIR,
    URL,
    REAL_LIST,
    NAME_SYNC_WEB_SCRAPING,
    DESCRIPTION_SYNC_WEB_SCRAPING,
    FILENAME_TIME_RESULTS,
)
from src.utils import timer


logging.basicConfig(
    format="%(process)d-%(levelname)s-%(message)s",
    level=logging.INFO,
)

app = typer.Typer(
    name=NAME_SYNC_WEB_SCRAPING,
    help=DESCRIPTION_SYNC_WEB_SCRAPING,
    add_completion=False,
)


def save_html(soup: str, path: Path) -> None:
    try:
        logging.info("Saving %s", path)
        with open(path, "w+", encoding="utf-8") as file:
            file.write(soup)
    except Exception as e:
        logging.warning("Unable to save to %s due to %s", path.as_posix(), e)


def get_save_path(link: str, category: str) -> Path:
    CATEGORY_DIR = DATA_DIR / category
    CATEGORY_DIR.mkdir(parents=True, exist_ok=True)
    save_path = CATEGORY_DIR / link
    return save_path


def get_html_page(link: str) -> str:
    full_url = f"{URL}/{link}"
    logging.info("Processing %s", full_url)
    try:
        response = urllib.request.urlopen(full_url)
        text = response.read().decode("utf-8")
    except HTTPError:
        logging.warning("%s not found, skipping it.", link)
    else:
        return text
        # return extract_text(text)


def process_url(url: Dict[str, str]) -> None:
    category = url.get("category")
    link = url.get("link")
    if category and link:
        page = get_html_page(
            link=link,
        )
        save_path = get_save_path(link, category)
        save_html(soup=page, path=save_path)


def process_urls(urls: List[Dict[str, str]]) -> None:
    for url in urls:
        process_url(url)


@app.command()
def run(
    num_files: int = typer.Option(
        None,
        help="Number of files to process. If no value is passed then all the files are processed.",
    ),
    to_save: bool = typer.Option(
        True,
        help=f"Whether to time the run or not. If the run is timed then it will overried the {FILENAME_TIME_RESULTS}",
    ),
) -> None:
    @timer(
        file_path=FILENAME_TIME_RESULTS,
        to_save=to_save,
    )
    def run_basic_program():
        URL_PATH = ROOT_DIR / REAL_LIST
        with open(URL_PATH) as file:
            html_files = json.load(file)

        try:
            html_files[num_files]
            html_files = html_files[:num_files]
        except IndexError:
            logging.error(
                "num_files(%d) is > the actual number of files(%d) that exist, pass in a smaller value.",
                num_files,
                len(html_files),
            )
        except TypeError:
            process_urls(urls=html_files)
        else:
            process_urls(urls=html_files)

    run_basic_program()
