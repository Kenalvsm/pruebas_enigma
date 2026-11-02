"""Errores funcionales que el menú puede comunicar sin mostrar un traceback."""


class EnigmaError(Exception):
    """Error controlado de entrada, formato o autenticación."""


class ValidationError(EnigmaError):
    """Entrada no admitida por el contrato."""


class OperationCancelled(EnigmaError):
    """El usuario ha cancelado un selector de archivos."""


class ContainerError(EnigmaError):
    """Contenedor R2AE incompleto o con parámetros no compatibles."""


class AuthenticationError(EnigmaError):
    """La contraseña o la autenticidad del contenedor no son válidas."""
