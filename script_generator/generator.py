from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any, Dict

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

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Genera un YAML de guion para VideoCreation"
    )
    p.add_argument("--type", required=True, choices=[t.value for t in VideoType],
                   help="Tipo de video: gancho | benchmark | tutorial")
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

    data: Dict[str, Any] = {
        "ide":                  args.ide,
        "puppy_version":        args.puppy,
        "ram_puppy_mb":         args.ram_puppy,
        "ram_windows_mb":       args.ram_windows,
        "response_puppy_sec":   args.resp_puppy,
        "response_windows_sec": args.resp_windows,
        "install_minutes":      args.install_minutes,
        "language":             args.lang,
        "orientation":          args.orientation,
    }
    if args.title:
        data["title"] = args.title

    gen = ScriptGenerator()
    out_path = gen.save_yaml(VideoType(args.type), data, args.out)
    print(f"✓ Guion guardado en: {out_path}")
    print("\n--- Preview ---")
    print(out_path.read_text(encoding="utf-8"))
