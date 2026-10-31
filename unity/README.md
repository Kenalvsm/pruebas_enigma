# Unity - pendiente proyecto real
Unity 6.3 (6000.3.x), Test Framework, Code Coverage.
Definir UNITY_EDITOR con ruta completa; crear EditMode/PlayMode tests con asmdef.
Configurar assemblyFilters de cobertura para codigo propio, excluyendo tests y
paquetes del motor; OpenCover con sequence points. No excluir logica de juego.
Los hooks ejecutan ambos modos y exigen >=80% de puntos medibles propios.
Las evidencias de Unity son locales, no hay job Unity en GitHub.
Validar ejecutable Windows 11 x64 manualmente y conservar capturas/logs.
