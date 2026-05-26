#!/usr/bin/env python3
"""
PDF generator for final-report.md and slides.md using fpdf2 with Unicode support
"""
import re
import unicodedata
import urllib.request
import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos

FONT_REGULAR = "/Library/Fonts/Arial Unicode.ttf"
FONT_BOLD    = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

def download_font():
    """Arial Unicode sistem fontunu kullan."""
    return FONT_REGULAR, FONT_BOLD



def clean_text(text):
    """Emoji'leri temizle, markdown işaretlerini kaldır."""
    # Markdown temizle
    text = text.replace("**", "").replace("`", "")
    text = text.replace("✅", "[OK]").replace("⚠️", "[!!]").replace("🔴", "[X]")
    text = text.replace("🟡", "[?]").replace("🌟", "[*]").replace("🚨", "[!]")
    text = text.replace("📋", "").replace("📊", "").replace("🔍", "")
    text = text.replace("→", "->").replace("≥", ">=").replace("≤", "<=")
    # Kalan emoji'leri sil
    cleaned = ""
    for ch in text:
        cp = ord(ch)
        if cp > 0x2FFF and not (0x4E00 <= cp <= 0x9FFF):  # CJK hariç emoji sil
            if unicodedata.category(ch) in ("So", "Sm"):
                continue
        cleaned += ch
    return cleaned.strip()


class PDF(FPDF):
    def __init__(self, title, font_regular, font_bold):
        super().__init__()
        self.doc_title = title
        self.add_font("DejaVu", "", font_regular, uni=True)
        self.add_font("DejaVu", "B", font_bold, uni=True)
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(20, 25, 20)
        self.add_page()

    def header(self):
        self.set_font("DejaVu", "", 7)
        self.set_text_color(160, 160, 160)
        self.cell(0, 6, self.doc_title[:80], align="L")
        self.ln(2)
        self.set_draw_color(200, 200, 200)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(3)
        self.set_text_color(0, 0, 0)

    def footer(self):
        self.set_y(-14)
        self.set_font("DejaVu", "", 8)
        self.set_text_color(160, 160, 160)
        self.cell(0, 8, f"Sayfa {self.page_no()}", align="C")


