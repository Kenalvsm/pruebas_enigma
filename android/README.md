# Android - pendiente proyecto real
Android Studio Quali 4 2026.1.4; Kotlin; Gradle Wrapper y SDK compatible con AGP.
Tareas raiz: testDebugUnitTest y jacocoTestReport (agrega modulo app).
Activar cobertura JVM/Kotlin. XML requerido:
app/build/reports/jacoco/jacocoTestReport/jacocoTestReport.xml.
Configurar clases propias y fuentes, documentar exclusiones generadas.
Instrumentacion y pruebas de importacion/UI aparte en emulador/dispositivo.
No confundir unitarias JVM con funcionales. El hook bloquea sin tests/informe.

## CI/CD desde Windows, Debian o Ubuntu

Preparar el host y los hooks siguiendo el [README principal](../README.md#inicio-por-integrante).
Desde la raiz del repositorio, la comprobacion local de Android se ejecuta con:

```powershell
# Windows
py -3 scripts/quality.py test --platform android
```

```bash
# Debian o Ubuntu, despues de importar el proyecto real y su wrapper
chmod +x android/gradlew
python scripts/quality.py test --platform android
```

Instalar un JDK compatible con el AGP del proyecto y el Android SDK en cada
host. Configurar `JAVA_HOME` y la ruta local del SDK mediante Android Studio
o `local.properties` (no versionar rutas personales). En Linux se usa `gradlew`;
en Windows, `gradlew.bat`. Las ramas terminadas en `/android` seleccionan esta
suite en los hooks. La instrumentacion sigue necesitando emulador o dispositivo.

El [workflow local con Docker y act](../README.md#cicd-local-con-docker-y-act-windows-debian-y-ubuntu)
se lanza desde cualquiera de esos hosts con
`act push -j python-quality --artifact-server-path .artifacts/act`.
El workflow actual solo comprueba Python; no ejecuta el SDK ni el emulador Android.
