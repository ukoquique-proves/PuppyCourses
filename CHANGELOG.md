# Changelog

All notable changes to this project will be documented here.

---

## [Unreleased]

---

## [0.2.0] — 2026-06-11

### Added
- `requirements.txt` with pinned versions: `jinja2==3.1.4`, `pyyaml==6.0.2`, `pytest==8.3.5`
- `tests/test_script_generator.py` — 6 tests covering all three video types, variable
  substitution, auto-title generation, default values, and YAML validity on every template
- `_default_inbox()` — portable path resolution for the VideoCreation inbox:
  1. `VIDEOCREATION_INBOX` environment variable
  2. `../VideoCreation/watcher_folders/inbox` relative to this project (sibling layout)
  3. `generated_configs/` local fallback (standalone / CI)
- `CHANGELOG.md` (this file)

### Changed
- `save_yaml` default output path now uses `_default_inbox()` instead of a hardcoded
  absolute path, making the project portable across machines and users
- README updated to document the three-step inbox path resolution, add a Tests section,
  and fix the discrepancy between documented and actual default output path

### Fixed
- Hardcoded `/root/a_VIDEO_GENERATION/...` absolute path in `save_yaml` that silently
  broke on any machine other than the original development environment

---

## [0.1.1] — 2026-06-11

### Changed
- `save_yaml` default output path updated to write directly to the VideoCreation
  `watcher_folders/inbox/` directory, replacing the previous `generated_configs/` local
  fallback, following the Drop Folder Watcher architecture described in
  `VideoCreation_handling.md`
- README updated to reflect the new watcher-based workflow

---

## [0.1.0] — 2026-06-11

### Added
- `script_generator.py` — `ScriptGenerator` class with three Jinja2-based video script
  templates: `gancho`, `benchmark`, `tutorial`
- CLI interface: `python script_generator.py --type <type> [options]`
- Auto-generated titles per video type when `--title` is not provided
- Auto-calculated `ram_diff_mb` from `ram_windows_mb - ram_puppy_mb`
- `Cursos_posibles.txt` updated to include Kiro alongside Cursor, Trae, and Windsurf
  in the IDE list for the Opción 1 course syllabus
- `README.md` documenting project structure, CLI usage, Python API, and full
  video production workflow
