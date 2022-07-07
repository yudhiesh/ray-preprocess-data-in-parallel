import json
import logging
from typing import Dict, List

import psutil
import ray
import typer

from src.constants import ROOT_DIR, REAL_LIST
from src.utils import timer
from src.web_scraper.web_scraping import process_url
from src.constants import (
    NAME_WEB_SCRAPING_RAY,
    DESCRIPTION_WEB_SCRAPING_RAY,
    FILENAME_TIME_RESULTS,
)

logging.basicConfig(
    format="%(process)d-%(levelname)s-%(message)s",
    level=logging.INFO,
)


app = typer.Typer(
    name=NAME_WEB_SCRAPING_RAY,
    help=DESCRIPTION_WEB_SCRAPING_RAY,
    add_completion=False,
)

process_url_ = ray.remote(process_url)


def process_urls_ray(urls: List[Dict[str, str]]) -> None:
    result_refs = []
    for url in urls:
        ref = process_url_.remote(url)
        result_refs.append(ref)
    ray.get(result_refs)


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
    ray.init(num_cpus=psutil.cpu_count())

    @timer(
        file_path=FILENAME_TIME_RESULTS,
        to_save=to_save,
    )
    def run_ray_program():

        URL_PATH = ROOT_DIR / REAL_LIST
        with open(URL_PATH) as file:
            html_files = json.load(file)

        try:
            html_files[num_files]
            html_files = html_files[:num_files]
        except IndexError:
            logging.error(
                "num_files(%d) is > the actual number of files(%d) that exist. Pass in a smaller value",
                num_files,
                len(html_files),
            )
        except TypeError:
            process_urls_ray(urls=html_files)
        else:
            process_urls_ray(urls=html_files)

    run_ray_program()
