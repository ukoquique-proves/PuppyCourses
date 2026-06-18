from __future__ import annotations

from enum import Enum
from typing import Any, Dict


class VideoType(str, Enum):
    GANCHO       = "gancho"
    BENCHMARK    = "benchmark"
    TUTORIAL     = "tutorial"
    PILDORA      = "pildora"
    TELEDIGITOS  = "teledigitos_hack"


DEFAULTS: Dict[str, Any] = {
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
    "truco_nombre":         "El Hack del Rendimiento",
}

AUTO_TITLES: Dict[VideoType, str] = {
    VideoType.GANCHO:       "PuppyLinux + {ide}: IA a máxima velocidad",
    VideoType.BENCHMARK:    "Benchmark: {ide} en PuppyLinux vs Windows",
    VideoType.TUTORIAL:     "Instalar {ide} en PuppyLinux {puppy_version} — Guía completa",
    VideoType.PILDORA:      "Píldora Dev: IA en RAM mínima con {ide}",
    VideoType.TELEDIGITOS:  "El Secreto de Teledígitos: Programar sin Lag con {ide}",
}
