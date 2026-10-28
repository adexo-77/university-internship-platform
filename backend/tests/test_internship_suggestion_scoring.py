"""Pure deterministic scoring unit tests for internship suggestions."""

from app.services.internship_suggestion import (
    LOCATION_MAX_POINTS,
    LOCATION_NEUTRAL_POINTS,
    MAX_SKILL_POINTS,
    POINTS_PER_SKILL,
    WORK_MODE_MAX_POINTS,
    WORK_MODE_NEUTRAL_POINTS,
    score_posting,
)


def test_scoring_whole_word_java_not_javascript() -> None:
    """Java skill must match Java but not JavaScript."""
    score, matched, _, _ = score_posting(
        title="JavaScript Engineer",
        description="Write modern JavaScript and TypeScript",
        requirements="Expertise in JavaScript required",
        work_mode="remote",
        location="Remote",
        student_skills=["Java"],
        preferred_work_modes=[],
        preferred_location=None,
    )
    assert matched == []
    # 0 skills, 10 neutral work mode, 20 remote location = 30 total, but 0 skills
    assert score == 30

    score_java, matched_java, _, _ = score_posting(
        title="Java Backend Engineer",
        description="Spring Boot microservices",
        requirements="Strong Java skills",
        work_mode="remote",
        location="Remote",
        student_skills=["Java"],
        preferred_work_modes=[],
        preferred_location=None,
    )
    assert matched_java == ["Java"]
    assert score_java == 12 + WORK_MODE_NEUTRAL_POINTS + LOCATION_MAX_POINTS


def test_scoring_c_cpp_csharp_boundaries() -> None:
    """C must not match C++ or C#, while C++ and C# match accurately."""
    # C skill on C++ posting
    _, matched_c, _, _ = score_posting(
        title="C++ Game Developer",
        description="Unreal Engine C++ development",
        requirements="C++ proficiency",
        work_mode="onsite",
        location="Hawassa",
        student_skills=["C"],
        preferred_work_modes=["onsite"],
        preferred_location="Hawassa",
    )
    assert matched_c == []

    # C++ and C# skills on mixed posting
    _, matched_both, _, _ = score_posting(
        title="Systems Developer",
        description="Experience in C++ and C# desired",
        requirements="C++ or C#",
        work_mode="onsite",
        location="Hawassa",
        student_skills=["C++", "C#", "C"],
        preferred_work_modes=[],
        preferred_location=None,
    )
    assert sorted(matched_both) == ["C#", "C++"]


def test_scoring_dotnet_and_nodejs_with_punctuation() -> None:
    """.NET and Node.js skills work with punctuation and case."""
    score, matched, wm_match, loc_match = score_posting(
        title="Full Stack Developer (Node.js / .NET)",
        description="Building APIs with Node.js, and .NET Core backend services.",
        requirements="Node.js and .NET.",
        work_mode="hybrid",
        location="Addis Ababa",
        student_skills=["node.js", ".NET"],
        preferred_work_modes=["hybrid"],
        preferred_location="Addis Ababa",
    )
    assert sorted(matched) == [".NET", "node.js"]
    assert wm_match is True
    assert loc_match is True
    assert score == (2 * POINTS_PER_SKILL) + WORK_MODE_MAX_POINTS + LOCATION_MAX_POINTS


def test_scoring_skills_cap_at_five_matches() -> None:
    """Skill matches cap at 5 (60 points) even if student has 6 matching skills."""
    student_skills = ["Python", "FastAPI", "SQL", "Docker", "PostgreSQL", "Redis"]
    score, matched, _, _ = score_posting(
        title="Python Backend Architect",
        description="Python, FastAPI, SQL, Docker, PostgreSQL, and Redis stack.",
        requirements="Must know Python, FastAPI, SQL, Docker, PostgreSQL, and Redis.",
        work_mode="onsite",
        location="Hawassa",
        student_skills=student_skills,
        preferred_work_modes=[],
        preferred_location=None,
    )
    assert len(matched) == 6
    expected_skill_points = MAX_SKILL_POINTS
    assert score == (expected_skill_points + WORK_MODE_NEUTRAL_POINTS + LOCATION_NEUTRAL_POINTS)


def test_scoring_neutral_work_mode_and_location_points() -> None:
    """Empty preferences yield 10 neutral points each and None match flags."""
    score, matched, wm_match, loc_match = score_posting(
        title="Python Developer",
        description="Python tasks",
        requirements="Python required",
        work_mode="onsite",
        location="Dire Dawa",
        student_skills=["Python"],
        preferred_work_modes=[],
        preferred_location=None,
    )
    assert matched == ["Python"]
    assert wm_match is None
    assert loc_match is None
    assert score == 12 + 10 + 10


def test_scoring_work_mode_and_location_mismatch() -> None:
    """Non-matching work mode and location yield 0 points each and False flags."""
    score, matched, wm_match, loc_match = score_posting(
        title="Python Developer",
        description="Python tasks",
        requirements="Python required",
        work_mode="onsite",
        location="Dire Dawa",
        student_skills=["Python"],
        preferred_work_modes=["remote"],
        preferred_location="Addis Ababa",
    )
    assert matched == ["Python"]
    assert wm_match is False
    assert loc_match is False
    assert score == 12 + 0 + 0
