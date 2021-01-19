from grinder.helpers import cacher
from grinder.helpers import scraper
from grinder import config_handler


if __name__ == "__main__":
    # Cache scraped data
    if config_handler.cache_data:
        cacher.write_cache(
            config_handler.moves_file,
            scraper.scrape_all_moves(),
            overwrite=config_handler.overwrite_data,
        )
        cacher.write_cache(
            config_handler.pokemon_file,
            scraper.scrape_all_pokemon(),
            overwrite=config_handler.overwrite_data,
        )
        cacher.write_cache(
            config_handler.routes_file,
            scraper.scrape_all_routes(),
            overwrite=config_handler.overwrite_data,
        )

    # Read cached data
    moves_data = cacher.read_cache(config_handler.moves_file)
    pokemon_data = cacher.read_cache(config_handler.pokemon_file)
    routes_data = cacher.read_cache(config_handler.routes_file)

    # Run pokemon through algorithm
