# Prioridad: contrato tecnico v1.1 sobre pliego
Contrato en estado propuesta pendiente de aprobacion: no se afirma aprobacion docente.
3.5/P-10 y 6.3: CI/CD exclusivamente Python. En todos los push y PR se ejecuta
Python, incluso desde ramas de otros clientes: es el check requerido del monorrepo.
Los hooks locales seleccionan la plataforma por el ultimo segmento de la rama.
6.4: >=80% por aplicacion, nunca promedio. JavaFX/Android/Unity solo local.
6.6: Python 3.14; formato, lint, tests, XML/HTML y artefactos; uv.lock versionado.
4.7: tres commits reales por persona, dos ramas usadas ademas de main, PR con
revision ajena. La configuracion no fabrica estas evidencias ni autores.
4.13: hooks por clon; GitHub debe aplicar la proteccion remota (README).

## Aceptacion pendiente de implementar y medir
P-01 Vigenere A-Z, case, signos, espacios, ñ/tildes sin avance, clave 1-64 letras.
P-02/P-03 AES: 0B, 1B, 1MiB, >=20MiB; comparar bytes, tamanos y SHA-256.
P-04/P-05/P-13 clave incorrecta, alteracion, errores escritura/permisos,
no sobrescritura, sin salida parcial, limpiar .part y preservar original.
P-06/P-12 intercambio R2AE Python/JavaFX/Android y contraseñas cruzadas.
R2AE v1: cabecera 37B AAD; magic R2AE 4B, version 1B, iteraciones 4B
big-endian, sal 16B, nonce 12B; ciphertext y tag 16B; sobrecarga 53B.
AES-256-GCM, PBKDF2-HMAC-SHA256 200000; password CSPRNG alfanumerica 16,
no elegida al cifrar ni almacenada/logueada. Usar vectores PUBLICOS de prueba.
P-07 Java 25 LTS, fatjar Windows 11 x64/Linux; Alerts, vistas limitadas.
P-08 Android solo descifra PNG AES y txt Cesar, compartir/Bluetooth/selector,
avisos nativos sin cierre; aclaracion .png.enc pendiente segun 3.1.1.
P-09 Unity 6.3 Windows x64: tutorial, 5 rondas, 3 vidas, 4 fallos por vida,
estados, fisicas 2D, normalizacion conserva Ñ, vacios no penalizan.
P-10 cobertura >=80% de codigo propio, informes por aplicacion.
P-11 contraseñas seguras. Manual instalacion/uso, decisiones, limites,
mediciones y evidencias reales; act + Docker al menos una vez.

No existe despliegue a servidor central: aplicaciones autonomas. Publicar
fatjars/APK/juego tras validacion local y PR; este scaffold no los fabrica.
La calculadora copiada de ejemplos prueba la infraestructura, NO AES/Vigenere
ni cumplimiento funcional. Sustituirla al implementar la aplicacion real.
