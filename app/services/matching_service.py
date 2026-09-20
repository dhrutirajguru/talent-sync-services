"""
Core matching engine (Section 6.3 of the design doc).

One function, used in both directions:
- Flow A (Student): score each opportunity against the student's skills.
- Flow B (Industry): score each candidate student against one opportunity's
  required skills.

score = |required skills the person has| / |required skills total|

Deliberately simple and explainable on stage — this is the first real slice
of the Phase 3 recommendation engine (rule-based matching), not a mock.
"""

import uuid


def compute_match(
    required_skill_ids: set[uuid.UUID],
    possessed_skill_ids: set[uuid.UUID],
) -> float:
    """Returns a score in [0.0, 1.0]. An opportunity/candidate with no
    required skills listed is treated as a full match (nothing to fail)."""
    if not required_skill_ids:
        return 1.0
    matched = required_skill_ids & possessed_skill_ids
    return round(len(matched) / len(required_skill_ids), 4)


def matched_and_missing(
    required_skill_ids: set[uuid.UUID],
    possessed_skill_ids: set[uuid.UUID],
    skill_id_to_name: dict[uuid.UUID, str],
) -> tuple[list[str], list[str]]:
    matched_ids = required_skill_ids & possessed_skill_ids
    missing_ids = required_skill_ids - possessed_skill_ids
    matched_names = sorted(skill_id_to_name.get(sid, str(sid)) for sid in matched_ids)
    missing_names = sorted(skill_id_to_name.get(sid, str(sid)) for sid in missing_ids)
    return matched_names, missing_names
