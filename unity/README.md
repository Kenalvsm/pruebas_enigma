# Unity - pendiente proyecto real
Unity 6.3 (6000.3.x), Test Framework, Code Coverage.
Definir UNITY_EDITOR con ruta completa; crear EditMode/PlayMode tests con asmdef.
Configurar assemblyFilters de cobertura para codigo propio, excluyendo tests y
paquetes del motor; OpenCover con sequence points. No excluir logica de juego.
Los hooks ejecutan ambos modos y exigen >=80% de puntos medibles propios.
Las evidencias de Unity son locales, no hay job Unity en GitHub.
Validar ejecutable Windows 11 x64 manualmente y conservar capturas/logs.

## CI/CD desde Windows, Debian o Ubuntu

La preparacion de hooks y la ejecucion del workflow con Docker y act estan en
el [README principal](../README.md#cicd-local-con-docker-y-act-windows-debian-y-ubuntu).
Desde la raiz, ejecutar
`act push -j python-quality --artifact-server-path .artifacts/act`
para lanzar el mismo job Linux con cualquiera de esos hosts. Este workflow
no instala ni ejecuta Unity.

Para las pruebas locales de Unity, ademas del proyecto real, hace falta un
Editor 6.3 instalado, con licencia y compatible con el sistema host. Definir
`UNITY_EDITOR` con la ruta real del ejecutable antes de lanzar la suite:

```powershell
# Windows; sustituir por la version instalada
$env:UNITY_EDITOR = 'C:\Program Files\Unity\Hub\Editor\6000.3.x\Editor\Unity.exe'
py -3 scripts/quality.py test --platform unity
```

```bash
# Host Linux con Editor compatible; sustituir por la ruta instalada
export UNITY_EDITOR="$HOME/Unity/Hub/Editor/6000.3.x/Editor/Unity"
python scripts/quality.py test --platform unity
```

Las ramas terminadas en `/unity` seleccionan esta suite en los hooks. Poder
ejecutar act en Debian no acredita compatibilidad del Editor Unity con Debian;
comprobar los requisitos del Editor antes de preparar pruebas nativas.
Los informes y logs locales se guardan en `.artifacts/unity/`.
