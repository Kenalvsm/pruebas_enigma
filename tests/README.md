# Integracion
Implementar vectores publicos R2AE y pruebas cruzadas P-06/P-12, tamanos
P-03 y recuperacion byte a byte/SHA-256. No hay pruebas de aceptacion aun.
Los informes deben enlazar commit, plataforma, comando, fecha y resultado real.

## Comprobaciones de infraestructura en el host

Preparar dependencias y hooks siguiendo el [README principal](../README.md#inicio-por-integrante).
Desde la raiz del repositorio:

```powershell
# Windows
py -3 scripts/test_quality.py
```

```bash
# Debian o Ubuntu
python scripts/test_quality.py
```

Estas comprobaciones verifican la infraestructura de hooks y CI; no sustituyen
las pruebas de aceptacion ni generan cobertura de las aplicaciones.

Para reproducir el workflow en Docker desde los tres sistemas host, seguir
las [instrucciones de act](../README.md#cicd-local-con-docker-y-act-windows-debian-y-ubuntu)
y ejecutar `act push -j python-quality` desde la raiz. El job solo comprueba
Python; no ejecuta las pruebas cruzadas de esta carpeta. Los artefactos de act
quedan en `.artifacts/act/`.
