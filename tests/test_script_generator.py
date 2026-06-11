"""
Tests for script_generator.py

Run with:
    python -m pytest tests/ -v
"""

import pytest
import yaml

from script_generator import ScriptGenerator, VideoType


@pytest.fixture
def gen():
    return ScriptGenerator()


# ---------------------------------------------------------------------------
# generate_yaml — one test per VideoType
# ---------------------------------------------------------------------------

def test_gancho_renders_valid_yaml_with_substitutions(gen):
    data = {"ide": "Kiro", "puppy_version": "TrixieRetro", "ram_puppy_mb": 290, "ram_windows_mb": 2600}
    result = gen.generate_yaml(VideoType.GANCHO, data)

    parsed = yaml.safe_load(result)
    assert parsed["title"] == "PuppyLinux + Kiro: IA a máxima velocidad"
    assert parsed["language"] == "es"
    assert "Kiro" in parsed["speech_content"]
    assert "TrixieRetro" in parsed["speech_content"]
    assert "290" in parsed["speech_content"]
    assert parsed["visual_assets"]["asset_type"] == "text_prompts"
    assert len(parsed["visual_assets"]["prompts"]) == 4


def test_benchmark_renders_valid_yaml_with_substitutions(gen):
    data = {
        "ide": "Cursor",
        "puppy_version": "TrixieRetro",
        "ram_puppy_mb": 310,
        "ram_windows_mb": 2800,
        "response_puppy_sec": 1.1,
        "response_windows_sec": 4.9,
    }
    result = gen.generate_yaml(VideoType.BENCHMARK, data)

    parsed = yaml.safe_load(result)
    assert "Cursor" in parsed["title"]
    assert "Cursor" in parsed["speech_content"]
    assert "310" in parsed["speech_content"]
    assert "2800" in parsed["speech_content"]
    # ram_diff_mb should be auto-calculated: 2800 - 310 = 2490
    assert "2490" in parsed["speech_content"]
    assert "1.1" in parsed["speech_content"]
    assert "4.9" in parsed["speech_content"]


def test_tutorial_renders_valid_yaml_with_substitutions(gen):
    data = {"ide": "Trae", "puppy_version": "TrixieRetro", "install_minutes": 8}
    result = gen.generate_yaml(VideoType.TUTORIAL, data)

    parsed = yaml.safe_load(result)
    assert "Trae" in parsed["title"]
    assert "Trae" in parsed["speech_content"]
    assert "8" in parsed["speech_content"]
    assert len(parsed["visual_assets"]["prompts"]) == 4


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_custom_title_overrides_auto_title(gen):
    result = gen.generate_yaml(VideoType.GANCHO, {"ide": "Windsurf", "title": "Mi título custom"})
    parsed = yaml.safe_load(result)
    assert parsed["title"] == "Mi título custom"


def test_default_values_applied_when_no_data(gen):
    result = gen.generate_yaml(VideoType.GANCHO)
    parsed = yaml.safe_load(result)
    assert "Cursor" in parsed["speech_content"]   # default IDE
    assert parsed["language"] == "es"
    assert parsed["orientation"] == "horizontal"


def test_output_is_parseable_yaml_for_all_types(gen):
    """All three templates must produce valid YAML — catches Jinja2 template typos."""
    for vtype in VideoType:
        result = gen.generate_yaml(vtype)
        parsed = yaml.safe_load(result)
        assert isinstance(parsed, dict), f"{vtype} did not produce a dict"
        assert "speech_content" in parsed
        assert "visual_assets" in parsed


# ---------------------------------------------------------------------------
# save_yaml — path resolution
# ---------------------------------------------------------------------------

def test_save_yaml_uses_env_var_inbox(gen, monkeypatch, tmp_path):
    """VIDEOCREATION_INBOX env var overrides the default sibling path."""
    monkeypatch.setenv("VIDEOCREATION_INBOX", str(tmp_path))

    out = gen.save_yaml(VideoType.GANCHO, {"ide": "Kiro"})

    assert out.parent == tmp_path
    assert out.name == "gancho_kiro.yaml"
    assert out.exists()
    parsed = yaml.safe_load(out.read_text())
    assert "Kiro" in parsed["speech_content"]


def test_save_yaml_falls_back_to_relative_sibling(gen, monkeypatch, tmp_path):
    """Without env var, output goes to the relative sibling inbox path."""
    monkeypatch.delenv("VIDEOCREATION_INBOX", raising=False)

    # Redirect _RELATIVE_INBOX to tmp_path so the test is self-contained
    import script_generator.generator as gen_module
    original = gen_module._RELATIVE_INBOX
    gen_module._RELATIVE_INBOX = tmp_path
    try:
        out = gen.save_yaml(VideoType.BENCHMARK, {"ide": "Cursor"})
        assert out.parent == tmp_path
        assert out.name == "benchmark_cursor.yaml"
    finally:
        gen_module._RELATIVE_INBOX = original


