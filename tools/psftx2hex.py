#!/usr/bin/env python3

import sys
import re

if len(sys.argv) != 3:
    print("Usage:")
    print("python psftx2hex.py font.psftx font.h")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

width = None
height = None
glyphs = []

with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

# ------------------------------------------------------------
# Descobre o tamanho da fonte
# ------------------------------------------------------------

for line in lines:

    # Procura algo como:
    # 8x16
    # 8 x 16

    m = re.search(r'\b(\d+)\s*x\s*(\d+)\b', line)

    if m:
        width = int(m.group(1))
        height = int(m.group(2))
        break

if width is None or height is None:
    print("Failed: Not able to find font's size.")
    sys.exit(1)

# ------------------------------------------------------------
# Lê os GLYPH
# ------------------------------------------------------------

i = 0

while i < len(lines):

    line = lines[i].strip()

    if line.startswith("GLYPH"):

        bitmap = []

        i += 1

        while i < len(lines):

            line = lines[i].strip()

            if line == "ENDGLYPH":
                break

            # Uma linha de bitmap contém somente . e X
            if line and set(line).issubset({'.', 'X'}):

                bitmap.append(line)

            i += 1

        # Só adiciona glyphs completos
        if len(bitmap) == height:

            glyphs.append(bitmap)

        else:

            print(
                f"Warning: glyph {len(glyphs)} has "
                f"{len(bitmap)} lines, expected {height}"
            )

    i += 1

# ------------------------------------------------------------
# Conversão
# ------------------------------------------------------------

bytes_per_row = (width + 7) // 8

with open(output_file, "w", encoding="utf-8") as out:

    out.write(f"#define WFONT {width}\n")
    out.write(f"#define HFONT {height}\n\n")

    out.write("unsigned char isoFont[] = {\n")

    count = 0

    for glyph in glyphs:

        for row in glyph:

            for byte_index in range(bytes_per_row):

                value = 0

                for bit in range(8):

                    x = byte_index * 8 + bit

                    if x >= width:
                        break

                    if row[x] == 'X':
                        value |= 1 << (7 - bit)

                out.write(f"0x{value:02X},")

                count += 1

                if count % 16 == 0:
                    out.write("")
                else:
                    out.write("")

        out.write("\n")

    out.write("};\n")

print("Converted Successfully!")
print(f"Glyphs : {len(glyphs)}")
print(f"Size   : {width}x{height}")
print(f"Bytes  : {count}")
