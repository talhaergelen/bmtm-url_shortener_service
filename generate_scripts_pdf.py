#!/usr/bin/env python3
"""Markdown dosyalarını güzel HTML'e çevirir, sonra macOS'un yerleşik aracıyla PDF yapar."""
import markdown
import subprocess
import os

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

@page {
    size: A4;
    margin: 2cm 2.5cm;
}

@media print {
    body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    h2 { page-break-after: avoid; }
    pre { page-break-inside: avoid; }
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 14px;
    line-height: 1.8;
    color: #1e293b;
    background: #fff;
    max-width: 750px;
    margin: 0 auto;
    padding: 40px;
}

h1 {
    font-size: 28px;
    font-weight: 800;
    color: #0f172a;
    border-bottom: 3px solid #3b82f6;
    padding-bottom: 10px;
    margin-top: 36px;
    margin-bottom: 16px;
}

h2 {
    font-size: 19px;
    font-weight: 700;
    color: #1e40af;
    margin-top: 32px;
    margin-bottom: 14px;
    padding: 10px 14px;
    background: #eff6ff;
    border-left: 5px solid #3b82f6;
    border-radius: 0 8px 8px 0;
}

h3 {
    font-size: 15px;
    font-weight: 600;
    color: #475569;
    margin-top: 20px;
    margin-bottom: 10px;
}

p {
    margin-bottom: 12px;
    text-align: justify;
}

strong {
    color: #0f172a;
    background: #fef3c7;
    padding: 2px 5px;
    border-radius: 3px;
}

blockquote {
    background: #f0fdf4;
    border-left: 4px solid #22c55e;
    padding: 14px 18px;
    margin: 18px 0;
    border-radius: 0 8px 8px 0;
    font-size: 13px;
    color: #166534;
}

code {
    font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
    background: #f1f5f9;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 12px;
    color: #dc2626;
}

pre {
    background: #1e293b;
    color: #e2e8f0;
    padding: 16px 20px;
    border-radius: 10px;
    font-size: 13px;
    line-height: 1.6;
    overflow-x: auto;
    margin: 14px 0;
}

pre code {
    background: none;
    color: #e2e8f0;
    padding: 0;
}

hr {
    border: none;
    border-top: 2px solid #e2e8f0;
    margin: 28px 0;
}

ul, ol {
    margin-bottom: 14px;
    padding-left: 26px;
}

li {
    margin-bottom: 6px;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 18px 0;
    font-size: 13px;
}

th {
    background: #1e40af;
    color: white;
    padding: 10px 14px;
    text-align: left;
    font-weight: 600;
}

td {
    padding: 10px 14px;
    border-bottom: 1px solid #e2e8f0;
}

tr:nth-child(even) td {
    background: #f8fafc;
}

.doc-header {
    text-align: center;
    padding: 28px 24px;
    margin-bottom: 28px;
    background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%);
    color: white;
    border-radius: 14px;
}

.doc-header h1 {
    color: white;
    border: none;
    font-size: 30px;
    margin: 0 0 8px 0;
    padding: 0;
}

.doc-header p {
    color: #c7d2fe;
    margin: 0;
    text-align: center;
    font-size: 15px;
}
"""


def md_to_html_file(md_path, html_path, title, subtitle):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    html_body = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])

    header = f"""
    <div class="doc-header">
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """

    full_html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>{CSS}</style>
</head>
<body>
{header}
{html_body}
</body>
</html>"""

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"✅ HTML oluşturuldu: {html_path}")
    return html_path


if __name__ == "__main__":
    base = "docs"

    h1 = md_to_html_file(
        f"{base}/SUNUM_KONUSMA_METNI.md",
        f"{base}/SUNUM_KONUSMA_METNI.html",
        "📋 Sunum Konuşma Metni",
        "URL Shortener Service — 10 Dakikalık Slayt Sunumu | Talha Ergelen & Osman Çingöz"
    )

    h2 = md_to_html_file(
        f"{base}/DEMO_KONUSMA_METNI.md",
        f"{base}/DEMO_KONUSMA_METNI.html",
        "🎬 Canlı Demo Konuşma Metni",
        "URL Shortener Service — 7 Dakikalık Canlı Demo | Talha Ergelen & Osman Çingöz"
    )

    # macOS'un yerleşik aracıyla HTML → PDF
    for html_file in [h1, h2]:
        pdf_file = html_file.replace('.html', '.pdf')
        try:
            subprocess.run([
                '/usr/sbin/cupsfilter', html_file
            ], capture_output=True)
        except Exception:
            pass

    print()
    print("=" * 50)
    print("PDF'leri oluşturmak için tarayıcıda aç ve")
    print("Cmd+P → PDF olarak kaydet yap. Ya da:")
    print()
    print(f"  open {h1}")
    print(f"  open {h2}")
    print()
    print("Tarayıcıda açıldıktan sonra Cmd+P ile PDF yap!")
    print("=" * 50)
