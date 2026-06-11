from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any, Dict, List

import yaml
from jinja2 import PackageLoader, Environment, StrictUndefined

from .types import AUTO_TITLES, DEFAULTS, VideoType

# ---------------------------------------------------------------------------
# Inbox path resolution
# ---------------------------------------------------------------------------

_HERE = Path(__file__).resolve().parent
_RELATIVE_INBOX = _HERE.parent.parent / "VideoCreation" / "watcher_folders" / "inbox"


def _default_inbox() -> Path:
    """
    Resolve the VideoCreation inbox directory.
    Priority:
      1. VIDEOCREATION_INBOX env var (explicit, portable) — recommended
      2. ../../VideoCreation/watcher_folders/inbox relative to this file (sibling layout)

    If the directory does not exist at write time, save_yaml creates it via mkdir.
    Use --out to override, or set VIDEOCREATION_INBOX for a custom path.
    """
    env_path = os.environ.get("VIDEOCREATION_INBOX")
    if env_path:
        return Path(env_path)
    return _RELATIVE_INBOX


# ---------------------------------------------------------------------------
# YAML schema validation
# ---------------------------------------------------------------------------

# Fields that VideoCreation's VideoConfiguration model requires (non-optional).
_REQUIRED_FIELDS: List[str] = ["title", "speech_content", "visual_assets"]

# Fields that must be present inside visual_assets.
_REQUIRED_VISUAL_FIELDS: List[str] = ["asset_type"]


def validate_yaml(content: str) -> None:
    """
    Parse `content` as YAML and verify it contains the fields required by
    VideoCreation's VideoConfiguration schema.

    Raises:
        ValueError: with a descriptive message listing every missing field.
    """
    try:
        parsed = yaml.safe_load(content)
    except yaml.YAMLError as exc:
        raise ValueError(f"YAML inválido: {exc}") from exc

    if not isinstance(parsed, dict):
        raise ValueError("El YAML no es un mapping de campos (dict esperado en la raíz).")

    missing = [f for f in _REQUIRED_FIELDS if not parsed.get(f)]
    if missing:
        raise ValueError(
            f"Campos requeridos por VideoCreation ausentes o vacíos: {missing}"
        )

    visual = parsed.get("visual_assets", {})
    if not isinstance(visual, dict):
        raise ValueError("'visual_assets' debe ser un mapping.")
    missing_visual = [f for f in _REQUIRED_VISUAL_FIELDS if not visual.get(f)]
    if missing_visual:
        raise ValueError(
            f"Campos requeridos dentro de 'visual_assets' ausentes: {missing_visual}"
        )


# ---------------------------------------------------------------------------
# ScriptGenerator
# ---------------------------------------------------------------------------

