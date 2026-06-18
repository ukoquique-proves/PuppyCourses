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


def test_cli_flag_overrides_data_file_value(monkeypatch, tmp_path):
    """Explicit CLI args override values from the data file via main()."""
    from script_generator.generator import main
    import sys

    # Simulate: file says Cursor, CLI says Kiro — Kiro should win
    data_file = tmp_path / "bench.json"
    data_file.write_text(json.dumps({"ide": "Cursor", "ram_puppy_mb": 299, "ram_windows_mb": 2800}))
    out_file = tmp_path / "out.yaml"

    monkeypatch.setattr(sys, "argv", [
        "script_generator",
        "--type", "gancho",
        "--data", str(data_file),
        "--ide", "Kiro",  # override
        "--out", str(out_file)
    ])

    main()

    assert out_file.exists()
    parsed = yaml.safe_load(out_file.read_text())
    assert "Kiro" in parsed["speech_content"]
    assert "299" in parsed["speech_content"]


def test_pildora_and_teledigitos_use_parametric_puppy_version(gen):
    """Verify that puppy_version is no longer hardcoded in pildora and teledigitos_hack."""
    data = {"puppy_version": "FocalFossa"}

    # Test pildora
    res_pildora = gen.generate_yaml(VideoType.PILDORA, data)
    parsed_pildora = yaml.safe_load(res_pildora)
    assert "FocalFossa" in parsed_pildora["speech_content"]
    assert "TrixieRetro" not in parsed_pildora["speech_content"]

    # Test teledigitos_hack
    res_tele = gen.generate_yaml(VideoType.TELEDIGITOS, data)
    parsed_tele = yaml.safe_load(res_tele)
    assert "FocalFossa" in parsed_tele["speech_content"]
    assert "TrixieRetro" not in parsed_tele["speech_content"]


def test_pildora_and_teledigitos_honor_custom_title(gen):
    """Verify that pildora and teledigitos_hack now use the {{ title }} variable."""
    custom_title = "Mi Título Customizado"
    
    # Test pildora
    res_pildora = gen.generate_yaml(VideoType.PILDORA, {"title": custom_title})
    parsed_pildora = yaml.safe_load(res_pildora)
    assert parsed_pildora["title"] == custom_title

    # Test teledigitos_hack
    res_tele = gen.generate_yaml(VideoType.TELEDIGITOS, {"title": custom_title})
    parsed_tele = yaml.safe_load(res_tele)
    assert parsed_tele["title"] == custom_title


def test_pildora_and_teledigitos_use_auto_titles(gen):
    """Verify that pildora and teledigitos_hack use AUTO_TITLES when no title is provided."""
    # Test pildora auto-title
    res_pildora = gen.generate_yaml(VideoType.PILDORA, {"ide": "Trae", "truco_nombre": "Hack RAM"})
    parsed_pildora = yaml.safe_load(res_pildora)
    # AUTO_TITLES[VideoType.PILDORA] = "Píldora Dev: {truco_nombre} con {ide}"
    assert parsed_pildora["title"] == "Píldora Dev: Hack RAM con Trae"

    # Test teledigitos_hack auto-title
    res_tele = gen.generate_yaml(VideoType.TELEDIGITOS, {"ide": "Kiro", "truco_nombre": "El Super Hack"})
    parsed_tele = yaml.safe_load(res_tele)
    # AUTO_TITLES[VideoType.TELEDIGITOS] = "El Secreto de Teledígitos: {truco_nombre} con {ide}"
    assert parsed_tele["title"] == "El Secreto de Teledígitos: El Super Hack con Kiro"
    assert "Teledígitos" in parsed_tele["title"]  # Explicitly check for accent


def test_pildora_and_teledigitos_honor_context_variables(gen):
    """Verify that pildora and teledigitos_hack respect context variables like language and orientation."""
    custom_data = {
        "language": "en",
        "orientation": "vertical",
        "output_format": "mov",
        "tts_rate": "+5%",
        "image_engine": "dalle3"
    }

    for vtype in [VideoType.PILDORA, VideoType.TELEDIGITOS]:
        res = gen.generate_yaml(vtype, custom_data)
        parsed = yaml.safe_load(res)
        assert parsed["language"] == "en"
        assert parsed["orientation"] == "vertical"
        assert parsed["output_format"] == "mov"
        assert parsed["tts_rate"] == "+5%"
        assert parsed["image_engine"] == "dalle3"


def test_truco_nombre_is_reflected_in_auto_titles(gen):
    """Verify that truco_nombre is correctly used in AUTO_TITLES for PILDORA and TELEDIGITOS."""
    custom_truco = "Hack Extremo"
    data = {"truco_nombre": custom_truco}

    # Test pildora
    res_pildora = gen.generate_yaml(VideoType.PILDORA, data)
    parsed_pildora = yaml.safe_load(res_pildora)
    assert custom_truco in parsed_pildora["title"]

    # Test teledigitos_hack
    res_tele = gen.generate_yaml(VideoType.TELEDIGITOS, data)
    parsed_tele = yaml.safe_load(res_tele)
    assert custom_truco in parsed_tele["title"]
