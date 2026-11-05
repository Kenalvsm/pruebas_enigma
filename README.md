# Enigma - Reto 02
Monorrepo preparado a partir de ejemplos y contrato tecnico v1.1 (prioritario).
Estructura: python/, javafx/, android/, unity/, tests/, docs/.
Los PDF y ejemplos se conservan. El instalador del agente y sus credenciales se
excluyen de Git. No ejecutar git add -f sobre esos archivos.

## Alcance actual: solo Python
Todo el flujo automatico (CI/CD de GitHub, act, pre-commit y pre-push) se
redujo a Python. JavaFX, Android y Unity nos estan dando demasiados problemas:
dependencias de Gradle/AGP que no reproducen el entorno local, tareas que no
generan informes reales, emuladores, Unity en batchmode y coberturas que no
llegan al 80% por el propio andamiaje. Para no bloquear commits y PR por
herramientas ajenas al avance del equipo, esas plataformas quedan fuera de la
validacion.
Los directorios javafx/, android/ y unity/ se conservan como referencia del
contrato, pero no se ejecutan, no se miden y no cuentan como evidencia.
La calculadora de python/ es solo demostracion de la infraestructura: no
acredita los requisitos criptograficos. python/src/cifrado.py empieza P-01
(Vigenere A-Z, clave de 1 a 64 letras, ñ/tildes y signos sin avance) con sus
pruebas en python/tests/test_cifrado.py; el resto de requisitos sigue pendiente.

## Inicio por integrante
Instalar Git, Python para herramientas y uv. Ejecutar:
```
powershell -ExecutionPolicy Bypass -File scripts/install-hooks.ps1
uv sync --locked --project python
```
En Linux: `sh scripts/install-hooks.sh`. Cada persona configura su propia
identidad con git config user.name y user.email; no suplantar autores.

## Ramas y pruebas
Toda rama de trabajo debe terminar en la palabra python, por ejemplo
chore/infra/python o feature/descripcion/python. main y develop siguen siendo
las ramas comunes protegidas y no ejecutan gates.
El resto de ramas se ignora: pre-commit, pre-push, el workflow de GitHub y act
no ejecutan nada en ellas (los hooks lo avisan y terminan sin error), aunque el
push hacia main/develop sigue bloqueado.
En una rama python, pre-commit y pre-push ejecutan uv --locked, formato, lint,
pruebas y cobertura propia >=80%:
```
py -3 scripts/quality.py test --platform python
```
Commit en main/develop y push directo hacia ellas quedan bloqueados, incluso
con refspec desde otra rama; solo se envia la rama actual, sin tags ni borrados.
Integrar mediante PR.

## CI y act (solo Python)
.github/workflows/ci.yml se dispara con push a ramas acabadas en python y con
PR hacia main/develop desde esas mismas ramas; en cualquier otra rama el job se
omite. Genera JUnit, cobertura XML y HTML en .artifacts/python.
.actrc fija el job python-quality, asi que `act push` ejecuta solo Python.
`act push` verificado el 2026-11-05 con Docker Desktop: un unico job,
Job succeeded y artefacto python-informes en .artifacts/act/1.
origin apunta al repositorio y la rama chore/infra/python esta publicada; el
workflow de GitHub aun no se ha visto ejecutado alli.

## Proteccion en GitHub (ruleset pendiente)
Crear ruleset para main y develop: impedir borrados y force-push, exigir PR,
una aprobacion de otro miembro, conversaciones resueltas y check
`Python - lint, tests y cobertura >=80%`. No permitir bypass habitual.
Hooks locales pueden omitirse y no sustituyen reglas del servidor.
origin: https://github.com/Kenalvsm/pruebas_enigma.git; las ramas publicadas
hasta ahora salen de chore/infra/python. Falta crear el ruleset.

Cada integrante debe producir cambios reales con su identidad y abrir PR
contra develop; crear main/develop y el ruleset al revisar el primer PR.
Ver docs/REQUISITOS.md.

Pruebas de la infraestructura (independientes de la cobertura de la aplicacion):
`py -3 scripts/test_quality.py`.

Guia: [CI/CD y hooks](docs/GUIA_CI_CD.md). Validacion: [infraestructura](docs/VALIDACION_INFRA.md).
