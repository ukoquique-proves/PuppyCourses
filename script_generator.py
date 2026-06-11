"""
script_generator.py — Generador de guiones estructurados para videos PuppyLinux.

Copiar a: VideoCreation/src/script_generator.py

Uso programático:
    from src.script_generator import ScriptGenerator, VideoType

    gen = ScriptGenerator()
    yaml_str = gen.generate_yaml(
        video_type=VideoType.GANCHO,
        data={
            "ide": "Cursor",
            "puppy_version": "TrixieRetro",
            "ram_puppy_mb": 310,
            "ram_windows_mb": 2800,
        }
    )

CLI:
    python -m src.script_generator --type gancho --ide Kiro --out config/gancho_kiro.yaml
    python -m src.script_generator --type benchmark --ide Cursor
    python -m src.script_generator --type tutorial --ide Trae --install-minutes 8
"""

from __future__ import annotations

import argparse
import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict

from jinja2 import BaseLoader, Environment, StrictUndefined

# Inbox path resolution (priority: env var → relative sibling → local fallback)
_HERE = Path(__file__).resolve().parent
_RELATIVE_INBOX = _HERE.parent / "VideoCreation" / "watcher_folders" / "inbox"

def _default_inbox() -> Path:
    """
    Resolve the VideoCreation inbox directory.
    Priority:
      1. VIDEOCREATION_INBOX env var (explicit, portable)
      2. ../VideoCreation/watcher_folders/inbox relative to this file (sibling layout)
      3. generated_configs/ local fallback (standalone / CI)
    """
    env_path = os.environ.get("VIDEOCREATION_INBOX")
    if env_path:
        return Path(env_path)
    if _RELATIVE_INBOX.parent.exists():
        return _RELATIVE_INBOX
    return _HERE / "generated_configs"


# ---------------------------------------------------------------------------
# Tipos de video
# ---------------------------------------------------------------------------

class VideoType(str, Enum):
    GANCHO    = "gancho"
    BENCHMARK = "benchmark"
    TUTORIAL  = "tutorial"


# ---------------------------------------------------------------------------
# Plantillas Jinja2
# ---------------------------------------------------------------------------

_TEMPLATES: Dict[VideoType, str] = {

    # --- GANCHO (corto/impactante, ~45-60 s) --------------------------------
    VideoType.GANCHO: """\
title: "{{ title }}"
language: {{ language }}
orientation: {{ orientation }}
subtitles_enabled: true
output_format: "mp4"
tts_rate: "{{ tts_rate }}"
image_engine: "{{ image_engine }}"

speech_content: |
  ¿Tu IDE de Inteligencia Artificial va lento?
  {{ ide }}, Windsurf, Kiro, Trae... son herramientas increíbles,
  pero Windows y Ubuntu consumen los recursos que tu agente de IA necesita.
  La solución existe y corre en RAM: Puppy Linux {{ puppy_version }}.
  Con solo {{ ram_puppy_mb }} megabytes de memoria en frío,
  le devolvés toda la potencia a tu IA.
  Bajate el script gratuito de instalación en el link de GitHub.
  El link está en la descripción.

visual_assets:
  asset_type: "text_prompts"
  prompts:
    - "A frozen, lagging IDE on a dark screen with a spinning loader — frustrated developer — dramatic red lighting, cinematic style"
    - "Split screen: left side Windows Task Manager at 90% RAM usage, right side Puppy Linux {{ puppy_version }} desktop using only {{ ram_puppy_mb }}MB RAM — clean minimal flat illustration"
    - "{{ ide }} IDE running smoothly on Puppy Linux {{ puppy_version }}, AI code suggestion appearing instantly — green neon glow, dark background, hacker aesthetic"
    - "GitHub repository page for PuppyCourses with a download script highlighted — clean UI screenshot style illustration"
""",

    # --- BENCHMARK (datos duros) -------------------------------------------
    VideoType.BENCHMARK: """\
title: "{{ title }}"
language: {{ language }}
orientation: {{ orientation }}
subtitles_enabled: true
output_format: "mp4"
tts_rate: "{{ tts_rate }}"
image_engine: "{{ image_engine }}"

speech_content: |
  Hipótesis: ¿puede {{ ide }} correr mejor en Puppy Linux {{ puppy_version }}
  que en un sistema tradicional?
  Veamos los datos reales.
  En Windows, el sistema consume {{ ram_windows_mb }} megabytes de RAM antes de abrir el IDE.
  En Puppy Linux {{ puppy_version }}, el sistema operativo ocupa solo {{ ram_puppy_mb }} megabytes.
  Eso significa {{ ram_diff_mb }} megabytes extra disponibles para tu agente de IA.
  Tiempo de respuesta del agente en Windows: {{ response_windows_sec }} segundos.
  Tiempo de respuesta en Puppy Linux: {{ response_puppy_sec }} segundos.
  Los números no mienten. Puppy Linux {{ puppy_version }} es el entorno ideal
  para programar con IA en hardware real.
  Todos los scripts y configuraciones están en GitHub, link en la descripción.

visual_assets:
  asset_type: "text_prompts"
  prompts:
    - "System monitor dashboard showing Windows using {{ ram_windows_mb }}MB RAM vs Puppy Linux {{ puppy_version }} using {{ ram_puppy_mb }}MB RAM — bar chart style, clean data visualization, blue and red colors"
    - "Stopwatch comparison: {{ response_windows_sec }}s label on left with Windows logo, {{ response_puppy_sec }}s label on right with Puppy Linux logo — minimal flat design, green winner highlight on right"
    - "{{ ide }} AI agent generating code at full speed on a dark terminal — green text stream, fast and fluid — cinematic tech aesthetic"
    - "GitHub repository showing benchmark scripts and results — developer-friendly UI illustration"
""",

    # --- TUTORIAL (educativo/paso a paso) ----------------------------------
    VideoType.TUTORIAL: """\
title: "{{ title }}"
language: {{ language }}
orientation: {{ orientation }}
subtitles_enabled: true
output_format: "mp4"
tts_rate: "{{ tts_rate }}"
image_engine: "{{ image_engine }}"

speech_content: |
  En este video vas a instalar y configurar {{ ide }} en Puppy Linux {{ puppy_version }}
  desde cero, en menos de {{ install_minutes }} minutos.
  Primero, descargá la ISO de {{ puppy_version }} desde el link oficial.
  Luego, grabala en un pendrive con Ventoy o Rufus.
  Al bootear, el sistema corre completamente en RAM:
  eso significa velocidad máxima desde el primer segundo.
  Una vez dentro, abrí el terminal y ejecutá el script de instalación
  que encontrás en el repositorio de GitHub en la descripción.
  El script instala {{ ide }}, configura las dependencias necesarias
  y monta la persistencia para que tu entorno no se pierda al reiniciar.
  En {{ install_minutes }} minutos tenés un entorno profesional con IA
  listo para trabajar en cualquier máquina.
  El link al script y al curso completo están en la descripción.

visual_assets:
  asset_type: "text_prompts"
  prompts:
    - "Puppy Linux {{ puppy_version }} boot screen loading from a USB drive — pixel art meets modern flat design, clean and colorful"
    - "Terminal window showing installation commands running step by step — dark background, green monospace font, progress bars completing"
    - "{{ ide }} opening for the first time on Puppy Linux desktop — clean workspace, AI chat panel visible, dark theme"
    - "Split screen: USB pendrive on the left, a fully configured {{ ide }} with AI running on the right — before/after style, satisfying minimal illustration"
""",
}

