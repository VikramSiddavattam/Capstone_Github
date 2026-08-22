import locator_lense.locators as locators
from locator_lense.locators import create_locator_context, generate_locator
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


def test_identical_siblings_prefer_axis_xpath_before_position():
    soup = parse_html("<div><span>Same</span><span>Same</span></div>")

    result = generate_locator(soup.find_all("span")[1], soup)

    assert result.locator_type == "XPath"
    assert not result.locator.startswith("/")
    assert "following-sibling::span" in result.locator
    assert result.match_count == 1


def test_xpath_is_used_when_css_candidates_are_unavailable(monkeypatch):
    soup = parse_html('<button>Save</button>')
    monkeypatch.setattr(locators, "_css_candidates", lambda tag: [])

    result = generate_locator(soup.find("button"), soup)

    assert result.locator_type == "XPath"
    assert result.match_count == 1
    assert result.score == 65


def test_xpath_prefers_stable_attributes_and_never_uses_absolute_root():
    soup = parse_html('<section id="account"><button aria-label="Save">Save</button></section>')

    result = generate_locator(soup.find("button"), soup)

    assert result.locator_type == "XPath"
    assert result.locator == ".//button[@aria-label='Save']"
    assert not result.locator.startswith("/")


def test_xpath_uses_normalized_text_for_dynamic_elements():
    soup = parse_html('<div><button>  Save   changes </button></div>')

    result = generate_locator(soup.find("button"), soup)

    assert result.locator_type == "XPath"
    assert "normalize-space" in result.locator
    assert result.match_count == 1


def test_xpath_can_use_a_stable_descendant_axis():
    soup = parse_html('<section id="account"><button class="generated">Save</button></section><button>Save</button>')

    result = generate_locator(soup.find("button"), soup)

    assert result.locator_type == "XPath"
    assert "descendant::button" in result.locator
    assert result.match_count == 1


def test_xpath_generates_ancestor_axis_candidate_for_stable_context():
    candidates = locators._relative_xpath_candidates(
        parse_html('<section id="account"><button>Save</button></section>').find("button")
    )

    assert any("ancestor::section" in candidate for candidate in candidates)


def test_xpath_uses_following_sibling_axis_for_context():
    soup = parse_html('<form><label id="email-label">Email</label><input><input></form>')

    result = generate_locator(soup.find("input"), soup)

    assert result.locator_type == "XPath"
    assert "following-sibling::input" in result.locator
    assert result.match_count == 1


def test_xpath_uses_preceding_sibling_axis_for_context():
    soup = parse_html('<form><input><input><label id="email-label">Email</label></form>')

    result = generate_locator(soup.find_all("input")[1], soup)

    assert result.locator_type == "XPath"
    assert "preceding-sibling::input" in result.locator
    assert result.match_count == 1


def test_xpath_uses_positional_fallback_only_without_stable_context():
    soup = parse_html("<div><input><input></div>")

    result = generate_locator(soup.find_all("input")[1], soup)

    assert result.locator_type == "XPath"
    assert result.locator == ".//div/input[2]"
    assert result.match_count == 1


def test_shared_locator_context_parses_xpath_document_once(monkeypatch):
    calls = 0
    original_fromstring = locators.lxml_html.fromstring

    def counting_fromstring(*args, **kwargs):
        nonlocal calls
        calls += 1
        return original_fromstring(*args, **kwargs)

    monkeypatch.setattr(locators.lxml_html, "fromstring", counting_fromstring)
    soup = parse_html("<main>" + "".join(f'<button aria-label="Action {index}">Action</button>' for index in range(20)) + "</main>")
    context = create_locator_context(soup)

    for button in soup.find_all("button"):
        generate_locator(button, soup, context)

    assert calls == 1
