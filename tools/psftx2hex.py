#!/usr/bin/env python3

import re
import sys

if len(sys.argv) != 3:
    print("Usage:")
    print("python psftx2hex.py font.psftx font.c")
    exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

glyphs = []
width = None
height = None

with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
    lines = [line.rstrip() for line in f]

i = 0

while i < len(lines):

    line = lines[i].strip()

    if line.startswith("# Size:"):
        m = re.search(r'(\d+)\s*x\s*(\d+)', line)
        if m:
            width = int(m.group(1))
            height = int(m.group(2))

    if line.startswith("GLYPH"):

        bitmap = []

        i += 1

        while i < len(lines):

            l = lines[i].rstrip()

            if l.strip() == "ENDGLYPH":
                break

            if "U+" in l or l.strip() == "":
                i += 1
                continue

            row = l.strip()

            if set(row).issubset({'.', 'X'}):

                if width is None:
                    width = len(row)

                bitmap.append(row)

            i += 1

        glyphs.append(bitmap)

    i += 1

if width is None or height is None:
    print("Error: can't find font's size.")
    exit(1)

bytes_per_row = (width + 7) // 8

with open(output_file, "w") as out:
    out.write(f"#define WFONT {width}\n")
    out.write(f"#define HFONT {height}\n")
    out.write("unsigned char font[] = {\n\n")

    for g, bitmap in enumerate(glyphs):
        for row in bitmap:
            for b in range(bytes_per_row):
                
                value = 0

                for bit in range(8):
                    
                    x = b * 8 + bit
                    
                    if x >= width:
                        break

                    if row[x] == 'X':
                        value |= 1 << (7 - bit)

                out.write(f"0x{value:02X}, ")
            out.write("\n")
        out.write("\n")
    out.write("};\n")

print("Converted Successfully!")
print(f"Glyphs : {len(glyphs)}")
print(f"Size: {width}x{height}")
