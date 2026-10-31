# Validacion de infraestructura - 2026-10-31
Ejecutado en pc_casa, Windows, Python 3.14.7, Git 2.45.1.
- 9 pruebas de scripts/test_quality.py: OK. Seleccion de sufijos,
  commits protegidos, push/refspec protegido, ref distinto al checkout,
  CI limitada a Python y umbrales de cobertura.
- git hook run pre-commit: exit 0, hook instalado mediante core.hooksPath.
- uv sync --locked: OK, python/uv.lock generado, 20 paquetes resueltos.
- ruff format --check: 3 archivos correctos. ruff check: OK.
- pytest ejemplo: 4 passed, cobertura 100%, XML/HTML/JUnit en .artifacts/python.
- Bloqueo main y develop: exit 1 en ambas (resultado esperado).
- git check-ignore: config del instalador queda excluida.
La calculadora es solo el ejemplo docente: NO valida AES ni requisitos funcionales.
JavaFX, Android y Unity no tienen proyectos implementados todavia; por ello sus
gates no se presentan como superados. Se incluyen contratos de tareas y
plantillas JaCoCo; hace falta importar cada proyecto real.
GitHub y act no ejecutados: no hay remoto conectado ni validacion Docker.
No se han creado commits, PR, main/develop con contenido ni evidencias de
participacion ficticias. HEAD inicial: chore/infra/python.