import locator_lense.locators as locators
from locator_lense.locators import generate_locator
from locator_lense.parser import parse_html


def test_unique_id_is_preferred_and_scored():
    soup = parse_html('<button id="save">Save</button>')

    result = generate_locator(soup.select_one("button"), soup)

    assert result.locator == "#save"
    assert result.locator_type == "id"
    assert result.match_count == 1
    assert result.score == 100
    assert result.uniqueness == ""


def test_unique_name_beats_non_unique_id():
    soup = parse_html('<input id="field"><input id="field" name="email">')

    result = generate_locator(soup.select("input")[1], soup)

    assert result.locator_type == "name"
    assert result.match_count == 1
    assert result.score == 90


def test_unique_xpath_beats_non_unique_attributes():
    soup = parse_html('<button id="duplicate" name="action">A</button><button id="duplicate" name="action">B</button>')

    result = generate_locator(soup.select("button")[0], soup)

    assert result.locator_type == "XPath"
    assert result.match_count == 1
    assert result.score == 65
    assert result.uniqueness == ""


def test_xpath_is_unique_when_attributes_are_missing():
    soup = parse_html('<div><span>One</span><span>Two</span></div>')

    result = generate_locator(soup.select("span")[1], soup)

    assert result.locator_type == "XPath"
    assert result.match_count == 1
    assert result.score == 65


def test_xpath_is_preferred_over_css_when_both_are_unique():
    soup = parse_html('<div><span>One</span><span>Two</span></div>')

    result = generate_locator(soup.select("span")[1], soup)

    assert result.locator_type == "XPath"
    assert result.score == 65


def test_xpath_fallback_has_a_real_dom_match_count():
    soup = parse_html("<div><span>One</span><span>Two</span></div>")

    result = generate_locator(soup.select("span")[1], soup)

    assert result.match_count == 1


def test_special_character_id_keeps_id_priority():
    soup = parse_html('<button id="a:b">Save</button>')

    result = generate_locator(soup.find("button"), soup)

    assert result.locator_type == "id"
    assert result.match_count == 1
    assert result.score == 100


def test_identical_siblings_get_the_targeting_xpath_position():
    soup = parse_html("<div><span>Same</span><span>Same</span></div>")

    result = generate_locator(soup.find_all("span")[1], soup)

    assert result.locator == "/html[1]/body[1]/div[1]/span[2]"
    assert result.locator_type == "XPath"


def test_xpath_is_used_when_css_candidates_are_unavailable(monkeypatch):
    soup = parse_html('<button>Save</button>')
    monkeypatch.setattr(locators, "_css_candidates", lambda tag: [])

    result = generate_locator(soup.find("button"), soup)

    assert result.locator_type == "XPath"
    assert result.match_count == 1
    assert result.score == 65
