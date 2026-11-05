# Prioridad: contrato tecnico v1.1 sobre pliego
Contrato en estado propuesta pendiente de aprobacion: no se afirma aprobacion docente.
3.5/P-10 y 6.3: CI/CD exclusivamente Python. Todo push de una rama que acaba en
python y todo PR abierto desde ella ejecuta el check Python, que es el unico
requerido del monorrepo. Las demas ramas se ignoran: no disparan CI ni hooks.
Los hooks locales aplican la misma regla de rama y no eligen plataforma.
6.4: >=80% del codigo propio de Python. JavaFX, Android y Unity quedan fuera de
alcance: sus toolchains nos estan dando demasiados problemas y no se exigen ni
se simulan sus informes.
6.6: Python 3.14; formato, lint, tests, XML/HTML y artefactos; uv.lock versionado.
4.7: tres commits reales por persona, dos ramas usadas ademas de main, PR con
revision ajena. La configuracion no fabrica estas evidencias ni autores.
4.13: hooks por clon; GitHub debe aplicar la proteccion remota (README).

## Fuera de alcance en esta entrega
P-06/P-12 (intercambio Python-JavaFX-Android), P-07 (fatjar JavaFX),
P-08 (Android) y P-09 (Unity) siguen escritos en el contrato, pero no se
validan aqui. Se retomaran solo si esos entornos dejan de bloquear al equipo.

## Aceptacion pendiente de implementar y medir
P-01 Vigenere A-Z, case, signos, espacios, ñ/tildes sin avance, clave 1-64 letras.
P-02/P-03 AES: 0B, 1B, 1MiB, >=20MiB; comparar bytes, tamanos y SHA-256.
P-04/P-05/P-13 clave incorrecta, alteracion, errores escritura/permisos,
no sobrescritura, sin salida parcial, limpiar .part y preservar original.
R2AE v1: cabecera 37B AAD; magic R2AE 4B, version 1B, iteraciones 4B
big-endian, sal 16B, nonce 12B; ciphertext y tag 16B; sobrecarga 53B.
AES-256-GCM, PBKDF2-HMAC-SHA256 200000; password CSPRNG alfanumerica 16,
no elegida al cifrar ni almacenada/logueada. Usar vectores PUBLICOS de prueba.
P-10 cobertura >=80% de codigo propio Python, informes de la aplicacion.
P-11 contrasenas seguras. Manual instalacion/uso, decisiones, limites,
mediciones y evidencias reales; act + Docker al menos una vez.

No existe despliegue a servidor central: aplicaciones autonomas. Publicar
fatjars/APK/juego queda fuera de esta entrega; este scaffold no los fabrica.
La calculadora copiada de ejemplos prueba la infraestructura, NO AES/Vigenere
ni cumplimiento funcional. Sustituirla al implementar la aplicacion real.