class ScriptGenerator:
    """Genera guiones YAML listos para usar con VideoCreation."""

    def __init__(self) -> None:
        self._env = Environment(
            loader=PackageLoader("script_generator", "templates"),
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def _build_context(
        self, video_type: VideoType, data: Dict[str, Any] | None
    ) -> Dict[str, Any]:
        """Merge defaults with caller data and compute derived fields."""
        ctx = dict(DEFAULTS)
        if data:
            ctx.update(data)
        if "ram_diff_mb" not in ctx:
            ctx["ram_diff_mb"] = ctx["ram_windows_mb"] - ctx["ram_puppy_mb"]
        if ctx.get("title") is None:
            ctx["title"] = AUTO_TITLES[video_type].format(**ctx)
        return ctx

    def generate_yaml(
        self,
        video_type: VideoType,
        data: Dict[str, Any] | None = None,
    ) -> str:
        """
        Renderiza la plantilla para `video_type` con las variables en `data`.
        Variables no presentes usan valores por defecto.

        Returns:
            String YAML listo para guardar como config de VideoCreation.
        """
        ctx = self._build_context(video_type, data)
        template = self._env.get_template(f"{video_type.value}.jinja2")
        return template.render(**ctx)

    def save_yaml(
        self,
        video_type: VideoType,
        data: Dict[str, Any] | None = None,
        output_path: Path | str | None = None,
    ) -> Path:
        """
        Genera y guarda el YAML. Si no se provee output_path,
        lo guarda en <inbox>/<tipo>_<ide>.yaml.
        """
        content = self.generate_yaml(video_type, data)
        validate_yaml(content)

        if output_path is None:
            ctx = self._build_context(video_type, data)
            ide_slug = ctx["ide"].lower().replace(" ", "_")
            output_path = _default_inbox() / f"{video_type.value}_{ide_slug}.yaml"

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
        return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

# CLI args that have explicit defaults — used to detect "was this actually set
# by the user?" so --data values aren't silently overridden by argparse defaults.
_CLI_DEFAULTS: Dict[str, Any] = {
    "ide":                  "Cursor",
    "puppy":                "TrixieRetro",
    "ram_puppy":            310,
    "ram_windows":          2800,
    "resp_puppy":           1.2,
    "resp_windows":         4.8,
    "install_minutes":      10,
    "lang":                 "es",
    "orientation":          "horizontal",
}

_CLI_TO_DATA_KEY: Dict[str, str] = {
    "ide":             "ide",
    "puppy":           "puppy_version",
    "ram_puppy":       "ram_puppy_mb",
    "ram_windows":     "ram_windows_mb",
    "resp_puppy":      "response_puppy_sec",
    "resp_windows":    "response_windows_sec",
    "install_minutes": "install_minutes",
    "lang":            "language",
    "orientation":     "orientation",
}


def _load_data_file(path: str) -> Dict[str, Any]:
    """Load benchmark data from a JSON or YAML file."""
    import json
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Archivo de datos no encontrado: {path}")
    text = p.read_text(encoding="utf-8")
    if p.suffix in (".yaml", ".yml"):
        return yaml.safe_load(text) or {}
    return json.loads(text)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Genera un YAML de guion para VideoCreation"
    )
    p.add_argument("--type", required=True, choices=[t.value for t in VideoType],
                   help="Tipo de video: gancho | benchmark | tutorial")
    p.add_argument("--data",            default=None,          help="JSON/YAML con datos de prueba (ej: pruebas_trixie.json)")
    p.add_argument("--ide",             default="Cursor",      help="Nombre del IDE")
    p.add_argument("--puppy",           default="TrixieRetro", help="Versión de PuppyLinux")
    p.add_argument("--ram-puppy",       type=int,   default=310,  help="RAM MB de Puppy en frío")
    p.add_argument("--ram-windows",     type=int,   default=2800, help="RAM MB de Windows en frío")
    p.add_argument("--resp-puppy",      type=float, default=1.2,  help="Tiempo respuesta IA Puppy (seg)")
    p.add_argument("--resp-windows",    type=float, default=4.8,  help="Tiempo respuesta IA Windows (seg)")
    p.add_argument("--install-minutes", type=int,   default=10,   help="Minutos instalación (tutorial)")
    p.add_argument("--lang",            default="es",             help="Idioma (es/en)")
    p.add_argument("--orientation",     default="horizontal",     choices=["horizontal", "vertical"])
    p.add_argument("--title",           default=None,             help="Título del video (opcional)")
    p.add_argument("--out",             default=None,             help="Ruta de salida YAML (opcional)")
    return p


def main() -> None:
    args = _build_parser().parse_args()

    # Start with file data (if provided), then overlay only CLI args that were
    # explicitly set by the user (i.e. differ from argparse defaults).
    data: Dict[str, Any] = _load_data_file(args.data) if args.data else {}

    for cli_key, data_key in _CLI_TO_DATA_KEY.items():
        cli_val = getattr(args, cli_key)
        if cli_val != _CLI_DEFAULTS[cli_key]:
            # User explicitly passed this flag — it wins over the file
            data[data_key] = cli_val
        elif data_key not in data:
            # Not in file either — use the argparse default
            data[data_key] = cli_val

    if args.title:
        data["title"] = args.title

    gen = ScriptGenerator()
    out_path = gen.save_yaml(VideoType(args.type), data, args.out)
    print(f"✓ Guion guardado en: {out_path}")
    print("\n--- Preview ---")
    print(out_path.read_text(encoding="utf-8"))
