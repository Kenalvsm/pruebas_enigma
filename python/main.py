"""Lanzador alternativo tras instalar el paquete con pip install -e ./python."""

from enigma.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
