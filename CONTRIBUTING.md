# Contributing to SceneCheck

Thanks for helping improve SceneCheck!

## Before opening a pull request
1. Search existing issues to avoid duplicates.
2. For larger changes, open an issue describing the problem and proposed approach.
3. Keep changes focused and explain how you tested them.
4. Never commit private footage, credentials, API keys, or generated reports containing sensitive material.

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Quality checks

```bash
python -m unittest discover -s tests -v
```

## Pull request checklist
- [ ] The change solves a clearly described problem.
- [ ] Tests are added or updated where practical.
- [ ] README or UI guidance is updated if behavior changes.
- [ ] No secrets or private media are included.
