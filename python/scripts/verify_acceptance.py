"""Evidencia local reproducible de tamaño, integridad, tiempo y memoria Python."""

import hashlib
import json
import platform
import tempfile
import tracemalloc
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

from enigma import __version__, aes


def verify() -> dict:
    measurements = []
    for size in (0, 1, 1024 * 1024, 20 * 1024 * 1024):
        with tempfile.TemporaryDirectory(prefix="enigma-acceptance-") as directory:
            source = Path(directory) / "original.bin"
            block = bytes(range(256)) * 4096
            with source.open("wb") as stream:
                remaining = size
                while remaining:
                    portion = block[: min(remaining, len(block))]
                    stream.write(portion)
                    remaining -= len(portion)
            recovered = Path(directory) / "recuperado.bin"
            tracemalloc.start()
            start = perf_counter()
            result = aes.encrypt_file(source)
            encryption_seconds = perf_counter() - start
            start = perf_counter()
            aes.decrypt_file(result.path, recovered, result.password)
            decryption_seconds = perf_counter() - start
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            with source.open("rb") as stream:
                original_hash = hashlib.file_digest(stream, "sha256").hexdigest()
            with recovered.open("rb") as stream:
                recovered_hash = hashlib.file_digest(stream, "sha256").hexdigest()
            identical = True
            with source.open("rb") as a, recovered.open("rb") as b:
                while True:
                    left, right = a.read(aes.CHUNK_SIZE), b.read(aes.CHUNK_SIZE)
                    if left != right:
                        identical = False
                        break
                    if not left:
                        break
            valid = (
                identical
                and original_hash == recovered_hash
                and source.stat().st_size == recovered.stat().st_size == size
                and result.path.stat().st_size == size + aes.OVERHEAD
            )
            measurements.append(
                {
                    "original_bytes": size,
                    "container_bytes": result.path.stat().st_size,
                    "recovered_bytes": recovered.stat().st_size,
                    "original_sha256": original_hash,
                    "recovered_sha256": recovered_hash,
                    "byte_for_byte_equal": identical,
                    "encrypt_seconds": round(encryption_seconds, 6),
                    "decrypt_seconds": round(decryption_seconds, 6),
                    "python_peak_allocated_bytes": peak,
                    "passed": valid,
                }
            )
            if not valid:
                raise RuntimeError(f"La comprobación de {size} bytes no ha superado los criterios.")
    return {
        "executed_at_utc": datetime.now(UTC).isoformat(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "app_version": __version__,
        "memory_note": "tracemalloc mide asignaciones Python; no es RSS ni toda la memoria nativa.",
        "measurements": measurements,
    }


if __name__ == "__main__":
    report = verify()
    target = Path(__file__).resolve().parents[1] / "reports" / "acceptance.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"4/4 tamaños recuperados byte a byte; informe: {target}")
