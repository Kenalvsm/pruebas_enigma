# JavaFX - pendiente proyecto real
Java 25 LTS y JavaFX, mismo codigo Windows/Linux; fatjar con nativos por sistema.
Importar proyecto Gradle con wrapper y JUnit; aplicar plugin jacoco.
Tareas obligatorias: test y jacocoTestReport (XML enabled), codigo propio completo.
Informe: build/reports/jacoco/test/jacocoTestReport.xml.
No excluir logica criptografica ni archivos para inflar cobertura.
El hook falla hasta existir proyecto, pruebas y >=80% lineas.

## CI/CD desde Windows, Debian o Ubuntu

Preparar el host y los hooks siguiendo el [README principal](../README.md#inicio-por-integrante).
Desde la raiz del repositorio, la comprobacion local de JavaFX se ejecuta con:

```powershell
# Windows
py -3 scripts/quality.py test --platform javafx
```

```bash
# Debian o Ubuntu, despues de importar el proyecto real y su wrapper
chmod +x javafx/gradlew
python scripts/quality.py test --platform javafx
```

Instalar el JDK requerido y configurar `JAVA_HOME` y PATH en cada host. En Linux
se usa `gradlew`; en Windows, `gradlew.bat`. Trabajar en ramas terminadas en
`/javafx` para que los hooks seleccionen esta suite.

El [workflow local con Docker y act](../README.md#cicd-local-con-docker-y-act-windows-debian-y-ubuntu)
se lanza desde cualquiera de esos hosts con `act push -j python-quality`.
El workflow actual solo comprueba Python; las pruebas JavaFX son locales.
