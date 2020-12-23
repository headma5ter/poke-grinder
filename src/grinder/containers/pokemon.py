from collections import OrderedDict

from grinder.helpers import html as html_
from grinder.containers import move
from grinder import GENERATION


class Pokemon:
    def __init__(self, species: str, level: int, move_names: list = None):
        self._species = species
        self._level = level
        self._move_set = self._get_move_set(move_names or self._default_move_names())
        self._roots = self._get_all_roots()

    def _get_all_roots(self) -> dict:
        hyperlinks = {
            "general": f"https://pokemondb.net/pokedex/{self._species.lower()}",
            "moves": f"https://pokemondb.net/pokedex/{self._species.lower()}/moves/{GENERATION}",
        }
        return {key: html_.parse_url(link) for key, link in hyperlinks.items()}

    def _default_move_names(self) -> list:
        # TODO: I think this is pulling in move-sets from multiple games...
        root = self._roots.get("moves")
        all_moves = dict()
        for table_elem in root.xpath(
            ".//h3[text()='Moves learnt by level up']/following-sibling::div[1]/descendant::tr"
        ):
            # TODO: make less terrible
            numbers = [lvl.text for lvl in table_elem.xpath("td[@class='cell-num']")]
            moves = [mv.text for mv in table_elem.xpath("td[@class='cell-name']/a")]
            if not numbers or not moves:
                continue

            all_moves.update({moves[0]: numbers[0]})

        return [
            mv
            for lvl, mv in OrderedDict(sorted(all_moves.items(), key=lambda x: x[1]))
            if lvl >= self._level
        ][:4]

    @staticmethod
    def _get_move_set(move_names: list) -> list:
        return [move.Move(move_name) for move_name in move_names]

    def _all_stats(self) -> dict:
        root = self._roots.get("general")
        return {
            stat_type: root.xpath(
                f".//th[text()='{stat_type}']/following::td[1][@class='cell-num']"
            )[0].text
            for stat_type in ("HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed")
        }
