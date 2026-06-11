# Roadmap — PuppyLinux Promo & Course Project

Objetivo: posicionar PuppyLinux TrixieRetro como el entorno definitivo para programar
con IDEs de IA (Cursor, Trae, Windsurf, Kiro), construir una audiencia técnica real y
convertirla en alumnos del curso de pago.

---

## Fase 1 — Fundación técnica ✅ (completada)

- [x] `script_generator.py` con plantillas para los tres tipos de video: gancho, benchmark, tutorial
- [x] Integración con VideoCreation via Drop Folder Watcher (inbox YAML)
- [x] Resolución portable del inbox: env var → ruta relativa → fallback local
- [x] Tests unitarios para los tres tipos de video
- [x] `requirements.txt`, `.gitignore`, `.env.example`
- [x] README, CHANGELOG, ROADMAP

---

## Fase 2 — Producción del primer video gancho

El objetivo de esta fase es tener un video publicado en YouTube que genere tráfico al
repositorio de GitHub.

- [ ] Medir métricas reales en TrixieRetro: RAM en frío, RAM con IDE abierto, tiempo de
      respuesta del agente de IA vs. Windows con el mismo hardware
- [ ] Generar el YAML gancho con datos reales:
      `python script_generator.py --type gancho --ide Cursor --ram-puppy <real> --ram-windows <real>`
- [ ] Revisar y ajustar el `speech_content` generado si hace falta
- [ ] Producir el video con VideoCreation
- [ ] Crear el video en versión vertical (YouTube Shorts / Reels) con `orientation: vertical`
- [ ] Publicar en YouTube con título SEO optimizado
      Ejemplo: *"Configuré Cursor e IA en una PC de 2GB de RAM usando Puppy Linux (Y vuela)"*
- [ ] Subir el video Short a YouTube Shorts, TikTok e Instagram Reels

---

## Fase 3 — Repositorio GitHub como hub técnico

El repo es el verdadero gancho para programadores. Llegan del video, encuentran valor
técnico real y desde ahí se convierten en leads.

- [ ] Preparar el repo `PuppyCourses` en https://github.com/ukoquique-proves/PuppyCourses
- [ ] Escribir el `README.md` del repo con:
  - Benchmarks reales (tabla RAM / tiempo de respuesta)
  - Links a los videos de YouTube
  - Instrucciones de instalación
  - Banner/link a la lista de espera del curso
- [ ] Publicar scripts de instalación para Cursor, Trae, Windsurf y Kiro en TrixieRetro
- [ ] Publicar archivos de configuración listos para descargar

---

## Fase 4 — Video benchmark y video tutorial

Con el gancho publicado y el repo activo, producir los dos videos complementarios.

- [ ] Generar YAML benchmark con métricas reales:
      `python script_generator.py --type benchmark --ide Cursor`
- [ ] Producir y publicar el video benchmark (datos duros, comparativa visual)
- [ ] Generar YAML tutorial:
      `python script_generator.py --type tutorial --ide Cursor --install-minutes 10`
- [ ] Producir y publicar el video tutorial (instalación desde cero)
- [ ] Repetir ciclo para otros IDEs: Kiro, Trae, Windsurf

---

## Fase 5 — Embudo de conversión

Construir el puente entre el contenido gratuito y el curso de pago.

- [ ] Crear el Lead Magnet: script de post-instalación de TrixieRetro para devs
      (automatiza instalación de IDE + dependencias + persistencia)
- [ ] Crear landing page gratuita (Systeme.io o Carrd) para captura de emails
- [ ] Configurar secuencia de email marketing en Brevo o MailerLite:
  - Email 1 (inmediato): entrega del script
  - Email 2 (día 2): arquitectura de PuppyLinux — por qué la IA va más rápido
  - Email 3 (día 5): presentación del curso completo
- [ ] Publicar artículo técnico en Dev.to con benchmark e incrustación del video
- [ ] Publicar hilo en Reddit (r/linux, r/puppylinux, r/programming)
- [ ] Identificar y participar en comunidades hispanas de Discord y Telegram

---

## Fase 6 — Lanzamiento del Curso (Opción 1)

**Título:** *Entornos de Desarrollo de Alto Rendimiento: Optimización Extrema con Puppy Linux e IA*

- [ ] Definir plataforma de venta (Hotmart, Teachable, Gumroad u otra)
- [ ] Estructurar el temario completo:
  - Arquitectura de PuppyLinux en RAM vs. Docker / WSL
  - Configuración y personalización de TrixieRetro para desarrollo profesional
  - Integración de IDEs: Cursor, Trae, Windsurf, Kiro
  - Scripts de despliegue rápido — entorno listo en 5 minutos en cualquier máquina
- [ ] Grabar las lecciones
- [ ] Abrir preventa / lista de espera
- [ ] Lanzamiento oficial

---

## Fase 7 — Expansión (cursos avanzados)

Una vez validado el Curso 1:

- [ ] **Curso 2:** *Soberanía Tecnológica y Arquitectura Eficiente para Desarrolladores*
      (Arquitectura Hexagonal, Rust/Java, agentes de IA para refactorización)
- [ ] **Curso 3:** *Sistemas Operativos Minimalistas y Redes Operativas Soberanas*
      (Remasterización de PuppyLinux, redes locales resilientes, despliegue sin cloud)

---

## Mejoras técnicas pendientes (este proyecto)

- [ ] Módulo `github_publisher.py` — sube el YAML generado directamente al repo vía API
- [ ] Plantillas en inglés para alcance internacional
- [ ] Plantilla tipo `short` (30 s, vertical) como cuarto VideoType
- [ ] CLI interactivo con prompts guiados para usuarios no técnicos
