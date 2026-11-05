# Guia CI/CD - Enigma
Repositorio: https://github.com/Kenalvsm/pruebas_enigma.git
Raiz local: C:\Users\WinterOS\vento\ejemplos

## Alcance: solo Python
CI/CD, act, pre-commit y pre-push validan unicamente Python. JavaFX, Android y
Unity quedan fuera porque nos estan dando muchos problemas: Gradle/AGP no
reproducen el entorno, los informes JaCoCo dependen de tareas que hay que
rehacer por proyecto, los emuladores no son estables y Unity en batchmode
necesita una instalacion concreta en cada maquina. Mantener esos gates solo
bloqueaba commits sin aportar senal util. Sus directorios siguen en el
monorrepo como referencia del contrato, sin comandos ni evidencias asociadas.

## Preparacion y uso
```powershell
git config core.hooksPath .githooks
py -3 -m uv sync --locked --project python
py -3 scripts/test_quality.py
git switch -c feature/cambio/python
git hook run pre-commit
```
Ramas de trabajo: <tarea>/<descripcion>/python, por ejemplo
feature/cambio/python o chore/infra/python. main y develop son las ramas
comunes protegidas.

## Ramas y gates
| Rama | pre-commit / pre-push | CI de GitHub | act |
|---|---|---|---|
| Acaba en python | Ejecuta la suite Python completa | Ejecuta python-quality | Ejecuta python-quality |
| Cualquier otra | Avisa y termina sin ejecutar nada | No se dispara u omite el job | Se omite |

Las ramas protegidas no ejecutan gates pero siguen bloqueadas: no se permite
commit directo en main/develop ni push hacia ellas desde otra rama.

## Diferencias entre hooks
Ambos hooks son scripts locales de Git, instalados mediante `core.hooksPath=.githooks`. No son el workflow de GitHub ni requieren Docker. Ambos exigen tests e informes reales de Python y ejecutan instalacion bloqueada, formato, lint y cobertura >=80%.

| Comprobacion | pre-commit | pre-push |
|---|---|---|
| Momento | Antes de crear el commit local | Antes de enviar referencias al remoto |
| Si falla | No se crea el commit | No se envia ese push; los commits locales permanecen |
| main/develop como rama actual | Bloqueado | Bloqueado |
| Destino remoto main/develop desde otra rama | No interviene: no conoce el destino | Bloqueado, incluso mediante refspec |
| Que ejecuta en rama python | Suite Python completa | La misma suite, repetida antes de enviar |
| Que ejecuta en otra rama | Nada, solo el aviso de rama ignorada | Nada, pero el push protegido sigue bloqueado |
| Refs enviadas | No las comprueba | Solo permite la rama actual, sin tags, borrados ni otras ramas |

En esta implementacion pre-commit NO ejecuta exclusivamente tests rapidos ni pre-push anade cobertura por primera vez: ambos llaman a la misma suite completa. Los tests se ejecutan sobre el arbol de trabajo actual, no sobre una copia aislada del indice. Revisar `git diff` y `git diff --cached` antes del commit.

El framework llamado pre-commit es opcional; tener `.pre-commit-config.yaml` no sustituye la instalacion de los hooks nativos. No mezclar instalaciones sin revisar `core.hooksPath`. No usar `--no-verify`. Las reglas del servidor GitHub deben exigir PR, revision ajena, el check Python y restringir force-push/borrado en main/develop: los hooks se pueden desactivar localmente.

## Docker y act: comandos validados
Con Docker Desktop iniciado en contenedores Linux:
```powershell
winget install nektos.act
```

```powershell
$actDir = "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\nektos.act_Microsoft.Winget.Source_8wekyb3d8bbwe"
$env:Path += ";$actDir"
docker info
act --version
act -l
act push
# Con imagen ya descargada, evitar forzar descarga:
act push --pull=false
```
`.actrc` fija `-j python-quality`, por lo que act ejecuta solo el job de Python
sin importar el evento. Esperar Job succeeded. El numero de tests depende del
codigo: 17 corresponde a la calculadora de ejemplo y al cifrado Vigenere
(python/src/cifrado.py) con sus pruebas. .actrc conserva informes en
.artifacts/act. El modo ci no necesita Git dentro del contenedor ni un remoto
para correr act.

## Python y CI remoto
Python 3.14, uv.lock versionado, Ruff formato/lint y pytest con pytest-cov.
El workflow se dispara con push a ramas acaban en python y con PR hacia
main/develop abiertos desde esas ramas; cualquier otra rama se ignora.
Umbral 80%; JUnit XML y cobertura XML/HTML se generan en .artifacts/python y se
publican como artefactos.

## Configurar el remoto y flujo completo
```powershell
git remote -v
# Solo si origin todavia no existe:
git remote add origin https://github.com/Kenalvsm/pruebas_enigma.git
git switch -c feature/documentacion/python
git diff
git add README.md docs scripts .github .githooks .actrc .pre-commit-config.yaml
git diff --cached
git commit -m "docs: limita la infraestructura a Python"
git push -u origin feature/documentacion/python
```
Si origin existe y apunta a otra URL, comprobarlo antes de cambiarlo. Abrir PR a
develop y solicitar revision. El push ejecuta hooks locales; GitHub ejecuta CI
cuando recibe los commits. act simula el workflow en Docker sin publicar codigo.

## Como disenar los tests
Mantener la logica de dominio separada de pantallas y archivos para probarla con
entradas deterministas, un resultado esperado y una sola causa de fallo.
Usar directorios temporales y fixtures publicos, sin secretos ni rutas
personales. No comprobar solo que una llamada no lanza excepcion: contrastar
bytes, estado, valor esperado y ausencia de efectos indebidos. En AES comprobar
autenticacion, cabecera AAD, sal/nonce nuevos, contrasena generada y
recuperacion exacta.
No promediar cobertura entre modulos ni excluir logica propia para alcanzar 80%.

## Javadoc: autoria y generacion
Autor solicitado: **Kenneth Alvarez**. Usar `@author Kenneth Alvarez` en la
cabecera de cada clase propia que corresponda cuando exista codigo Java.
No cambiar autores de bibliotecas externas ni identidades de commits Git.
La carpeta javafx no contiene clases Java y no se valida en esta etapa.
