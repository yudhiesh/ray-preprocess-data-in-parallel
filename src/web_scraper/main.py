import typer
from src.web_scraper.web_scraping import app as sync_web_scraping_app
from src.web_scraper.web_scraping_ray import app as sync_ray_web_scraping_app
from src.web_scraper.async_web_scraping import app as async_web_scraping_app

app = typer.Typer(
    name="Web Scraper",
    add_completion=False,
    help="Web Scraper Pipeline",
)

app.add_typer(async_web_scraping_app, name="async")
app.add_typer(sync_web_scraping_app, name="sync")
app.add_typer(sync_ray_web_scraping_app, name="sync_ray")


if __name__ == "__main__":
    app()
