"""Check exact name==version pins against PyPI without installing packages."""

import argparse
from datetime import datetime
import json
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import urlopen


def fetch_json(url):
    """Return None only for a 404; other failures must not mean 'missing'."""
    try:
        with urlopen(url, timeout=15) as response:
            return json.load(response)
    except HTTPError as error:
        if error.code == 404:
            return None
        raise


def check_requirements(path, fetch=fetch_json):
    lines = Path(path).read_text(encoding="utf-8-sig").splitlines()
    missing_packages = []
    missing_versions = []
    oldest = None
    no_files = []

    for number, line in enumerate(lines, start=1):
        pin = line.split("#", 1)[0].strip()
        if not pin:
            continue
        match = re.fullmatch(r"([A-Za-z0-9][A-Za-z0-9._-]*)\s*==\s*([^\s=]+)", pin)
        if not match or "*" in match[2]:
            raise ValueError(f"Line {number}: expected an exact name==version pin")
        name, version = match.groups()
        pin = f"{name}=={version}"
        base = f"https://pypi.org/pypi/{quote(name, safe='')}"

        if fetch(f"{base}/json") is None:
            missing_packages.append(name)
            continue
        release = fetch(f"{base}/{quote(version, safe='')}/json")
        if release is None:
            missing_versions.append(pin)
            continue

        files = release["urls"]
        if not files:
            no_files.append(pin)
            continue
        # The task specifies the first listed file, not the earliest file.
        uploaded = datetime.fromisoformat(files[0]["upload_time"])
        if oldest is None or uploaded < oldest[0]:
            oldest = (uploaded, pin)

    return {
        "lines": len(lines),
        "missing_packages": missing_packages,
        "missing_versions": missing_versions,
        "oldest": oldest[1] if oldest else None,
        "oldest_year": oldest[0].year if oldest else None,
        "no_files": no_files,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", nargs="?", default="requirements.txt")
    args = parser.parse_args()
    try:
        result = check_requirements(args.file)
    except (OSError, URLError, ValueError, KeyError, TypeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Dependencies checked: {result['lines']}")
    print(f"Packages not on PyPI: {len(result['missing_packages'])}")
    print(f"Versions not on PyPI: {len(result['missing_versions'])}")
    oldest_label = (
        f"{result['oldest']} ({result['oldest_year']})"
        if result["oldest"] else "none"
    )
    print(f"Oldest pinned release: {oldest_label}")
    if result["no_files"]:
        print("Releases without files (no upload time): " + ", ".join(result["no_files"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
