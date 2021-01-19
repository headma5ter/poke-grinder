import re

from grinder.helpers import html as html_

GENERATION_CONVERTER = {
    1: "rby",
    2: "gs",
    3: "rs",
    4: "dp",
    5: "bw",
    6: "xy",
    7: "sm",
    8: "swsh",
}
GENERATION_URL_BLANKS = {
    "moves": 3,
    "pokes": 1,
    "routes": None,
}

DEFAULT_XPATHS = {
    "types": [
        ".//tr/td[contains(text(),'Damage Taken')]/following::tr[1]/td/a[contains(@href,'attackdex')]",
        ".//tr/td[contains(text(),'Damage Taken')]/following::tr[2]/td",
    ],
    "stats": [
        ".//td/b[contains(text(),'Stats')]/following::tr[1]/td/text()",
        ".//td/b[contains(text(),'Stats')]/following::tr[2]/td/text()",
    ],
    "levelup_moves": ".//table/descendant::tr/td[contains(text(),'Level')]/parent::tr/following-sibling::tr",
    "all_moves": ".//option[contains(@value,'attack')]/text()",
    "all_routes": "",
}

XPATHS = {
    1: {
        "types": DEFAULT_XPATHS["types"],
        "stats": DEFAULT_XPATHS["stats"],
        "levelup_moves": DEFAULT_XPATHS["levelup_moves"],
        "all_moves": DEFAULT_XPATHS["all_moves"],
    },
    2: {
        "types": DEFAULT_XPATHS["types"],
        "stats": DEFAULT_XPATHS["stats"],
        "levelup_moves": DEFAULT_XPATHS["levelup_moves"],
        "all_moves": DEFAULT_XPATHS["all_moves"],
    },
    3: {
        "types": "",  # not included in page
        "stats": [
            ".//td/b[contains(text(),'Stats')]/following::tr[1]/td/b/text()",
            ".//td/b[contains(text(),'Stats')]/following::tr[2]/td[@align='center']/text()",
        ],
        "levelup_moves": ".//table/descendant::th/font[contains(text(),'Level')]/ancestor::thead/following-sibling::tbody/tr",
        "all_moves": DEFAULT_XPATHS["all_moves"],
    },
    4: {
        "types": DEFAULT_XPATHS["types"],
        "stats": DEFAULT_XPATHS["stats"],
        "levelup_moves": DEFAULT_XPATHS["levelup_moves"],
        "all_moves": DEFAULT_XPATHS["all_moves"],
    },
    5: {
        "types": DEFAULT_XPATHS["types"],
        "stats": DEFAULT_XPATHS["stats"],
        "levelup_moves": DEFAULT_XPATHS["levelup_moves"],
        "all_moves": DEFAULT_XPATHS["all_moves"],
    },  # Levelup moves gets an extra item (edit?)
    6: {
        "types": DEFAULT_XPATHS["types"],
        "stats": DEFAULT_XPATHS["stats"],
        "levelup_moves": DEFAULT_XPATHS["levelup_moves"],
        "all_moves": DEFAULT_XPATHS["all_moves"],
    },
    7: {
        "types": [
            ".//tr/td/h2[contains(text(),'Weakness')]/following::tr[1]/td/a[contains(@href,'attackdex')]",
            ".//tr/td/h2[contains(text(),'Weakness')]/following::tr[2]/td",
        ],
        "stats": [
            ".//td/h2[contains(text(),'Stats')]/following::tr[1]/td/text()",
            ".//td/h2[contains(text(),'Stats')]/following::tr[2]/td/text()",
        ],
        "levelup_moves": ".//table/descendant::tr/td/h3[contains(text(),'Level')]/ancestor::tr/following-sibling::tr",
        "all_moves": DEFAULT_XPATHS["all_moves"],
    },
    8: {
        "types": [
            ".//tr/td/h2[contains(text(),'Weakness')]/following::tr[1]/td/a[contains(@href,'attackdex')]",
            ".//tr/td/h2[contains(text(),'Weakness')]/following::tr[2]/td",
        ],
        "stats": [
            ".//td/h2[contains(text(),'Stats')]/following::tr[1]/td/text()",
            ".//td/h2[contains(text(),'Stats')]/following::tr[2]/td/text()",
        ],
        "levelup_moves": ".//table/descendant::tr/td/h3[contains(text(),'Level')]/ancestor::tr/following-sibling::tr",
        "all_moves": DEFAULT_XPATHS["all_moves"],
    },
}

MOVES_COLUMNS = {
    "pre-split": {"level": 1, "type": 3, "power": 4, "accuracy": 5},
    "post-split": {"level": 1, "type": 3, "power": 5, "accuracy": 6},
}


def scrape_all_moves() -> dict:
    moves_dict = dict()
    for gen_number, gen_str in GENERATION_CONVERTER.items():
        url_end = ("-" + GENERATION_CONVERTER.get(gen_number)) * (
            gen_number != GENERATION_URL_BLANKS.get("moves")
        )
        url = f"https://www.serebii.net/attackdex{url_end}"
        root = html_.parse_url(url=url)

        moves_dict[gen_number] = [
            move.strip()
            for move in html_.get_markup_elements(
                root=root, xpath=XPATHS[gen_number]["all_moves"]
            )
        ]

    return moves_dict


