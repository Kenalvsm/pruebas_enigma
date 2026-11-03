# Aplicación Python Enigma

CLI autónoma para Python 3.14 con menú interactivo, Vigenère y AES/R2AE.
No necesita Java, Android, Unity ni un servicio central.

## Instalación

Compatible con Windows, Ubuntu y Debian usando Python 3.14. Los siguientes
comandos se ejecutan desde la raíz del repositorio. Con uv instalado, la misma
instalación y ejecución sirve en los tres sistemas:

```sh
uv sync --locked --project python
uv run --locked --project python enigma
```

uv puede descargar Python 3.14 si la distribución no lo proporciona. Para pruebas:

```sh
uv sync --locked --extra dev --project python
uv run --locked --extra dev --project python python scripts/quality.py ci
```

También se admite la instalación manual siguiente.

Windows:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r python/requirements-runtime.lock
.\.venv\Scripts\python.exe -m pip install --no-deps --no-build-isolation -e ./python
.\.venv\Scripts\python.exe -m enigma
```

Linux, con Python 3.14 y su módulo venv disponibles:

```bash
python3.14 -m venv .venv
.venv/bin/python -m pip install -r python/requirements-runtime.lock
.venv/bin/python -m pip install --no-deps --no-build-isolation -e ./python
.venv/bin/python -m enigma
```

El paquete instala también el comando `enigma` en la carpeta de ejecutables del
entorno. Desde `python/`, `python main.py` es un lanzador alternativo cuando se
utiliza ese mismo entorno. `python -m enigma --help` y `--version` muestran ayuda
y versión.

`pyproject.toml` centraliza dependencias directas, configuración y metadatos.
Los dos archivos `requirements-*.lock` fijan también dependencias transitivas y
herramientas de construcción. Para instalar desarrollo, sustituye el archivo de
runtime por `python/requirements-dev.lock`. La instalación editable usa el backend
ya fijado en ese archivo para evitar resolver dependencias durante la construcción.

## Uso del menú

Navega por las opciones con las flechas **arriba/abajo** y confirma con **Enter**.
La opción activa se marca con `>` y un acento de color. No necesitas escribir
números, tampoco al elegir el origen del texto o cómo guardar el resultado.
**Esc** vuelve desde los submenús y sale desde el menú principal; también puedes
usar **Inicio/Fin** o **k/j** para navegar. El selector requiere una terminal
interactiva con control de cursor, como Windows Terminal o la consola que abre
`iniciar_enigma.bat`. Los textos y contraseñas se siguen escribiendo normalmente.

1. **Cifrar Vigenère**: elegir texto de consola o archivo `.txt` UTF-8 en el explorador, introducir
   clave de 1 a 64 letras A-Z y mostrar, guardar o mostrar y guardar el resultado.
2. **Descifrar Vigenère**: mismo flujo, usando la clave original.
3. **Cifrar AES**: seleccionar cualquier archivo en el explorador y un destino en
   «Guardar como», que propone `<original>.enc`. Al finalizar se muestra la contraseña
   aleatoria de 16 caracteres.
4. **Descifrar AES**: seleccionar el contenedor R2AE, destino e introducir la
   contraseña original. Se propone `nombre.recuperado.ext` para conservar el original.
0. **Salir**. Ctrl+C o fin de entrada cancelan y cierran de forma controlada.

Las rutas se eligen con los diálogos nativos de abrir y guardar archivos; no hace
falta escribirlas. «Cancelar» cierra el selector y devuelve al menú sin ejecutar
la operación. Las rutas con espacios están admitidas. Las claves se
introducen con entrada oculta en una terminal interactiva. Un error de archivo,
validación o autenticación permite volver al menú.

Con Tkinter y una sesión de escritorio se abren diálogos nativos en los tres
sistemas. Si falta Tkinter o no se puede abrir una ventana (por ejemplo, SSH),
se pide la ruta en la terminal. Admite espacios, comillas alrededor de la ruta y
`~` para la carpeta personal. Una entrada vacía cancela; al guardar se añade la
extensión propuesta si el nombre no tiene ninguna. Se siguen rechazando destinos
existentes. El menú requiere una terminal interactiva con soporte ANSI.

Tkinter es opcional y no se instala con pip. Para usar ventanas, activa Tcl/Tk
en el instalador de Python en Windows. En Ubuntu/Debian instala el módulo Tk de
la misma versión e instalación de Python que ejecuta Enigma; `python3-tk` del
sistema no añade Tk a otro intérprete descargado por uv. Comprueba la instalación
con `uv run --project python python -m tkinter` desde una sesión de escritorio.

La terminal usa magenta `#C90068`, azul `#0003C9`, verde `#00C962` y amarillo
`#C9C600` en el título, los números del menú y los indicadores de estado. Estos
acentos tienen texto blanco sobre magenta/azul y negro sobre verde/amarillo;
el resto del contenido conserva el color habitual de la terminal. Los mensajes
incluyen etiquetas como «OK», «Aviso» y «Error», por lo que no dependen del color.
La salida redirigida se mantiene sin códigos de color. Para desactivar los colores
también en pantalla, define la variable de entorno `NO_COLOR=1`.

El menú incluye una cabecera decorativa, un marco, grupos separados para Vigenère
y AES y títulos para cada operación. En terminales estrechas se omite el marco;
si la codificación no admite sus bordes, se usan caracteres ASCII.

Ejemplo Vigenère: `ATTACKATDAWN` con clave `LEMON` produce `LXFOPVEFRNHR`.
Solo A-Z/a-z se transforma y avanza la clave. Se respeta la caja. Espacios,
dígitos, signos, ñ, vocales con tilde y otros caracteres Unicode se conservan.
Los archivos de texto conservan saltos CRLF/LF y BOM UTF-8, si existe.
Vigenère tiene finalidad educativa; para proteger archivos utiliza AES.

