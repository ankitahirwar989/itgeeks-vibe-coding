from app.citations.verifier import verify_citation

KNOWN = {
    "attendance_policy.md#3.1": (
        "3.1 Minimum Attendance\nStudents must maintain at least 75% attendance in each "
        "registered course to be eligible to appear for the semester examination."
    )
}


def test_unknown_citation_is_rejected():
    result = verify_citation("made_up.md#9.9", "anything", KNOWN)
    assert result.citation_exists is False
    assert result.quote_supported is False


def test_exact_substring_quote_is_supported():
    result = verify_citation(
        "attendance_policy.md#3.1",
        "Students must maintain at least 75% attendance",
        KNOWN,
    )
    assert result.citation_exists is True
    assert result.quote_supported is True


def test_fabricated_quote_not_present_in_source_is_rejected():
    result = verify_citation(
        "attendance_policy.md#3.1",
        "Students must maintain at least 40% attendance and pay a fine of one thousand rupees",
        KNOWN,
    )
    assert result.citation_exists is True
    assert result.quote_supported is False


def test_whitespace_and_case_differences_are_tolerated():
    result = verify_citation(
        "attendance_policy.md#3.1",
        "STUDENTS   must maintain\nat least 75% attendance",
        KNOWN,
    )
    assert result.quote_supported is True