def render_markdown_to_pdf(md_path, pdf_path, title, font_r, font_b):
    pdf = PDF(title, font_r, font_b)

    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    in_code_block = False
    code_lines = []

    for raw_line in lines:
        line = raw_line.rstrip("\n")

        # Kod bloğu başlangıç/bitiş
        if line.startswith("```"):
            if in_code_block:
                # Kod bloğunu kapat - son 3 satırı göster
                in_code_block = False
                pdf.set_font("DejaVu", "", 8)
                pdf.set_fill_color(240, 240, 240)
                for cl in code_lines[:6]:
                    cl = cl.rstrip()[:80]
                    if cl:
                        pdf.multi_cell(0, 5.5, "  " + cl, fill=True,
                                       new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                if len(code_lines) > 6:
                    pdf.set_font("DejaVu", "", 7)
                    pdf.set_text_color(120, 120, 120)
                    pdf.cell(0, 5, f"  ... ({len(code_lines)-6} satır daha)",
                             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.set_text_color(0, 0, 0)
                code_lines = []
                pdf.ln(2)
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        # Yatay çizgi
        if line.strip() == "---":
            pdf.set_draw_color(180, 180, 200)
            pdf.line(20, pdf.get_y() + 2, 190, pdf.get_y() + 2)
            pdf.ln(5)
            continue

        # H1
        if re.match(r"^# [^#]", line):
            text = clean_text(line[2:])
            pdf.ln(2)
            pdf.set_font("DejaVu", "B", 17)
            pdf.set_text_color(30, 60, 130)
            pdf.multi_cell(0, 10, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_draw_color(30, 60, 130)
            pdf.line(20, pdf.get_y(), 190, pdf.get_y())
            pdf.ln(4)
            pdf.set_text_color(0, 0, 0)
            continue

        # H2
        if re.match(r"^## [^#]", line):
            text = clean_text(line[3:])
            pdf.ln(4)
            pdf.set_font("DejaVu", "B", 13)
            pdf.set_text_color(20, 80, 160)
            pdf.multi_cell(0, 9, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_draw_color(150, 180, 230)
            pdf.line(20, pdf.get_y(), 190, pdf.get_y())
            pdf.ln(3)
            pdf.set_text_color(0, 0, 0)
            continue

        # H3
        if re.match(r"^### [^#]", line):
            text = clean_text(line[4:])
            pdf.ln(3)
            pdf.set_font("DejaVu", "B", 11)
            pdf.set_text_color(50, 50, 80)
            pdf.multi_cell(0, 8, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(0, 0, 0)
            continue

        # Bullet list
        if re.match(r"^[-*]\s", line):
            text = clean_text(line[2:])
            if text:
                pdf.set_font("DejaVu", "", 10)
                x = pdf.get_x()
                y = pdf.get_y()
                pdf.set_xy(20, y)
                pdf.cell(6, 7, "-", new_x=XPos.RIGHT, new_y=YPos.TOP)
                pdf.set_xy(26, y)
                pdf.multi_cell(164, 7, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            continue

        # Numbered list
        num_match = re.match(r"^(\d+)\.\s+(.+)", line)
        if num_match:
            num, text = num_match.group(1), clean_text(num_match.group(2))
            pdf.set_font("DejaVu", "", 10)
            y = pdf.get_y()
            pdf.set_xy(20, y)
            pdf.cell(8, 7, f"{num}.", new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.set_xy(28, y)
            pdf.multi_cell(162, 7, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            continue

        # Table separator
        if re.match(r"^\|[-| :]+\|", line):
            continue

        # Table row
        if line.startswith("|"):
            cells = [clean_text(c) for c in line.strip("|").split("|")]
            cells = [c[:35] for c in cells]
            n = len(cells)
            if n == 0:
                continue
            col_w = 170 // n
            is_header = any(len(c) > 2 and c == c.upper() for c in cells)
            for i, c in enumerate(cells):
                if is_header:
                    pdf.set_font("DejaVu", "B", 8)
                    pdf.set_fill_color(210, 225, 255)
                    pdf.cell(col_w, 6, c, border=1, fill=True,
                             new_x=XPos.RIGHT, new_y=YPos.TOP)
                else:
                    pdf.set_font("DejaVu", "", 8)
                    pdf.set_fill_color(245, 245, 250)
                    fill = (pdf.page_no() % 2 == 0)
                    pdf.cell(col_w, 6, c, border=1,
                             new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.ln()
            continue

        # Boş satır
        if not line.strip():
            pdf.ln(3)
            continue

        # Normal metin / bold
        text = clean_text(line.strip())
        if not text:
            continue

        # İtalik/bold metadata satırı (*, **)
        if text.startswith("*") or text.startswith("_"):
            text = text.lstrip("*_").rstrip("*_")
            pdf.set_font("DejaVu", "", 9)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(0, 7, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(0, 0, 0)
        else:
            pdf.set_font("DejaVu", "", 10)
            pdf.multi_cell(0, 7, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.output(pdf_path)
    size_kb = os.path.getsize(pdf_path) // 1024
    print(f"✅ {pdf_path}  ({size_kb} KB, {pdf.page_no()} sayfa)")


if __name__ == "__main__":
    font_r, font_b = download_font()
    
    base = "/Users/osmancingoz/Desktop/bulut/bmtm-url_shortener_service"
    
    render_markdown_to_pdf(
        f"{base}/docs/final-report.md",
        f"{base}/docs/final-report.pdf",
        "BMTM Donem Projesi - URL Shortener - Final Rapor",
        font_r, font_b
    )
    
    render_markdown_to_pdf(
        f"{base}/docs/slides.md",
        f"{base}/docs/slides.pdf",
        "BMTM Donem Projesi - URL Shortener - Sunum",
        font_r, font_b
    )
    
    print("\nTum PDF'ler olusturuldu!")
