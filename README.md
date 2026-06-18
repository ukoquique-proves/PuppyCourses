# PuppyLinux Promo — Generador de Guiones para Videos

Este proyecto genera guiones YAML listos para producir videos promocionales de PuppyLinux
usando [VideoCreation](https://github.com/ukoquique-proves/PuppyCourses).

Los dos proyectos están completamente desacoplados. Este proyecto solo produce archivos de
configuración YAML. VideoCreation los consume como si hubieran sido escritos a mano.

---

## Estructura

```
.
├── script_generator.py     # Generador de guiones
├── requirements.txt        # Dependencias
├── tests/
│   └── test_script_generator.py
├── generated_configs/      # YAMLs generados (fallback local, se crea automáticamente)
├── docs/
│   ├── Comercializacion.md     # Estrategia de distribución y embudo de ventas
│   ├── Cursos_posibles.txt     # Propuestas de cursos con análisis de mercado
│   └── VideoCreation_handling.md # Arquitectura de integración
```

---

## Instalación

```bash
pip install -e ".[dev]"
```

Esto instala el proyecto en modo editable junto con las dependencias de desarrollo (`pytest`, `pyyaml`). Los tests y el CLI funcionan desde cualquier directorio sin necesidad de configurar `PYTHONPATH`.

---

## Configuración del inbox

El generador necesita saber dónde vive el inbox de VideoCreation. Resuelve la ruta en este orden:

1. Variable de entorno `VIDEOCREATION_INBOX` (recomendado, portable)
2. `../VideoCreation/watcher_folders/inbox` relativo a este proyecto (layout de hermanos)

Si el directorio no existe al escribir, se crea automáticamente. Si VideoCreation está en
otra ubicación, usá la variable de entorno o el flag `--out`.

Para configurar la opción 1, añadí esto a tu `.env` o shell:

```bash
export VIDEOCREATION_INBOX=/ruta/a/VideoCreation/watcher_folders/inbox
```

---

## Tipos de video

| Tipo              | Descripción                                      | Duración aprox. |
|-------------------|--------------------------------------------------|-----------------|
| `gancho`          | Corto e impactante. Problema → Solución → CTA    | 45–60 s         |
| `benchmark`       | Datos duros. RAM, tiempos de respuesta, métricas | 60–90 s         |
| `tutorial`        | Paso a paso. Instalación desde cero              | 90–120 s        |
| `pildora`         | Micro-contenido técnico para Devs                | 30–45 s         |
| `teledigitos_hack`| El "secreto" de productividad sin lag            | 45–60 s         |

---

## Uso desde la línea de comandos

```bash
# Video gancho para Kiro
python -m script_generator --type gancho --ide Kiro

# Benchmark con métricas reales
python -m script_generator --type benchmark --ide Cursor \
  --ram-puppy 310 --ram-windows 2800 \
  --resp-puppy 1.1 --resp-windows 4.9

# Píldora técnica con nombre de truco personalizado
python -m script_generator --type pildora --ide Trae \
  --truco-nombre "El Hack de la RAM"

# Tutorial para Trae, con ruta de salida personalizada
python -m script_generator --type tutorial --ide Trae \
  --install-minutes 8 \
  --out generated_configs/tutorial_trae.yaml
```

Por defecto los archivos se guardan en `generated_configs/<tipo>_<ide>.yaml`.

### Todos los parámetros

| Parámetro           | Default                   | Descripción                            |
|---------------------|---------------------------|----------------------------------------|
| `--type`            | (requerido)               | `gancho`, `benchmark`, `tutorial`, etc.|
| `--ide`             | `Cursor`                  | Nombre del IDE                         |
| `--puppy`           | `TrixieRetro`             | Versión de PuppyLinux                  |
| `--ram-puppy`       | `310`                     | RAM en MB de Puppy Linux en frío       |
| `--ram-windows`     | `2800`                    | RAM en MB de Windows en frío           |
| `--resp-puppy`      | `1.2`                     | Tiempo de respuesta IA en Puppy (seg)  |
| `--resp-windows`    | `4.8`                     | Tiempo de respuesta IA en Windows (seg)|
| `--install-minutes` | `10`                      | Minutos para instalación (tutorial)    |
| `--truco-nombre`    | `El Hack del Rendimiento` | Nombre del truco (pildora/teledigitos) |
| `--lang`            | `es`                      | Idioma del guion (`es` / `en`)         |
| `--orientation`     | `horizontal`              | `horizontal` o `vertical`              |
| `--title`           | (automático)              | Título del video                       |
| `--out`             | (automático)              | Ruta de salida del YAML                |

---

## Uso desde Python

```python
from script_generator import ScriptGenerator, VideoType

gen = ScriptGenerator()

# Generar string YAML
yaml_str = gen.generate_yaml(
    VideoType.GANCHO,
    data={"ide": "Kiro", "ram_puppy_mb": 310, "ram_windows_mb": 2800}
)
print(yaml_str)

# Generar y guardar directamente
out = gen.save_yaml(VideoType.BENCHMARK, data={"ide": "Windsurf"})
print(f"Guardado en: {out}")
```

---

## Flujo completo: de guion a video

VideoCreation corre un watcher en segundo plano que monitorea una carpeta `inbox`. Cuando
dejás un YAML ahí, lo procesa automáticamente y mueve el archivo según el resultado:

```
inbox/        → en espera
processing/   → renderizando
done/         → video listo en VideoCreation/output/
failed/       → error durante la generación
```

El flujo es simplemente:

```bash
# Generar y enviar al inbox (todo en un paso)
python script_generator.py --type gancho --ide Kiro
```

El destino por defecto se resuelve en este orden: `VIDEOCREATION_INBOX` env var →
`../VideoCreation/watcher_folders/inbox` relativo a este proyecto (sibling layout).

Si el directorio no existe al momento de escribir, se crea automáticamente.
Usá `--out` para especificar una ruta distinta de forma explícita.

Para forzar salida local sin tocar el inbox:

```bash
python script_generator.py --type gancho --ide Kiro --out generated_configs/gancho_kiro.yaml
```

---

## Tests

```bash
python -m pytest tests/ -v
```

Cubre los tres tipos de video, sustitución de variables, título automático, valores por
defecto y que el YAML renderizado sea siempre parseable.

---

## Estrategia de contenido

Ver `docs/Comercializacion.md` para el plan completo de distribución: YouTube, GitHub, Dev.to,
Reddit, embudo de email y micro-contenidos verticales.

Ver `docs/Cursos_posibles.txt` para las propuestas de cursos de pago y su análisis de mercado.

El repositorio público del proyecto está en:
https://github.com/ukoquique-proves/PuppyCourses
