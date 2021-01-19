from lxml import html
import requests


def parse_url(url: str) -> html.parse:
    """
    Parse any given webpage.
    :param url: path to webpage
    :return: html.parse
    """

    print(f"Parsing {url}")
    response = requests.get(url, stream=True)
    response.raw.decode_content = True

    if response.status_code != 200:
        raise ValueError(
            f"Something went wrong ({response.status_code}) with parsing the URL ({url})"
        )

    root = html.parse(response.raw).getroot()
    if root is None:
        raise ValueError(f"Something went wrong! Check the URL and try again.")

    return root


def get_markup_elements(root: html.Element, xpath: str = "", attribute: str = "", **kwargs) -> list:
    """
    Grabs either text or attributes from all HTML elements
    using a xpath as defined below:

        [INSERT XPATH HERE]  # TODO: insert xpath

    :param root: the HTML root (from the parser).
    :param xpath: the xpath to search if the user has already
        created it (the rest of the input vars are ignored).
    :param attribute: the attribute key for which the value
        is returned; if left empty, the text is returned.
    :param kwargs: xpath nodes and filters.
    :return: list of data taken from the element(s).
    """

    if not xpath:
        xpath = "//"
        for node, filter_ in kwargs.items():
            if not isinstance(filter_, dict):
                raise ValueError("Keyword arguments must be dictionaries")

            xpath = f"{xpath}*[local-name()='{node}'"
            for name, value in filter_.items():
                xpath = f"{xpath}[@{name}='{value}']"

            xpath += "/"

        xpath = f"{xpath}@{attribute}" if attribute else f"{xpath}text()"

    return root.xpath(xpath)
