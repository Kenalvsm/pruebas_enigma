# Enigma - Reto 02
Monorrepo preparado a partir de ejemplos y contrato tecnico v1.1 (prioritario).
Estructura: python/, javafx/, android/, unity/, tests/, docs/.
Los PDF y ejemplos se conservan. El instalador del agente y sus credenciales se
excluyen de Git. No ejecutar git add -f sobre esos archivos.

## Inicio por integrante
Ejecutar los comandos desde la raiz del repositorio. Instalar Git, Python para
herramientas y uv. En Windows (PowerShell):

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install-hooks.ps1
uv sync --locked --project python
py -3 scripts/test_quality.py
```

En Debian o Ubuntu como maquina host (Bash):

```bash
sudo apt update
sudo apt install -y git curl ca-certificates python3 python-is-python3
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uv --version
python --version
sh scripts/install-hooks.sh
uv sync --locked --project python
python scripts/test_quality.py
git config --local --get core.hooksPath
```

El ultimo comando debe mostrar `.githooks`. `python-is-python3` proporciona
el comando `python` que usan los hooks; un alias interactivo no basta.
uv obtiene la version del interprete requerida por el proyecto, sin sustituir
el Python del sistema. El instalador de hooks activa tambien sus permisos de
ejecucion. El instalador de uv configura el PATH para futuras sesiones; el
`export` permite usarlo en la terminal actual. Ver [instalacion de uv](https://docs.astral.sh/uv/getting-started/installation/).

Cada persona configura su propia identidad con `git config user.name` y
`git config user.email`; no suplantar autores. Los hooks son locales a cada
clon y no necesitan Docker.

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
no acredita requisitos criptograficos. Para reproducir ese workflow con Docker,
seguir la seccion siguiente.

## CI/CD local con Docker y act: Windows, Debian y Ubuntu

El sistema host es la maquina donde se lanzan Docker y act. El job actual de
`.github/workflows/ci.yml` usa `ubuntu-latest`; `.actrc` lo asocia a
`catthehacker/ubuntu:act-latest`. Por tanto, desde los tres hosts se ejecuta el
mismo job Linux en un contenedor. Usar Debian como host no crea un job Debian.

### Windows (PowerShell)

Instalar Docker Desktop, iniciarlo en modo contenedores Linux e instalar act
segun su [guia oficial](https://nektosact.com/installation/index.html).
Con ambos comandos disponibles en PATH, desde la raiz:

```powershell
docker info
act --version
act -l
act push -j python-quality
# Repetir con la imagen ya descargada:
act push -j python-quality --pull=false
```

### Debian y Ubuntu (Bash)

Preparar Git, curl y uv como en «Inicio por integrante». Instalar Docker Engine
con el repositorio apt oficial que corresponda al host:

- [Docker Engine en Debian](https://docs.docker.com/engine/install/debian/).
- [Docker Engine en Ubuntu](https://docs.docker.com/engine/install/ubuntu/).

Seguir en esa guia la configuracion del repositorio y la instalacion de los
paquetes; no usar el repositorio de Ubuntu en Debian ni mezclar instalaciones
de Docker. Con Docker Engine instalado en un host con systemd:

```bash
sudo systemctl enable --now docker
sudo groupadd --force docker
sudo usermod -aG docker "$USER"
```

Cerrar sesion y volver a entrar para aplicar el grupo. El grupo `docker` concede
privilegios equivalentes a root; ver la [configuracion oficial de permisos](https://docs.docker.com/engine/install/linux-postinstall/).
Instalar act para el usuario, siguiendo su [instalador oficial](https://nektosact.com/installation/index.html):

```bash
mkdir -p "$HOME/.local/bin"
curl --proto '=https' --tlsv1.2 -sSf https://raw.githubusercontent.com/nektos/act/master/install.sh | bash -s -- -b "$HOME/.local/bin"
export PATH="$HOME/.local/bin:$PATH"
docker info
docker run --rm hello-world
act --version
```

Desde la raiz del repositorio, ya con acceso a Docker sin sudo:

```bash
act -l
act push -j python-quality
# Repetir con la imagen ya descargada:
act push -j python-quality --pull=false
```

La primera ejecucion descarga la imagen, las acciones y las dependencias;
requiere acceso a Internet. `--pull=false` evita forzar la descarga de la imagen,
pero no garantiza una ejecucion sin red. No ejecutar `sudo act`.

### Resultado, informes y ejecucion remota

Esperar `Job succeeded` y codigo de salida 0. Las comprobaciones requieren
formato, lint, tests y cobertura >=80%; un fallo real bloquea el job.
Los informes de ejecucion directa quedan en `.artifacts/python/` (JUnit,
cobertura XML y HTML). Con act, los artefactos subidos se conservan en
`.artifacts/act/`, segun `.actrc`. No versionar esos directorios.

Para ejecutar el mismo control directamente en el host, sin Docker, tras
instalar los requisitos anteriores:

```powershell
# Windows
py -3 scripts/quality.py ci
```

```bash
# Debian o Ubuntu
python scripts/quality.py ci
```

Los commits y pushes ejecutan los hooks segun el sufijo de la rama; para probar
el hook de commit manualmente, usar `git hook run pre-commit` desde una rama de
trabajo valida. El CI remoto se inicia al hacer push o abrir un PR y tambien
admite `workflow_dispatch` desde la pestaña Actions. act ejecuta localmente
sin publicar commits. El workflow actual realiza comprobaciones y publica
informes; no contiene una etapa de despliegue (CD).

Si `docker info` falla, revisar el servicio y los permisos antes de lanzar act.
Si falta `python`, revisar `python-is-python3`; si falta `uv` o `act`, revisar
PATH. Los resultados historicos estan en [validacion de infraestructura](docs/VALIDACION_INFRA.md);
estas instrucciones no acreditan una ejecucion nueva desde Debian o Ubuntu.

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
`py -3 scripts/test_quality.py` en Windows o `python scripts/test_quality.py`
en Debian/Ubuntu. Plantillas JaCoCo: archivos *.gradle.example;
adaptarlos al importar proyectos reales, sin crear compilaciones ficticias.

Guia: [CI/CD y hooks](docs/GUIA_CI_CD.md), [lectura HTML](docs/GUIA_CI_CD.html).
Javadoc: [autoria y generacion](javafx/JAVADOC.md).
