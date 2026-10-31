# Guia CI/CD - Enigma
Repositorio: https://github.com/Kenalvsm/pruebas_enigma.git
Raiz local: C:\Users\WinterOS\vento\ejemplos

## Preparacion y uso
```powershell
git config core.hooksPath .githooks
py -3 -m uv sync --locked --project python
py -3 scripts/test_quality.py
git switch -c feature/cambio/python
git hook run pre-commit
```
Ramas: feature/cambio/python, feature/cambio/javafx, feature/cambio/android,
feature/cambio/unity. main y develop son ramas comunes protegidas.

## Diferencias entre hooks
Ambos hooks son scripts locales de Git, instalados mediante `core.hooksPath=.githooks`. No son el workflow de GitHub ni requieren Docker. Ambos seleccionan la suite por el sufijo de la rama y exigen tests e informes reales; en Python ejecutan instalación bloqueada, formato, lint y cobertura >=80%.

| Comprobación | pre-commit | pre-push |
|---|---|---|
| Momento | Antes de crear el commit local | Antes de enviar referencias al remoto |
| Si falla | No se crea el commit | No se envía ese push; los commits locales permanecen |
| main/develop como rama actual | Bloqueado | Bloqueado |
| Destino remoto main/develop desde otra rama | No interviene: no conoce el destino | Bloqueado, incluso mediante refspec |
| Qué tests ejecuta | Suite local del sufijo | La misma suite, repetida antes de enviar |
| Refs enviadas | No las comprueba | Solo permite la rama actual, sin tags, borrados ni otras ramas |

En esta implementación pre-commit NO ejecuta exclusivamente tests rápidos ni pre-push añade cobertura por primera vez: ambos llaman a la misma suite completa. Los tests se ejecutan sobre el árbol de trabajo actual, no sobre una copia aislada del índice. Revisar `git diff` y `git diff --cached` antes del commit.

El framework llamado pre-commit es opcional; tener `.pre-commit-config.yaml` no sustituye la instalación de los hooks nativos. No mezclar instalaciones sin revisar `core.hooksPath`. `prevent_protected_branch_commit.sh` es una alternativa del ejemplo y no es el ejecutor activo.

No usar `--no-verify`. Las reglas del servidor GitHub deben exigir PR, revisión ajena, check Python y restringir force-push/borrado en main/develop: los hooks se pueden desactivar localmente.

## Docker y act: comandos validados
Con Docker Desktop iniciado en contenedores Linux:
```powershell
cd C:\Users\WinterOS\vento\ejemplos
$actDir = "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\nektos.act_Microsoft.Winget.Source_8wekyb3d8bbwe"
$env:Path += ";$actDir"
docker info
act --version
act -l
act push -j python-quality
# Con imagen ya descargada, evitar forzar descarga:
act push -j python-quality --pull=false
```
Esperar Job succeeded. El numero de tests depende del codigo: 4 corresponde
solo al ejemplo actual. .actrc conserva informes en .artifacts/act.
El modo ci no necesita Git dentro del contenedor ni un remoto para correr act.

## Python y CI remoto
Python 3.14, uv.lock versionado, Ruff formato/lint y pytest con pytest-cov.
En todo push y PR se ejecuta solo Python segun contrato prioritario.
Umbral 80%; JUnit XML, cobertura XML/HTML se generan y publican como artefactos.
JavaFX, Android y Unity tienen ejecuciones locales con informes por aplicacion.

## JavaFX
Java 25 LTS, Gradle Wrapper real, JUnit y JaCoCo.
```powershell
cd javafx
.\gradlew.bat test jacocoTestReport javadoc
```
JUnit: parser R2AE, AES-GCM, PBKDF2, contraseña aleatoria de 16 caracteres,
casos 0B, 1B, 1MiB y >=20MiB; bytes/SHA-256, errores, no sobrescritura,
.part, autenticacion y vectores cruzados Python/Android.
UI: Alerts, seleccion, vista previa limitada y flujo de errores aparte.
JaCoCo XML: build/reports/jacoco/test/jacocoTestReport.xml, >=80% propio.

