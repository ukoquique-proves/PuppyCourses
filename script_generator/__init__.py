"""
PuppyTeach — script_generator package.

Genera guiones YAML estructurados para videos promocionales de PuppyLinux,
listos para ser consumidos por VideoCreation via Drop Folder Watcher.

Usage:
    from script_generator import ScriptGenerator, VideoType

    gen = ScriptGenerator()
    yaml_str = gen.generate_yaml(
        VideoType.GANCHO,
        data={"ide": "Kiro", "ram_puppy_mb": 310, "ram_windows_mb": 2800},
    )
"""

from .generator import ScriptGenerator, main
from .types import VideoType

__all__ = ["ScriptGenerator", "VideoType", "main"]
