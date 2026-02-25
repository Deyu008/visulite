# Contributing to VisuLite Studio

Thanks for contributing to VisuLite Studio, a PySide6 desktop analytics application.

## Development Setup

Use the `visulite` conda environment for all local work.

```powershell
conda create -n visulite python=3.11 -y
conda activate visulite
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Run the app locally:

```powershell
python main.py
```

## Testing

Run tests before opening or updating a pull request:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

If you run tests in a headless shell, use:

```powershell
$env:MPLBACKEND = "Agg"
$env:QT_QPA_PLATFORM = "offscreen"
python -m unittest discover -s tests -p "test_*.py"
```

## Pull Requests

- Keep changes focused and avoid unrelated refactors.
- Follow the PR template in `.github/PULL_REQUEST_TEMPLATE.md`.
- Include a short problem statement, approach, and local test evidence.
- Update `CHANGELOG.md` under `Unreleased` for user visible changes.

## Issues

Use the GitHub issue templates:

- `.github/ISSUE_TEMPLATE/bug_report.yml`
- `.github/ISSUE_TEMPLATE/feature_request.yml`