## Android
Unitarias JVM en app/src/test: logica AES/R2AE, Cesar, claves/desplazamientos
incorrectos, cabeceras/truncado, archivos y errores. app/src/androidTest:
selector ACTION_OPEN_DOCUMENT, compartir/ContentResolver, PNG recuperado,
avisos y persistencia de estado; emulador/dispositivo requerido.
```powershell
cd android
.\gradlew.bat testDebugUnitTest
.\gradlew.bat jacocoTestReport
.\gradlew.bat connectedDebugAndroidTest
# Solo al configurar Dokka:
.\gradlew.bat dokkaHtml
```
App solo descifra; no implementar cifrado nuevo para satisfacer los tests.
XML requerido por hooks: app/build/reports/jacoco/jacocoTestReport/jacocoTestReport.xml.
La tarea JaCoCo debe crearse/configurarse para el AGP real. Medir >=80% JVM/Kotlin.
KDoc/Dokka documentan Kotlin; instrumentacion no equivale a tests unitarios.

## Unity 6.3
Test Framework y Code Coverage; UNITY_EDITOR con ruta real de 6000.3.x.
EditMode: Cesar, normalizacion, rondas, vidas y estados con semilla controlada.
PlayMode: Rigidbody2D/Collider2D, puerta trigger, una perdida de vida por evento,
reinicio/pausa/victoria/derrota. Cinco rondas, cuatro errores por vida, tres vidas;
trim y espacios, vocales acentuadas, Ñ conservada; vacios no penalizan.
```powershell
cd C:\Users\WinterOS\vento\ejemplos
py -3 scripts/quality.py test --platform unity
```
El hook ejecuta EditMode/PlayMode y lee OpenCover; filtros de assemblies propios
en unity/coverage-assemblies.txt. >=80% propio; tests y motor no cuentan.
Conservar informes, logs, capturas y probar Windows 11 x64 aparte.


## Requisitos previos y estado real
Los comandos Gradle solo funcionan al importar los proyectos reales y sus wrappers.
La tarea jacocoTestReport de Android debe configurarse con las rutas del AGP usado;
Dokka es opcional. Javadoc documenta Java, KDoc/Dokka Kotlin y comentarios XML C#.
No aplicar Javadoc a Python, Kotlin o Unity como si fueran Java.
Los informes locales de JavaFX, Android y Unity no sustituyen pruebas funcionales,
interoperabilidad ni demostraciones. Solo Python tiene job remoto segun contrato.
La calculadora es una demostracion de CI, no un resultado de aceptacion del producto.

## Javadoc: autoria y generacion
Autor solicitado: **Kenneth Alvarez**. Usar `@author Kenneth Alvarez` en la
cabecera de cada clase propia que corresponda y habilitar la opcion author.
No cambiar autores de bibliotecas externas ni identidades de commits Git.
Ver `javafx/JAVADOC.md`, la plantilla `.java.example` y `scripts/generate-javadoc.ps1`.
La carpeta javafx aun no contiene clases Java: no existe una API de aplicacion
que documentar en este estado. La guia HTML generada no es Javadoc.

## Configurar el remoto y flujo completo
```powershell
git remote -v
# Solo si origin todavia no existe:
git remote add origin https://github.com/Kenalvsm/pruebas_enigma.git
git switch -c feature/documentacion/python
git diff
git add docs README.md scripts javafx
git diff --cached
git commit -m "docs: documenta hooks CI y pruebas por plataforma"
git push -u origin feature/documentacion/python
```
Si origin existe y apunta a otra URL, comprobarlo antes de cambiarlo. Abrir PR a
develop y solicitar revision. El push ejecuta hooks locales; GitHub ejecuta CI
cuando recibe los commits. act simula el workflow en Docker sin publicar codigo.

## Como diseñar los tests
Mantener logica de dominio separada de pantallas, archivos y motor para probarla
con entradas deterministas, un resultado esperado y una sola causa de fallo.
Usar directorios temporales y fixtures publicos, sin secretos ni rutas personales.
No comprobar solo que una llamada no lanza excepcion: contrastar bytes, estado,
valor esperado y ausencia de efectos indebidos. En AES comprobar autenticacion,
cabecera AAD, sal/nonce nuevos, contraseña generada y recuperacion exacta.
En JavaFX usar JUnit para dominio; pruebas de controles en JavaFX Application
Thread o herramienta UI apropiada, separadas de las unitarias. En Android probar
ViewModels/repositorios con dependencias inyectadas; UI/ContentResolver en
instrumentacion o entorno de prueba explicito. En Unity usar asmdef de tests,
NUnit/EditMode y UnityTest/PlayMode con semilla controlada, restaurando escenas.
No promediar cobertura entre plataformas ni excluir logica propia para alcanzar 80%.
