#!/usr/bin/env python3
"""
Quick validation script for Codex skills.

Validates only what Codex cares about for discovery:
- `SKILL.md` exists
- YAML frontmatter parses
- `name` and `description` are present, non-empty, and within limits
"""

import sys
import yaml
from pathlib import Path
from typing import Optional

NAME_MAX_LEN = 100
DESCRIPTION_MAX_LEN = 500


def _sanitize_one_line(value: str) -> str:
    # Codex sanitizes to one line; mimic that by collapsing all whitespace.
    return " ".join(value.split())


def _extract_frontmatter(markdown_text: str) -> Optional[str]:
    if not markdown_text.startswith("---"):
        return None

    lines = markdown_text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            return "\n".join(lines[1:idx])
    return None


def validate_skill(skill_path):
    """Basic validation of a Codex skill directory."""
    skill_path = Path(skill_path)

    # Check SKILL.md exists
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found"

    # Read and validate frontmatter
    content = skill_md.read_text()
    frontmatter_text = _extract_frontmatter(content)
    if frontmatter_text is None:
        return False, "Invalid or missing YAML frontmatter (expected leading '---' ... '---')"

    # Parse YAML frontmatter
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return False, "Frontmatter must be a YAML dictionary"
    except yaml.YAMLError as e:
        return False, f"Invalid YAML in frontmatter: {e}"

    # Check required fields
    if 'name' not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if 'description' not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    # Extract name for validation
    name = frontmatter.get('name', '')
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}"
    name = _sanitize_one_line(name)
    if not name:
        return False, "Name must be non-empty"
    if len(name) > NAME_MAX_LEN:
        return False, f"Name is too long ({len(name)} characters). Maximum is {NAME_MAX_LEN} characters."

    # Extract and validate description
    description = frontmatter.get('description', '')
    if not isinstance(description, str):
        return False, f"Description must be a string, got {type(description).__name__}"
    description = _sanitize_one_line(description)
    if not description:
        return False, "Description must be non-empty"
    if len(description) > DESCRIPTION_MAX_LEN:
        return (
            False,
            f"Description is too long ({len(description)} characters). "
            f"Maximum is {DESCRIPTION_MAX_LEN} characters.",
        )

    return True, "Skill is valid!"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <skill_directory>")
        sys.exit(1)
    
    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)
