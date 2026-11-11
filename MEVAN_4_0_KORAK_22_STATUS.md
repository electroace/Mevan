# MEVAN 4.0 — Korak 22: Sigurnosna kopija i provjera vraćanja

- Dodan `backup_restore.py` koji pravi konzistentan SQLite backup preko SQLite backup API-ja (uključujući WAL promjene).
- Svaka kopija prolazi `PRAGMA integrity_check`.
- Vraćanje se vrši isključivo na novu putanju; postojeća baza se nikad ne prepisuje.
- Dodana tri automatska testa: WAL backup i restore, odbijanje neispravne baze i nedostajuće baze.
- **Nije implementiran automatizirani dnevni raspored, šifrovanje niti offsite pohrana.** To se mora podesiti na hostingu.
- GitHub/Render nisu mijenjani; nema pristupa produkcijskim podacima.
