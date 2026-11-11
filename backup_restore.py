"""Offline, consistent SQLite backup and integrity verification for a single MEVAN instance.

Never copy a live SQLite database file with shutil.copyfile: use SQLite's backup API.
The restore command refuses to overwrite an existing destination.
"""
import argparse
import sqlite3
from pathlib import Path


def integrity_check(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"Baza ne postoji: {path}")
    connection = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    try:
        result = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if result != 'ok':
            raise ValueError(f"SQLite integrity_check: {result}")
    finally:
        connection.close()


def backup(source: Path, destination: Path) -> None:
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve():
        raise ValueError('Izvor i odredište ne smiju biti isti')
    if destination.exists():
        raise FileExistsError('Odredište već postoji; ne prepisujem postojeći backup')
    integrity_check(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    src = sqlite3.connect(f"file:{source.resolve()}?mode=ro", uri=True)
    try:
        with sqlite3.connect(destination) as dst:
            src.backup(dst)
        integrity_check(destination)
    except BaseException:
        destination.unlink(missing_ok=True)
        raise
    finally:
        src.close()


def restore(source: Path, destination: Path) -> None:
    """Restore only to a NEW path; stop the app before switching DB paths."""
    backup(source, destination)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MEVAN SQLite backup / restore (bez prepisivanja)')
    parser.add_argument('command', choices=['backup', 'restore', 'verify'])
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path, nargs='?')
    args = parser.parse_args()
    if args.command == 'verify':
        integrity_check(args.source)
    elif args.destination is None:
        parser.error('Za backup/restore je potrebna odredišna putanja')
    elif args.command == 'backup':
        backup(args.source, args.destination)
    else:
        restore(args.source, args.destination)
    print('OK: provjera završena')
