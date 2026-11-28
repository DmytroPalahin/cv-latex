from check_links import classify, hint, parse_pdfinfo_urls

PDFINFO = """Page  Type          URL
   1  Annotation    tel:+33123456789
   1  Annotation    mailto:name@example.com
   1  Annotation    https://example.com/a page
   2  Annotation    https://github.com/name/repo
"""


def test_links_listed_by_pdfinfo():
    assert parse_pdfinfo_urls(PDFINFO) == [
        "tel:+33123456789",
        "mailto:name@example.com",
        "https://example.com/a page",
        "https://github.com/name/repo",
    ]
    assert parse_pdfinfo_urls("Page  Type          URL\n") == []


def test_only_a_missing_page_fails():
    assert classify(200)[0] == "ok"
    assert classify(404)[0] == "fail"
    assert classify(410)[0] == "fail"
    for code in (401, 403, 429, 500, 503, 999):
        assert classify(code)[0] == "warning"


def test_hint_for_github():
    assert "private" in hint("https://github.com/name/repo")
    assert hint("https://example.com") == ""
