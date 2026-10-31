# Enigma - Reto 02
Monorrepo preparado a partir de ejemplos y contrato tecnico v1.1 (prioritario).
Estructura: python/, javafx/, android/, unity/, tests/, docs/.
Los PDF y ejemplos se conservan. El instalador del agente y sus credenciales se
excluyen de Git. No ejecutar git add -f sobre esos archivos.

## Inicio por integrante
Instalar Git, Python para herramientas y uv. Ejecutar:
```
powershell -ExecutionPolicy Bypass -File scripts/install-hooks.ps1
uv sync --locked --project python
```
En Linux: `sh scripts/install-hooks.sh`. Cada persona configura su propia
identidad con git config user.name y user.email; no suplantar autores.

## Ramas y pruebas
Usar feature/descripcion/python, feature/descripcion/javafx,
feature/descripcion/android o feature/descripcion/unity. El ultimo segmento
selecciona las pruebas LOCALES. Sufijos desconocidos y HEAD separado bloqueados.
Commit en main/develop y push directo hacia ellas bloqueados, incluso con
refspec desde otra rama. Integrar mediante PR.
```
python scripts/quality.py test --platform python
python scripts/quality.py test --platform javafx
python scripts/quality.py test --platform android
python scripts/quality.py test --platform unity
```
pre-commit y pre-push ejecutan pruebas y cobertura propia >=80%. Python tambien
formato y lint. Faltan proyectos o tests: fallo, nunca verde ficticio.
JavaFX/Android: Gradle Wrapper real, JUnit y JaCoCo XML. Leer README de plataforma.
Unity: instalar Unity 6.3, Test Framework y Code Coverage; UNITY_EDITOR debe ser
la ruta del editor. Configurar filtros de assemblies propios y tests separados.

CI GitHub ejecuta SOLO Python en todo push y PR, conforme contrato 3.5/6.3.
Genera JUnit, cobertura XML y HTML. La cobertura de la calculadora de ejemplo
no acredita requisitos criptograficos. act: con Docker, `act push -j python-quality`.
No se ha ejecutado act ni GitHub hasta disponer de Docker/remoto.

## Proteccion en GitHub (pendiente de vincular remoto)
Crear ruleset para main y develop: impedir borrados y force-push, exigir PR,
una aprobacion de otro miembro, conversaciones resueltas y check
`Python - lint, tests y cobertura >=80%`. No permitir bypass habitual.
Hooks locales pueden omitirse y no sustituyen reglas del servidor.
No hay remote configurado ni push efectuado por esta preparacion.

No se han creado commits: cada integrante debe producir cambios reales con
su identidad. Tras revisar, hacer el primer commit desde chore/infra/python;
crear main/develop desde ese commit y trabajar por PR. Ver docs/REQUISITOS.md.

Pruebas de la infraestructura (independientes de cobertura de aplicaciones):
`py -3 scripts/test_quality.py`. Plantillas JaCoCo: archivos *.gradle.example;
adaptarlos al importar proyectos reales, sin crear compilaciones ficticias.