def test_save_yaml_explicit_out_overrides_everything(gen, monkeypatch, tmp_path):
    """An explicit output_path always wins over env var and sibling path."""
    monkeypatch.setenv("VIDEOCREATION_INBOX", str(tmp_path / "inbox"))
    explicit = tmp_path / "custom" / "my_video.yaml"

    out = gen.save_yaml(VideoType.TUTORIAL, {"ide": "Trae"}, output_path=explicit)

    assert out == explicit
    assert out.exists()


def test_save_yaml_creates_missing_directories(gen, monkeypatch, tmp_path):
    """save_yaml creates the target directory if it doesn't exist yet."""
    target = tmp_path / "deeply" / "nested" / "dir" / "out.yaml"
    assert not target.parent.exists()

    gen.save_yaml(VideoType.GANCHO, output_path=target)

    assert target.exists()


# ---------------------------------------------------------------------------
# validate_yaml
# ---------------------------------------------------------------------------

from script_generator import validate_yaml


def test_validate_yaml_passes_for_all_types(gen):
    """All three templates produce YAML that passes schema validation."""
    for vtype in VideoType:
        content = gen.generate_yaml(vtype)
        validate_yaml(content)  # must not raise


def test_validate_yaml_raises_on_missing_required_field():
    invalid = "language: es\norientation: horizontal\n"
    with pytest.raises(ValueError, match="title"):
        validate_yaml(invalid)


def test_validate_yaml_raises_on_missing_visual_asset_type():
    invalid = (
        "title: Test\n"
        "speech_content: Hello\n"
        "visual_assets:\n"
        "  prompts:\n"
        "    - some prompt\n"
    )
    with pytest.raises(ValueError, match="asset_type"):
        validate_yaml(invalid)


def test_validate_yaml_raises_on_invalid_yaml():
    with pytest.raises(ValueError, match="YAML inválido"):
        validate_yaml("key: [unclosed")


def test_save_yaml_raises_before_writing_if_template_broken(gen, tmp_path, monkeypatch):
    """If a template produces invalid output, save_yaml raises before touching disk."""
    # Monkey-patch generate_yaml to return schema-invalid content
    monkeypatch.setattr(gen, "generate_yaml", lambda *_: "not_a_valid_config: true")
    target = tmp_path / "should_not_exist.yaml"

    with pytest.raises(ValueError):
        gen.save_yaml(VideoType.GANCHO, output_path=target)

    assert not target.exists()


# ---------------------------------------------------------------------------
# _load_data_file
# ---------------------------------------------------------------------------

from script_generator.generator import _load_data_file
import json


def test_load_data_file_json(tmp_path):
    f = tmp_path / "data.json"
    f.write_text(json.dumps({"ide": "Kiro", "ram_puppy_mb": 300}))
    result = _load_data_file(str(f))
    assert result["ide"] == "Kiro"
    assert result["ram_puppy_mb"] == 300


def test_load_data_file_yaml(tmp_path):
    f = tmp_path / "data.yaml"
    f.write_text("ide: Trae\nram_puppy_mb: 290\n")
    result = _load_data_file(str(f))
    assert result["ide"] == "Trae"
    assert result["ram_puppy_mb"] == 290


def test_load_data_file_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        _load_data_file(str(tmp_path / "nonexistent.json"))


def test_data_file_values_used_in_output(gen, tmp_path):
    """Values from --data file appear correctly in the rendered YAML."""
    data_file = tmp_path / "bench.json"
    data_file.write_text(json.dumps({
        "ide": "Windsurf",
        "ram_puppy_mb": 299,
        "ram_windows_mb": 2900,
        "response_puppy_sec": 0.9,
        "response_windows_sec": 5.1,
    }))
    file_data = _load_data_file(str(data_file))
    result = gen.generate_yaml(VideoType.BENCHMARK, file_data)
    parsed = yaml.safe_load(result)
    assert "Windsurf" in parsed["speech_content"]
    assert "299" in parsed["speech_content"]
    assert "2900" in parsed["speech_content"]
    # ram_diff_mb: 2900 - 299 = 2601
    assert "2601" in parsed["speech_content"]


def test_cli_flag_overrides_data_file_value(gen, tmp_path):
    """Explicit CLI args override values from the data file."""
    # Simulate: file says Cursor, CLI says Kiro — Kiro should win
    file_data = {"ide": "Cursor", "ram_puppy_mb": 310, "ram_windows_mb": 2800}
    cli_override = {"ide": "Kiro"}
    merged = {**file_data, **cli_override}
    result = gen.generate_yaml(VideoType.GANCHO, merged)
    assert "Kiro" in result
