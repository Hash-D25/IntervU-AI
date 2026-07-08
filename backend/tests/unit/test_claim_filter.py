"""Claim grounding filter tests."""

from app.features.interview.follow_up.claim_filter import claim_grounded_in_answer
from app.features.interview.follow_up.schemas import ExtractedClaim
from app.features.interview.follow_up.validator import FollowUpValidator


def test_rejects_question_premise_as_claim() -> None:
    question = (
        "Write a simple SQL query to retrieve the last 5 records inserted into a "
        "PostgreSQL table, assuming no deletes have occurred."
    )
    answer = (
        "Use ORDER BY id DESC LIMIT 5 when the table has an auto-incrementing id."
    )
    assert (
        claim_grounded_in_answer("no deletes have occurred", answer, question) is False
    )


def test_accepts_answer_claim() -> None:
    question = "How do you load a private GitHub repository?"
    answer = (
        "I used authenticated requests with a Personal Access Token and cached "
        "previously opened folders to stay under GitHub API rate limits."
    )
    assert claim_grounded_in_answer("Personal Access Token", answer, question) is True


def test_validate_claims_drops_premise_leak() -> None:
    claims = FollowUpValidator.validate_claims(
        [
            ExtractedClaim(
                text="no deletes have occurred",
                claim_type="process",
                probe_angle="What if deletes happen?",
            ),
            ExtractedClaim(
                text="ORDER BY id DESC LIMIT 5",
                claim_type="technical",
                probe_angle="What if there is no id column?",
            ),
        ],
        answer_transcript=(
            "I would sort by id descending and limit to five with ORDER BY id DESC LIMIT 5."
        ),
        question_text=(
            "Retrieve the last 5 records inserted into a PostgreSQL table, "
            "assuming no deletes have occurred."
        ),
    )
    assert len(claims) == 1
    assert "ORDER BY" in claims[0].text
