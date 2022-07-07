import concurrent
import functools
import asyncio
from asyncio import Semaphore
import json
import logging
from pathlib import Path
from typing import List, Optional

import aiofiles
from aiohttp import ClientSession
import aiohttp
from bs4 import BeautifulSoup
import typer

from src.constants import (
    DATA_DIR,
    ROOT_DIR,
    URL,
    REAL_LIST,
    NAME_ASYNC_WEB_SCRAPING,
    DESCRIPTION_ASYNC_WEB_SCRAPING,
    FILENAME_ASYNC_WEB_SCRAPING,
)
from src.utils import async_timer

app = typer.Typer(
    name=NAME_ASYNC_WEB_SCRAPING,
    help=DESCRIPTION_ASYNC_WEB_SCRAPING,
    add_completion=False,
)

logging.basicConfig(
    format="%(process)d-%(levelname)s-%(message)s",
    level=logging.DEBUG,
)


def extract_text(raw_text: str) -> str:
    return " ".join(BeautifulSoup(raw_text, "html.parser").stripped_strings)


async def fetch_url(
    url: str,
    session: ClientSession,
    semaphore: Semaphore,
) -> str:
    async with semaphore:
        response = await session.request(method="GET", url=url)
        response.raise_for_status()
        logging.info("Got response [%s] for URL: %s", response.status, url)
        text = await response.text(encoding="utf-8")
        return text


async def parse(
    url: str,
    session: ClientSession,
    semaphore: Semaphore,
    executor: concurrent.futures.Executor,
) -> Optional[str]:
    try:
        text = await fetch_url(
            url=url,
            session=session,
            semaphore=semaphore,
        )
    except (
        aiohttp.ClientError,
        aiohttp.http_exceptions.HttpProcessingError,
    ) as e:
        logging.error(
            "aiohttp exception for %s [%s]: %s",
            url,
            getattr(e, "status", None),
            getattr(e, "message", None),
        )
    except Exception as e:
        logging.exception(
            "Non-aiohttp exception occured:  %s",
            getattr(e, "__dict__", None),
        )
    else:
        loop = asyncio.get_running_loop()
        extract_text_ = functools.partial(extract_text, text)
        text = await loop.run_in_executor(executor, extract_text_)
        logging.info("Found text for %s", url)
        return text


async def process_file(
    url: dict,
    session: ClientSession,
    semaphore: Semaphore,
    executor: concurrent.futures.Executor,
) -> None:
    category = url.get("category")
    link = url.get("link")
    if category and link:
        text = await parse(
            url=f"{URL}/{link}",
            session=session,
            semaphore=semaphore,
            executor=executor,
        )
        if text:
            save_path = await get_save_path(
                link=link,
                category=category,
            )
            await write_file(html_text=text, path=save_path)
        else:
            logging.warning("Text for %s not found, skipping it...", link)


async def get_save_path(link: str, category: str) -> Path:
    CATEGORY_DIR = DATA_DIR / category
    CATEGORY_DIR.mkdir(parents=True, exist_ok=True)
    save_path = CATEGORY_DIR / link
    return save_path


async def process_files(
    html_files: List[dict],
    semaphore: Semaphore,
):
    async with ClientSession() as session:
        with concurrent.futures.ProcessPoolExecutor() as executor:

            tasks = [
                process_file(
                    url=file,
                    session=session,
                    semaphore=semaphore,
                    executor=executor,
                )
                for file in html_files
            ]
            await asyncio.gather(*tasks)


async def write_file(
    html_text: str,
    path: Path,
) -> None:
    async with aiofiles.open(
        path,
        "w+",
        encoding="utf-8",
    ) as file:
        await file.write(html_text)
        logging.info("Saved %s", path.as_posix())


@app.command()
def run(
    num_files: int = typer.Option(
        None,
        help="Number of files to process. If no value is passed then all the files are processed.",
    ),
    to_save: bool = typer.Option(
        True,
        help=f"Whether to time the run or not. If the run is timed then it will overried the {FILENAME_ASYNC_WEB_SCRAPING}",
    ),
    semaphore_count: int = typer.Option(
        10,
        help="The number of counts to use within the Semaphore to limit the number of concurrent request to make.",
    ),
):
    @async_timer(file_path=FILENAME_ASYNC_WEB_SCRAPING, to_save=to_save)
    async def main_async(
        num_files: Optional[int],
        semaphore_count: int,
    ) -> None:
        URL_PATH = ROOT_DIR / REAL_LIST
        async with aiofiles.open(URL_PATH, "r") as file:
            html_files = json.loads(await file.read())
        semaphore = Semaphore(semaphore_count)
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
            await process_files(
                html_files=html_files,
                semaphore=semaphore,
            )
        else:
            await process_files(
                html_files=html_files,
                semaphore=semaphore,
            )

    asyncio.run(
        main_async(
            num_files=num_files,
            semaphore_count=semaphore_count,
        )
    )
