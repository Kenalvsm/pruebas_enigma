import hashlib

import pytest

from enigma import aes


@pytest.mark.acceptance
@pytest.mark.parametrize("size", [1024 * 1024, 20 * 1024 * 1024])
def test_required_file_sizes(tmp_path, size):
    # Patrón binario reproducible que incluye los 256 valores posibles.
    data = bytes(range(256)) * (size // 256)
    source = tmp_path / "entrada.bin"
    source.write_bytes(data)
    result = aes.encrypt_file(source)
    recovered = tmp_path / "recuperado.bin"
    aes.decrypt_file(result.path, recovered, result.password)
    actual = recovered.read_bytes()
    assert source.read_bytes() == data
    assert result.path.stat().st_size == size + 53
    assert len(actual) == size
    assert hashlib.sha256(actual).digest() == hashlib.sha256(data).digest()
    assert actual == data