# Valores por defecto
_DEFAULTS: Dict[str, Any] = {
    "title":                None,
    "language":             "es",
    "orientation":          "horizontal",
    "tts_rate":             "-10%",
    "image_engine":         "cloudflare",
    "ide":                  "Cursor",
    "puppy_version":        "TrixieRetro",
    "ram_puppy_mb":         310,
    "ram_windows_mb":       2800,
    "response_puppy_sec":   1.2,
    "response_windows_sec": 4.8,
    "install_minutes":      10,
    "github_url":           "https://github.com/ukoquique-proves/PuppyCourses",
}

_AUTO_TITLES: Dict[VideoType, str] = {
    VideoType.GANCHO:    "PuppyLinux + {ide}: IA a máxima velocidad",
    VideoType.BENCHMARK: "Benchmark: {ide} en PuppyLinux vs Windows",
    VideoType.TUTORIAL:  "Instalar {ide} en PuppyLinux {puppy_version} — Guía completa",
}


# ---------------------------------------------------------------------------
# Clase principal
# ---------------------------------------------------------------------------

class ScriptGenerator:
    """Genera guiones YAML listos para usar con VideoCreation."""

    def __init__(self) -> None:
        self._env = Environment(
            loader=BaseLoader(),
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
        )

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
        ctx = dict(_DEFAULTS)
        if data:
            ctx.update(data)

        # ram_diff_mb calculado automáticamente
        if "ram_diff_mb" not in ctx:
            ctx["ram_diff_mb"] = ctx["ram_windows_mb"] - ctx["ram_puppy_mb"]

        # Título automático si no se provee
        if ctx.get("title") is None:
            ctx["title"] = _AUTO_TITLES[video_type].format(**ctx)

        template = self._env.from_string(_TEMPLATES[video_type])
        return template.render(**ctx)

    def save_yaml(
        self,
        video_type: VideoType,
        data: Dict[str, Any] | None = None,
        output_path: Path | str | None = None,
    ) -> Path:
        """
        Genera y guarda el YAML. Si no se provee output_path,
        lo guarda en config/<tipo>_<ide>.yaml dentro del proyecto.
        """
        content = self.generate_yaml(video_type, data)

        if output_path is None:
            ctx = dict(_DEFAULTS)
            if data:
                ctx.update(data)
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


if __name__ == "__main__":
    main()
