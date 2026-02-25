# AGENTS Guide

This file defines repository rules for automated contributors and coding agents.

## Language

- Think in English.
- Reply in Chinese.
- For chart text rendered by matplotlib, prefer English labels/text to avoid garbled characters.

## Scope Rules

- Edit only files explicitly requested for the task.
- Treat the repository as shared; do not modify unrelated files.
- Do not perform git commit, reset, or history rewrite actions unless explicitly asked.

## Project Context

- Project type: PySide6 desktop application.
- Entrypoint: `python main.py`
- Local environment: `conda activate visulite`
- Test command: `python -m unittest discover -s tests -p "test_*.py"`

## Documentation Governance

When the task is documentation only:

- Keep language concise and professional.
- Keep commands copy/paste ready for PowerShell.
- Maintain `CHANGELOG.md` in Keep a Changelog format.
- Record user visible changes under `Unreleased`.

## PR and Issue Workflow

- PR structure should align with `.github/PULL_REQUEST_TEMPLATE.md`.
- Bug and feature intake should use `.github/ISSUE_TEMPLATE/*` forms.

