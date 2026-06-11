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
