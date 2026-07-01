from pathlib import Path
import shutil
import re

SCH_FILE = Path("Oszillatoren.kicad_sch")
FIELD_NAMES = {"Description", "Beschreibung", "ki_description"}

if not SCH_FILE.exists():
    raise FileNotFoundError(f"Datei nicht gefunden: {SCH_FILE}")

backup = SCH_FILE.with_suffix(".kicad_sch.bak")
shutil.copy2(SCH_FILE, backup)

lines = SCH_FILE.read_text(encoding="utf-8").splitlines(keepends=True)

new_lines = []
i = 0
found = 0
changed = 0
already_hidden = 0

while i < len(lines):
    line = lines[i]
    stripped = line.strip()

    if stripped.startswith("(property "):
        m = re.match(r'\(property\s+"([^"]+)"\s+', stripped)

        if m and m.group(1) in FIELD_NAMES:
            found += 1
            block = [line]
            depth = line.count("(") - line.count(")")
            i += 1

            while i < len(lines) and depth > 0:
                block.append(lines[i])
                depth += lines[i].count("(") - lines[i].count(")")
                i += 1

            block_text = "".join(block)

            if "(hide yes)" in block_text:
                already_hidden += 1
            elif "(hide no)" in block_text:
                block_text = block_text.replace("(hide no)", "(hide yes)")
                changed += 1
            else:
                # hide yes nach do_not_autoplace einfügen
                block_text = re.sub(
                    r"(\n\s*\(do_not_autoplace\s+(?:yes|no)\))",
                    r"\1\n\t\t\t\t(hide yes)",
                    block_text,
                    count=1
                )
                changed += 1

            new_lines.append(block_text)
            continue

    new_lines.append(line)
    i += 1

SCH_FILE.write_text("".join(new_lines), encoding="utf-8")

print(f"Gefundene Beschreibungsfelder: {found}")
print(f"Neu versteckt/geändert: {changed}")
print(f"Bereits versteckt: {already_hidden}")
print(f"Backup erstellt: {backup}")