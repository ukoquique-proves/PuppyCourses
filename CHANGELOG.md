# Changelog

All notable changes to this project will be documented here.

---

## [Unreleased]

---

## [0.4.0] — 2026-06-11

### Added
- `--data` CLI argument to load benchmark/video data directly from an external JSON or YAML file
- `validate_yaml` exported function and internal check to ensure the generated configuration is valid YAML before writing to disk
- Test coverage for `validate_yaml` and CLI data loading (`_load_data_file`), including CLI flag override behavior

### Changed
- CLI logic updated: explicit CLI arguments now correctly overlay and override values loaded from the `--data` file

---

## [0.3.0] — 2026-06-11

### Changed
- Restructured from a single flat `script_generator.py` into a proper package:
  - `script_generator/types.py` — `VideoType`, `DEFAULTS`, `AUTO_TITLES`
  - `script_generator/generator.py` — `ScriptGenerator`, `_default_inbox()`, CLI
  - `script_generator/__init__.py` — public exports
  - `script_generator/__main__.py` — `python -m script_generator` entry point
- Jinja2 templates moved from inline Python strings to `.jinja2` files under
  `script_generator/templates/` loaded via `PackageLoader`
- `save_yaml` now calls `generate_yaml` internally instead of rendering the template
  a second time independently
- `_build_context` is now only called once per `save_yaml` invocation (for filename
  derivation when `output_path` is `None`)
- Stale module docstring note `Copiar a: VideoCreation/src/script_generator.py` removed
- CLI examples in docstring corrected to `python -m script_generator`

### Added
- 4 new tests covering `save_yaml` and `_default_inbox()`:
  - `VIDEOCREATION_INBOX` env var is resolved correctly
  - Falls back to relative sibling path when env var is absent
  - Explicit `output_path` always overrides env var and sibling path
  - Missing directories are created automatically
- `.gitignore` expanded: `*.egg-info/`, `dist/`, `build/`, `.venv/`, IDE folders, OS files

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
