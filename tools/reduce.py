#!/usr/bin/env python3

import sys
import re


# ============================================================
# CONFIGURAÇÃO
# ============================================================

SRC_WIDTH = 16
SRC_HEIGHT = 32

DST_WIDTH = 8
DST_HEIGHT = 16

# Controla a espessura da fonte.
#
# 1 = mais grossa
# 2 = intermediária
# 3 = Light
# 4 = muito Light
#
THRESHOLD = 3


# ============================================================
# HEX -> MATRIZ DE PIXELS
# ============================================================

def hex_to_bitmap(hex_rows, width):

    bitmap = []

    bytes_per_row = (width + 7) // 8

    for value in hex_rows:

        value = value.strip()

        # Garante o número correto de caracteres hexadecimais
        value = value.zfill(bytes_per_row * 2)

        bits = []

        for byte in range(bytes_per_row):

            b = int(
                value[byte * 2:byte * 2 + 2],
                16
            )

            for bit in range(8):

                bits.append(
                    (b >> (7 - bit)) & 1
                )

        bitmap.append(bits[:width])

    return bitmap


# ============================================================
# REDUZ 16x32 -> 8x16
# ============================================================

def reduce_bitmap(rows):

    """
    Reduz uma matriz 16x32 para 8x16.

    Cada pixel da fonte nova representa um bloco 2x2
    da fonte original.

    THRESHOLD:

        1 = mais grosso
        2 = normal
        3 = Light
        4 = muito Light
    """

    result = []

    for y in range(0, SRC_HEIGHT, 2):

        out_row = []

        for x in range(0, SRC_WIDTH, 2):

            count = 0

            # Analisa o bloco 2x2
            for dy in range(2):

                for dx in range(2):

                    if rows[y + dy][x + dx]:
                        count += 1

            # Decide se o pixel será ligado
            if count >= THRESHOLD:
                out_row.append(1)
            else:
                out_row.append(0)

        result.append(out_row)

    return result


# ============================================================
# MATRIZ DE PIXELS -> HEX
# ============================================================

def bitmap_to_hex(bitmap, width):

    result = []

    bytes_per_row = (width + 7) // 8

    for row in bitmap:

        value = 0

        for x in range(width):

            value <<= 1
            value |= row[x]

        # Completa até múltiplo de 8 bits
        value <<= (
            bytes_per_row * 8 - width
        )

        result.append(
            f"{value:0{bytes_per_row * 2}X}"
        )

    return result


# ============================================================
# PROCESSA BDF
# ============================================================

def process_bdf(input_file, output_file):

    with open(
        input_file,
        "r",
        encoding="ascii"
    ) as f:

        lines = f.readlines()

    output = []

    i = 0

    while i < len(lines):

        line = lines[i]

        # ====================================================
        # INÍCIO DO GLYPH
        # ====================================================

        if line.startswith("STARTCHAR"):

            glyph = [line]

            i += 1

            bitmap_lines = []

            in_bitmap = False

            # ------------------------------------------------
            # Lê o glyph inteiro
            # ------------------------------------------------

            while i < len(lines):

                current = lines[i]

                # Encontrou BITMAP
                if current.startswith("BITMAP"):

                    in_bitmap = True

                    glyph.append(current)

                    i += 1

                    continue

                # Estamos lendo o bitmap
                if in_bitmap:

                    # Fim do glyph
                    if current.startswith("ENDCHAR"):
                        break

                    # Linha hexadecimal
                    if re.fullmatch(
                        r"[0-9A-Fa-f]+\s*",
                        current
                    ):

                        bitmap_lines.append(
                            current.strip()
                        )

                    else:

                        glyph.append(current)

                else:

                    glyph.append(current)

                i += 1

            # =================================================
            # REDUZ O BITMAP
            # =================================================

            if len(bitmap_lines) == SRC_HEIGHT:

                bitmap = hex_to_bitmap(
                    bitmap_lines,
                    SRC_WIDTH
                )

                reduced = reduce_bitmap(
                    bitmap
                )

                new_bitmap = bitmap_to_hex(
                    reduced,
                    DST_WIDTH
                )

                # =============================================
                # ALTERA BBX
                # =============================================

                new_glyph = []

                for gline in glyph:

                    if gline.startswith("BBX"):

                        parts = gline.split()

                        if len(parts) >= 3:

                            parts[1] = str(
                                DST_WIDTH
                            )

                            parts[2] = str(
                                DST_HEIGHT
                            )

                        gline = (
                            " ".join(parts)
                            + "\n"
                        )

                    new_glyph.append(
                        gline
                    )

                # =============================================
                # NOVO BITMAP
                # =============================================

                new_glyph.extend(
                    line + "\n"
                    for line in new_bitmap
                )

                new_glyph.append(
                    "ENDCHAR\n"
                )

                output.extend(
                    new_glyph
                )

            else:

                # Não era um glyph 16x32.
                # Mantém o glyph original.

                output.extend(glyph)

                if (
                    i < len(lines)
                    and lines[i].startswith("ENDCHAR")
                ):

                    output.append(
                        lines[i]
                    )

            i += 1

            continue

        # ====================================================
        # FONTBOUNDINGBOX
        # ====================================================

        if line.startswith(
            "FONTBOUNDINGBOX"
        ):

            parts = line.split()

            if len(parts) >= 3:

                parts[1] = str(
                    DST_WIDTH
                )

                parts[2] = str(
                    DST_HEIGHT
                )

            output.append(
                " ".join(parts)
                + "\n"
            )

            i += 1

            continue

        # ====================================================
        # OUTRAS LINHAS
        # ====================================================

        output.append(line)

        i += 1

    # ========================================================
    # SALVA O NOVO BDF
    # ========================================================

    with open(
        output_file,
        "w",
        encoding="ascii"
    ) as f:

        f.writelines(output)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    if len(sys.argv) != 3:

        print()
        print(
            "Uso:"
        )

        print(
            "  python reduce.py entrada.bdf saida.bdf"
        )

        print()

        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    process_bdf(
        input_file,
        output_file
    )

    print()
    print(
        "Fonte reduzida com sucesso!"
    )

    print(
        f"Entrada : {input_file}"
    )

    print(
        f"Saída   : {output_file}"
    )

    print(
        f"Tamanho : "
        f"{SRC_WIDTH}x{SRC_HEIGHT} "
        f"-> "
        f"{DST_WIDTH}x{DST_HEIGHT}"
    )

    print(
        f"Threshold: {THRESHOLD}"
    )

    print()