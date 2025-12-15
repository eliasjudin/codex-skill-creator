#!/usr/bin/env python3
"""
Skill Packager - Creates a zip archive of a skill folder (for sharing/backups)

Usage:
    python3 package_skill.py <path/to/skill-folder> [output-directory]

Example:
    python3 package_skill.py ~/.codex/skills/my-skill
    python3 package_skill.py ~/.codex/skills/my-skill ./dist

Note:
    Codex loads skills from on-disk `SKILL.md` files; it does not import archives.
"""

import sys
import zipfile
from pathlib import Path
from quick_validate import validate_skill


def package_skill(skill_path, output_dir=None):
    """
    Package a skill folder into a zip archive.

    Args:
        skill_path: Path to the skill folder
        output_dir: Optional output directory for the archive (defaults to current directory)

    Returns:
        Path to the created archive, or None if error
    """
    skill_path = Path(skill_path).resolve()

    # Validate skill folder exists
    if not skill_path.exists():
        print(f"❌ Error: Skill folder not found: {skill_path}")
        return None

    if not skill_path.is_dir():
        print(f"❌ Error: Path is not a directory: {skill_path}")
        return None

    # Validate SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"❌ Error: SKILL.md not found in {skill_path}")
        return None

    # Run validation before packaging
    print("🔍 Validating skill...")
    valid, message = validate_skill(skill_path)
    if not valid:
        print(f"❌ Validation failed: {message}")
        print("   Please fix the validation errors before packaging.")
        return None
    print(f"✅ {message}\n")

    # Determine output location
    skill_name = skill_path.name
    if output_dir:
        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path.cwd()

    archive_filename = output_path / f"{skill_name}.zip"

    # Create the archive (zip format)
    try:
        with zipfile.ZipFile(archive_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through the skill directory
            for file_path in skill_path.rglob('*'):
                if file_path.is_file():
                    # Calculate the relative path within the zip
                    arcname = file_path.relative_to(skill_path.parent)
                    zipf.write(file_path, arcname)
                    print(f"  Added: {arcname}")

        print(f"\n✅ Successfully packaged skill to: {archive_filename}")
        return archive_filename

    except Exception as e:
        print(f"❌ Error creating archive: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 package_skill.py <path/to/skill-folder> [output-directory]")
        print("\nExample:")
        print("  python3 package_skill.py ~/.codex/skills/my-skill")
        print("  python3 package_skill.py ~/.codex/skills/my-skill ./dist")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"📦 Packaging skill: {skill_path}")
    if output_dir:
        print(f"   Output directory: {output_dir}")
    print()

    result = package_skill(skill_path, output_dir)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
