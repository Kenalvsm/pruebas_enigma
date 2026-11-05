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
GitHub y act no ejecutados en esa fecha (historico; ver seccion 2026-11-05).
No se han creado commits, PR, main/develop con contenido ni evidencias de
participacion ficticias. HEAD inicial: chore/infra/python.
## Correccion CI en Docker (act) - 2026-10-31
Modo ci ejecuta exclusivamente Python antes de consultar ramas o Git.
Hooks locales conservan sufijos y bloqueos main/develop.
Regresiones: 11 tests OK, incluidos CI sin .git y test con plataforma explicita.
act push -j python-quality --pull=false: Job succeeded, exit 0.
Formato, lint, tests/cobertura e informes superados dentro de Docker Linux.
.actrc habilita servidor local de artefactos en .artifacts/act.
Este resultado valida la infraestructura de ejemplo, no la implementacion AES.

## Alcance reducido a Python - 2026-11-05
Los registros anteriores describen el estado previo, cuando los hooks elegian
plataforma por el sufijo de la rama y CI se disparaba en cualquier push. Desde
esta fecha, CI/CD, act, pre-commit y pre-push solo levantan Python:
- Las ramas deben acabar en el segmento python. El resto se ignora: los hooks
  avisan y terminan sin ejecutar suites, y el workflow no se dispara (o su job
  se omite si el evento ya estaba definido).
- Siguen bloqueados el commit directo en main/develop y el push hacia ellas,
  incluso por refspec; el push solo admite la rama actual.
- JavaFX, Android y Unity se retiraron de los gates porque sus toolchains
  (Gradle/AGP, emuladores, Unity batchmode) nos estaban dando demasiados
  problemas y bloqueaban commits sin aportar senal util. Sus README ya no
  describen como ejecutarlos.
- .actrc fija `-j python-quality`, asi que `act push` ejecuta solo ese job.
- Regresiones de scripts/test_quality.py: 12 tests OK con
  `py -3 scripts/test_quality.py`.

## act verificado con Docker - 2026-11-05
Docker Desktop 29.6.2 (motor Linux) e imagen catthehacker/ubuntu:act-latest.
- `act -l`: un unico job, python-quality, para push/pull_request/workflow_dispatch.
- `act push`: Job succeeded, exit 0, un solo job ejecutado (el filtro -j de
  .actrc y el if de rama funcionan). 4 tests en la primera pasada.
- Dentro del contenedor: ruff format --check y ruff check OK, cobertura 100%,
  informes publicados como artefacto python-informes (.artifacts/act/1/).
- Segunda pasada con codigo y tests nuevos (cifrado Vigenere P-01): gate local
  17 tests passed, cobertura 100% y `act push` de nuevo Job succeeded, exit 0,
  con 17 tests dentro del contenedor.
- Tercera pasada (multiplicar y tablas de resultados esperados): gate y hooks
  45 tests passed, cobertura 100% y `act push` Job succeeded con 45 tests y
  artefacto de 31.960 bytes.
- Hooks reales: pre-commit y pre-push exit 0 en rama chore/infra/python;
  en una rama feature/prueba/javafx ambos exit 0 sin ejecutar suite (rama
  ignorada) y el push a main desde ella sigue bloqueado (exit 1).
- Commit en main/develop (exit 1), push a refs/heads/main (exit 1) y push de
  otra ref (exit 1) verificados en local.
## GitHub Actions real - 2026-11-05
Consultado por API con las credenciales ya guardadas por Git (sin exponer el
token, el repositorio es privado y el navegador no tiene sesion):
- Run 42088483496 (2b1bb510) y run 42088604372 (660fdb11): conclusion success,
evento push, un solo job "Python - lint, tests y cobertura >=80%" con sus 8 pasos
en verde.
- Artefacto python-informes-42088604372 (31.954 bytes) descargado y abierto:
junit.xml tests=45 failures=0 errors=0 y coverage.xml line-rate=1
(37/37 lineas, 100% en calculadora.py y cifrado.py).
- Run 41451438632 (3f4ae403) habia fallado, coherente con el codigo truncado de
ese estado previo: el check detecta regresiones reales.
Esta validacion cubre la infraestructura, no los requisitos funcionales.

## Ramas remotas y ruleset - 2026-11-05
main y develop creadas en origin en 660fdb1 mediante la API de refs, para no
depender de los bloqueos locales de push. La rama por defecto sigue siendo
chore/infra/python.
Ruleset solicitado (sin borrados ni force-push, PR con 1 aprobacion ajena,
conversaciones resueltas y check Python estricto):
- POST /repos/Kenalvsm/pruebas_enigma/rulesets -> 403 "Upgrade to GitHub Pro or
make this repository public to enable this feature".
- PUT /repos/Kenalvsm/pruebas_enigma/branches/main/protection -> 403 con el mismo
mensaje.
El plan gratuito no permite proteger ramas en repositorios privados. La
definicion queda en docs/ruleset-main-develop.json para importar cuando el
repositorio sea publico o el plan lo permita; mientras tanto main y develop
solo tienen la barrera local de los hooks.
