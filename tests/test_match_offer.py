from pathlib import Path

from match_offer import (
    compare,
    cv_language,
    find_skills,
    language_of,
    plain,
    read_skills,
)

SKILLS = {
    "Power BI": ["Power BI"],
    "Tableau": ["Tableau"],
    "Dashboards": ["Dashboards", "tableau de bord"],
    "Data Quality": ["Data Quality", "qualité des données"],
    "CI/CD": ["CI/CD"],
    "LLM": ["LLM"],
    "Git": ["Git"],
    "C": ["C"],
    "C++": ["C++"],
    "R": ["R"],
    "Go": ["Go"],
}


def found(text: str) -> set[str]:
    return set(find_skills(text, SKILLS))


def test_a_space_a_hyphen_or_nothing_between_two_words():
    assert found("PowerBI, power-bi and Power BI") == {"Power BI"}
    assert len(find_skills("CI/CD, CI CD, cicd", SKILLS)["CI/CD"]) == 3


def test_a_final_s_and_missing_accents():
    assert found("des LLMs") == {"LLM"}
    assert found("la qualite des donnees") == {"Data Quality"}


def test_a_longer_spelling_wins():
    assert found("un tableau de bord") == {"Dashboards"}
    assert found("Tableau Desktop") == {"Tableau"}


def test_a_skill_is_a_whole_word():
    assert found("GitHub, digital, Rust, Google") == set()
    assert found("git") == {"Git"}


def test_one_and_two_letter_names():
    assert found("C++, C# and R&D") == {"C++"}
    assert found("C, R, Go") == {"C", "R", "Go"}
    assert found("go to market, c'est") == set()


def test_language_of_the_offer():
    assert language_of("Vous développez les pipelines de données pour nous") == "fr"
    assert language_of("You will build the data pipelines for our team") == "en"


def test_compare_sorts_the_skills_of_the_offer(tmp_path):
    tex = tmp_path / "cv.tex"
    tex.write_text(
        "\\usepackage[english]{babel}\n"
        "\\begin{document}\n"
        "\\item \\B{DevOps:} Git, CI/CD\n"
        "%% Reserve\n"
        "% \\item Power BI\n"
        "\\end{document}\n",
        encoding="utf-8",
    )
    result = compare("Git, git, PowerBI and LLMs", tex, SKILLS)
    assert [(m.name, m.mentions, m.lines) for m in result["page"]] == [("Git", 2, [3])]
    assert [(m.name, m.lines) for m in result["reserve"]] == [("Power BI", [5])]
    assert [m.name for m in result["missing"]] == ["LLM"]
    assert cv_language(tex) == "en"


def test_the_skills_file_has_no_spelling_twice():
    skills = read_skills(Path(__file__).resolve().parents[1] / "scripts" / "skills.txt")
    owner: dict[str, str] = {}
    for name, spellings in skills.items():
        for spelling in spellings:
            key = plain(spelling).lower()
            assert owner.setdefault(key, name) == name, f"'{spelling}' is listed twice"
    assert len(skills) > 150
