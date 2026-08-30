/*
    Coded by ArTic/JhoPro

    Choose a font and include it here, then you can use
    the 'Print' function to print strings on the screen.

    Example: #include "fontX.h"
*/

int cursorX = 0;
int cursorY = 0;

void DrawChar(unsigned char* bitmap, unsigned int color)
{
    for (int y = 0; y < HFONT; y++)
    {
        for (int x = 0; x < WFONT; x++)
        {
            int byte = x / 8;
            int bit  = 7 - (x % 8);

            if (bitmap[y * BYTES_PER_ROW + byte] & (1 << bit))
            {
                SetPixel(cursorX + x, cursorY + y, color);
            }
        }
    }

    cursorX += WFONT;

    if (cursorX >= WSCREEN)
    {
        cursorX = 0;
        cursorY += HFONT;
    }
}

void Print(const char* str, unsigned int color)
{
    for (int i = 0; str[i] != '\0'; i++)
    {
        if (str[i] == '\n')
        {
            if (shellNOGUI)
            {
                cursorX = 0;
                cursorY += HFONT;
            }

            continue;
        }

        if (str[i] == '\b')
        {
            if (cursorX > 0)
            {
                cursorX -= 16;
                DrawChar(isoFont + 0 * GLYPH_SIZE, 0);

                cursorX -= 8;

                continue;
            }
        }

        if (str[i] == '\f')
        {
            DrawChar(isoFont + 0xDB * GLYPH_SIZE, color);

            continue;
        }

        DrawChar(isoFont + (unsigned char)str[i] * GLYPH_SIZE, color);
    }
}

void MapFont()
{
    SetCursorX(0x00);

    for (BYTE index = 0; index < 0xFF; index++)
    {
        PrintOut((BYTE)index, 0xFFFFFFFF);

        PrintOut(' ', 0x00);

        if ((index & 0x0F) == 0x0F)
        {
            PrintOut('\n', 0xFFFFFFFF);
        }
    }
}