def _scrape_individual_pokemon_data(url: str, gen: int) -> dict:
    root = html_.parse_url(url=url)

    # Grab all the type effective multipliers
    if gen != 3:
        type_effectiveness = {
            type_elem.get("href")
            .split("/")[-1]
            .replace(".shtml", "")
            .title(): multiplier_elem.text.replace("*", "")
            for type_elem, multiplier_elem in zip(
                html_.get_markup_elements(root=root, xpath=XPATHS[gen]["types"][0],),
                html_.get_markup_elements(root=root, xpath=XPATHS[gen]["types"][1],),
            )
        }
    else:
        # TODO: figure out solution for gen 3 type effectiveness (not given on page)
        type_effectiveness = dict()

    # Grab all base stats
    base_stats = {
        stat_name: stat_value
        for stat_name, stat_value in zip(
            html_.get_markup_elements(root=root, xpath=XPATHS[gen]["stats"][0],),
            html_.get_markup_elements(root=root, xpath=XPATHS[gen]["stats"][1],),
        )
        if stat_name.strip()
    }

    # Grab all moves learned upon leveling up
    levelup_moves = dict()
    split_type = "pre-split" if gen in (1, 2) else "post-split"
    for table_elem in html_.get_markup_elements(
        root=root, xpath=XPATHS[gen]["levelup_moves"],
    ):
        try:
            move_name = table_elem.xpath("td[2]/a/text()")[0]
        except IndexError:
            continue

        levelup_moves.update(
            {
                move_name: {
                    "level": table_elem.xpath(
                        f"td[{MOVES_COLUMNS[split_type]['level']}]/text()"
                    )[0].replace("-", "1"),
                    "type": table_elem.xpath(
                        f"td[{MOVES_COLUMNS[split_type]['type']}]/descendant::img"
                    )[0]
                    .get("src")
                    .split("/")[-1]
                    .replace(".gif", "")
                    .title(),
                    "power": table_elem.xpath(
                        f"td[{MOVES_COLUMNS[split_type]['power']}]/text()"
                    )[0],
                    "accuracy": table_elem.xpath(
                        f"td[{MOVES_COLUMNS[split_type]['accuracy']}]/text()"
                    )[0],
                }
            }
        )

    return {
        "type_effectiveness": type_effectiveness,
        "base_stats": base_stats,
        "levelup_moves": levelup_moves,
    }


def scrape_all_pokemon() -> dict:
    poke_dict = dict()
    for gen_number, gen_str in GENERATION_CONVERTER.items():
        url_end = ("-" + GENERATION_CONVERTER.get(gen_number)) * (
            gen_number != GENERATION_URL_BLANKS.get("pokes")
        )
        base_url = f"https://www.serebii.net"
        root = html_.parse_url(url=f"{base_url}/pokedex{url_end}")

        poke_dict.update(
            {
                gen_number: {
                    pokemon_elem.text.split(" ", 1)[
                        -1
                    ].strip(): _scrape_individual_pokemon_data(
                        url=f"{base_url}{pokemon_elem.get('value').strip()}",
                        gen=gen_number,
                    )
                    for pokemon_elem in html_.get_markup_elements(
                        root=root, xpath=".//option[contains(@value,'pokedex')]"
                    )
                    if pokemon_elem.text
                    and len(pokemon_elem.text.split(" ", 1)) == 2
                    and re.match(r"^\d{3}$", pokemon_elem.text.split(" ", 1)[0])
                }
            }
        )

    return poke_dict


def scrape_all_routes() -> dict:
    base_url = "https://www.serebii.net"
    root = html_.parse_url(url=f"{base_url}/pokearth/index.shtml")

    regions_dict = dict()
    for dropdown_elem in root.xpath(
        ".//select/descendant::option[not(contains(text(),'Pokéarth')) and not(contains(text(),'Pokearth'))]"
    ):
        url_end = dropdown_elem.get("value")
        url = f"{base_url}{url_end}"
        route = dropdown_elem.text
        *_, region, _ = url_end.split("/")

        if region not in regions_dict:
            regions_dict[region] = dict()

        if "rand'shouse" in url:
            # TODO: figure out better way to fix this...
            url = url.replace("'", "")
        elif "noiaforest" in url:
            url = url.replace("noiaforest", "noirforest")

        route_root = html_.parse_url(url=url)
        route_data = dict()

        for generation_anchor in route_root.xpath(
            ".//td[contains(text(),'Anchor')]/parent::tr/following-sibling::tr/td/a"
        ):
            sub_url = f"{base_url}{generation_anchor.get('href')}"
            root_per_gen = html_.parse_url(url=sub_url)

            for route_elem in root_per_gen.xpath(
                ".//p/descendant::u[contains(text(),'Wild')]/following::tr/td[contains(text(),'Pokémon')]"
            ):
                game_name = route_elem.text
                data_by_game = list()
                for pokemon, rate, levels in zip(
                    route_elem.xpath(
                        "parent::tr/following-sibling::tr/td[@class='name']/text()"
                    ),
                    route_elem.xpath(
                        "parent::tr/following-sibling::tr/td[@class='rate']/text()"
                    ),
                    route_elem.xpath(
                        "parent::tr/following-sibling::tr/td[@class='level']/text()"
                    ),
                ):
                    low_level, high_level = (
                        (lvl.strip() for lvl in levels.split("-", 1))
                        if "-" in levels
                        else (levels, levels)
                    )

                    if "%" not in rate:
                        continue

                    try:
                        data_by_game.append(
                            {
                                "pokemon": pokemon,
                                "rate": int(
                                    rate.replace("%", "")
                                    .replace("--", "100")
                                    .replace("-", "100")
                                )
                                / 100,
                                "lowest_level": low_level,
                                "highest_level": high_level,
                            }
                        )
                    except ValueError:
                        print(f"WARNING: Skipping due to bad rate ({rate})")
                        continue

                route_data.update({game_name: data_by_game})

        regions_dict[region].update({route: route_data})

    return regions_dict
