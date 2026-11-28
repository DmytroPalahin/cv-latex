from cvtext import detex, source_lines, squeeze, words_of


def test_detex_joins_what_an_empty_group_splits():
    assert (
        detex(r"A{}WS S3, T{}ensorFlow/Keras, ETL/EL{}T")
        == "AWS S3, TensorFlow/Keras, ETL/ELT"
    )


def test_detex_keeps_the_text_of_a_command():
    assert (
        squeeze(detex(r"\B{Data Engineering:} Python, SQL"))
        == "Data Engineering: Python, SQL"
    )


def test_detex_drops_the_address_of_a_link():
    assert squeeze(detex(r"\href{https://example.com/page}{Example}")) == "Example"
    assert (
        squeeze(detex(r"\project{Title}{https://example.com/repo}{Python}"))
        == "Title Python"
    )


def test_detex_separates_two_arguments():
    assert (
        squeeze(detex(r"\cvevent{Data Engineer}{2023 - 2026}"))
        == "Data Engineer 2023 - 2026"
    )


def test_detex_replaces_the_symbols_of_the_template():
    line = r"Python \textperiodcentered{} SQL\sep 80\% \& A{}WS\nbrealspace S3"
    assert squeeze(detex(line)) == "Python · SQL | 80% & AWS S3"


def test_words_keep_the_signs_of_technical_terms():
    words = words_of("C/C++, CI/CD: 99.1% of TF-IDF (github.com/name), l'IA; 500+ GB")
    expected = [
        "C/C++",
        "CI/CD",
        "99.1%",
        "of",
        "TF-IDF",
        "github.com/name",
        "l'IA",
        "500+",
        "GB",
    ]
    assert list(words) == expected


def test_source_lines_tell_the_page_from_the_comments(tmp_path):
    tex = tmp_path / "cv.tex"
    tex.write_text(
        "\\documentclass{article}\n"
        "% preamble note\n"
        "\\begin{document}\n"
        "\\item Python, SQL % on the page\n"
        "\n"
        "    %% Reserve\n"
        "    % \\item \\B{Selenium}\n"
        "\\end{document}\n"
        "after the end\n",
        encoding="utf-8",
    )
    body = source_lines(tex, body_only=True)
    assert [(line.number, line.comment, squeeze(line.text)) for line in body] == [
        (4, False, "Python, SQL"),
        (6, True, "Reserve"),
        (7, True, "Selenium"),
    ]
    assert [line.number for line in source_lines(tex)] == [1, 2, 4, 6, 7]
