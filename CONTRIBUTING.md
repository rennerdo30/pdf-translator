# Contributing to PDF Translator

Thanks for helping improve this project.

## Development Setup

```bash
git clone https://github.com/rennerdo30/pdf-translator.git
cd pdf-translator
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
```

## Local Checks

Run these before opening a pull request:

```bash
python -m pytest
python -m compileall -q src tests
python -m build
```

## Branches and Commits

- Create focused branches from `master`
- Keep commits small and descriptive
- Include tests when fixing bugs or adding behavior

## Pull Requests

- Link related issues
- Describe behavior changes clearly
- Include validation steps and results

## Reporting Bugs

Please use the GitHub bug report template and include:

- steps to reproduce
- expected behavior
- actual behavior
- environment details (OS, Python version, provider/model)
