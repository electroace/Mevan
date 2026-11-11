import sqlite3
import tempfile
import unittest
from pathlib import Path
from backup_restore import backup, restore, integrity_check

class BackupRestoreTests(unittest.TestCase):
    def test_live_wal_backup_restore_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source, saved, restored = (root / n for n in ('live.db', 'snapshot.db', 'restored.db'))
            connection = sqlite3.connect(source)
            try:
                connection.execute('PRAGMA journal_mode=WAL')
                connection.execute('CREATE TABLE entries(id INTEGER PRIMARY KEY, value TEXT)')
                connection.execute('INSERT INTO entries(value) VALUES (?)', ('METALPRO demo',))
                connection.commit()
                backup(source, saved)
                restore(saved, restored)
                with sqlite3.connect(restored) as check:
                    self.assertEqual(check.execute('SELECT value FROM entries').fetchone()[0], 'METALPRO demo')
                with self.assertRaises(FileExistsError):
                    backup(source, saved)
            finally:
                connection.close()

    def test_corrupted_source_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source = root / 'invalid.db'
            source.write_bytes(b'not a sqlite database')
            with self.assertRaises(sqlite3.DatabaseError):
                integrity_check(source)
            self.assertFalse((root / 'backup.db').exists())

    def test_missing_source_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                backup(Path(d) / 'missing.db', Path(d) / 'backup.db')

if __name__ == '__main__':
    unittest.main()
