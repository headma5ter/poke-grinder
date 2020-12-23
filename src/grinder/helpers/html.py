from lxml import html
import requests


def parse_url(url: str) -> html.parse:
    try:
        response = requests.get(url, stream=True)
    except:
        # TODO: narrow down catch
        raise ValueError("Something's wrong with the URL")
    response.raw.decode_content = True

    try:
        return html.parse(response.raw).getroot()
    except:
        # TODO: narrow down catch
        raise ValueError("Something's wrong wih the parser?")