En AES se genera siempre una contraseña nueva mediante `secrets`; no se ofrece
la opción de elegirla al cifrar. Guárdala al verla: no se escribe en archivos,
configuraciones o logs. Si se pierde, no existe una función de recuperación.
La consola muestra la contraseña tras el cifrado: evita capturar esa sesión en
logs o compartir su historial. Una contraseña incorrecta o un archivo alterado
no produce un archivo recuperado publicado.

## Protección de archivos y límites

- Los orígenes se abren solo en lectura; nunca se reemplazan destinos existentes,
  ni siquiera si otro proceso los crea al terminar la operación.
- Se escribe un temporal aleatorio `.part` en la carpeta de destino; se sincroniza,
  se cierra y se publica mediante enlace duro sin reemplazo. Se intenta limpiar el
  temporal tanto al completar como al fallar o cancelar.
- El descifrado puede escribir contenido aún no autenticado **solo en el temporal**.
  No se publica hasta verificar GCM. `mkstemp` restringe permisos a su propietario
  en POSIX; en Windows se heredan las ACL de la carpeta. Usa una carpeta privada.
- El sistema de archivos debe permitir enlaces duros en el volumen de destino
  (por ejemplo, NTFS o ext4). FAT/exFAT y algunos volúmenes de red no los admiten:
  la operación fallará de forma segura. No se sustituye por una copia que pudiera
  dejar un destino parcial.
- AES usa bloques de 1 MiB; no carga el archivo completo en memoria. Se necesitan
  espacio para el resultado y permisos de lectura/escritura. Vigenère sí carga el
  texto completo. No edites los archivos de entrada mientras se procesan.
- El límite teórico de cada mensaje GCM es `2**36 - 32` bytes. La validación local
  incluida comprueba hasta 20 MiB; no acredita ese máximo teórico.
- Si el proceso muere abruptamente, se apaga el equipo o el sistema impide borrar
  archivos, pueden quedar temporales `.enigma-*.part`. Comprueba que no haya una
  operación activa antes de borrarlos. No se promete borrado físico seguro del disco.

El contenedor tiene 37 bytes de cabecera autenticada y 16 de etiqueta. Se cifra
el contenido completo y se usa `.enc`, también para imágenes (`foto.png.enc`).
Consulta `../docs/R2AE.md` para los offsets y vectores compartibles con los otros
clientes.

## Calidad y pruebas

Instala primero `python/requirements-dev.lock` en el entorno y el paquete editable.
Desde `python/`, con el entorno activado, ejecuta:

```bash
python -m ruff format --check .
python -m ruff check .
python -m pytest -m "not acceptance" --cov=enigma --cov-report=term-missing --cov-report=xml:reports/coverage.xml --cov-report=html:reports/htmlcov --cov-fail-under=80 --junitxml=reports/unit-tests.xml
python -m pytest -m acceptance --junitxml=reports/acceptance-tests.xml
python scripts/verify_acceptance.py
python -m build --no-isolation
```

En PowerShell, sin activar el entorno, utiliza `..\.venv\Scripts\python.exe` en
lugar de `python`. Los informes se guardan en `python/reports/`; el script de
aceptación escribe `acceptance.json` con tamaños, tiempos, SHA-256 y comparación
exacta para 0 B, 1 B, 1 MiB y 20 MiB. No registra contraseñas.

Se mide cobertura de líneas y ramas del paquete completo, incluido el menú. No
hay exclusiones de módulos propias para elevar el porcentaje; los lanzadores
pueden aparecer sin cobertura en la ejecución de pruebas en proceso. Las pruebas
de aceptación grandes se ejecutan aparte de la medición unitaria.

Las pruebas de fallos de escritura, permisos y disco lleno inyectan excepciones
controladas; no llenan realmente el disco ni cambian permisos del usuario. Las
pruebas de rutas existentes y de colisión al publicar usan archivos reales.

## Hooks y workflow preparado

Los hooks nativos `.githooks/pre-commit` y `.githooks/pre-push` llaman a
`scripts/quality.py` y ejecutan la suite de la plataforma indicada por la rama.
Para Python incluyen formato, lint, aceptación y cobertura mínima del 80 %.

Para preparar Windows, Debian o Ubuntu como **máquina host** del CI local,
consulta el [README principal](../README.md#cicd-local-con-docker-y-act-windows-debian-y-ubuntu).
Desde la raíz del repositorio, con Docker y act instalados, el comando es el
mismo en los tres hosts:

```sh
act push -j python-quality --artifact-server-path .artifacts/act
```

`.github/workflows/ci.yml` tiene un único job en `ubuntu-latest`, con el check
`Python - lint, tests y cobertura >=80%`. act lo ejecuta en la imagen Linux
definida en `.actrc`, independientemente del sistema host; no hay una matriz
de runners Windows/Debian/Ubuntu. Los artefactos de act se conservan en
`.artifacts/act/` gracias a la opción explícita de servidor local; la ejecución
directa de `scripts/quality.py ci` escribe en
`.artifacts/python/`. El workflow publica informes y no despliega la aplicación.

Las pruebas unitarias de diálogos simulan Tkinter;
comprueban también la selección de rutas sin Tk y sin escritorio. Las ventanas
reales requieren una comprobación manual en una sesión gráfica.

## Estructura

```text
python/
  pyproject.toml
  requirements-runtime.lock
  requirements-dev.lock
  main.py
  src/enigma/           # menú, Vigenère, AES/R2AE, archivos, errores
  tests/               # pruebas unitarias, funcionales y aceptación
    fixtures/          # vectores públicos de interoperabilidad
  scripts/             # comprobación reproducible de tamaños
```

