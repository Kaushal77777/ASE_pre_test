# ASE pretest: PyPI requirements checker

TO RUN:
py check_requirements.py paper_requirements.txt

Requires Python 3.11 or newer. The checker uses only the standard library;
`requirements.txt` is intentionally empty. No pip installation is needed.

Run from this directory:

```powershell
python check_requirements.py requirements.txt
python check_requirements.py example_requirements.txt
python check_requirements.py sample_requirements.txt
python check_requirements.py paper_requirements.txt
```

Replace the input with your own exact `name==version` pins. Other requirement
syntax (ranges, extras, URLs, environment markers and wildcard pins) is rejected.
The count includes every physical line as requested; blank lines and comments
are skipped for API requests. Duplicate pins count as separate lines.

The API endpoints from https://docs.pypi.org/api/json/ are:

| Address | What it returns |
| --- | --- |
| `https://pypi.org/pypi/<name>/json` | Package metadata; 404 if the package does not exist. |
| `https://pypi.org/pypi/<name>/<version>/json` | Release metadata; 404 if the release does not exist. `urls` lists files with `upload_time`. |

For existing pins, the checker compares `urls[0]["upload_time"]` and prints
the oldest pin with its upload year. Missing packages and versions are printed
as counts. If timestamps tie, the first input pin wins. Releases without
files cannot be dated and are reported separately. Network/server failures
produce an error instead of classifying a package as missing.

The example file is input data, not a list of dependencies needed by this project.
`sample_requirements.txt` contains the five lines from the task's sample input.
Its expected output is:

```text
Dependencies checked: 5
Packages not on PyPI: 1
Versions not on PyPI: 1
Oldest pinned release: numpy==1.16.0 (2019)
```

Results reflect the current PyPI registry and can change over time.
Checking existence on PyPI does not establish that a package is trustworthy:
an attacker can register a plausible or invented package name.



