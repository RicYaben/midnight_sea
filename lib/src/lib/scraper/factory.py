from lib.scraper.scraper import Scraper


class ScraperFactory:
    scrapers = {}

    @classmethod
    def get_scraper(cls, scraper: str) -> Scraper:
        try:
            retval = cls.scrapers[scraper]
        except KeyError as err:
            raise NotImplementedError(f"{scraper=} doesn't exist") from err
        return retval

    @classmethod
    def register(cls, name):
        def decorator(decorator_cls: Scraper):
            cls.scrapers[name] = decorator_cls
            return decorator_cls

        return decorator
