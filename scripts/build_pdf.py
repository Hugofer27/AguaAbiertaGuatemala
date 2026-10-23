from __future__ import annotations

import json
import shutil
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "public" / "data" / "catalog.json"
OUTPUT = ROOT / "catalogo_fuentes_agua_guatemala.pdf"
PAGE = landscape(A4)

INK = colors.HexColor("#0E2D36")
WATER = colors.HexColor("#0A706C")
HIGHLIGHT = colors.HexColor("#34B7A8")
PAPER = colors.HexColor("#EDF5F3")
PAPER_DEPTH = colors.HexColor("#DFECEA")
RULE = colors.HexColor("#91ADAE")
CARMINE = colors.HexColor("#B34238")
SECONDARY = colors.HexColor("#45656B")


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("Atlas", str(ROOT / "public" / "fonts" / "UbuntuCondensed.ttf")))
    pdfmetrics.registerFont(TTFont("AtlasText", str(ROOT / "public" / "fonts" / "Ubuntu-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("AtlasTextBold", str(ROOT / "public" / "fonts" / "Ubuntu-Bold.ttf")))


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="Atlas",
            fontSize=29,
            leading=28,
            textColor=colors.white,
            spaceAfter=8,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["BodyText"],
            fontName="AtlasText",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#D7E4E4"),
        ),
        "label": ParagraphStyle(
            "Label",
            parent=base["BodyText"],
            fontName="Atlas",
            fontSize=8,
            leading=9,
            textColor=SECONDARY,
            spaceAfter=2,
        ),
        "value": ParagraphStyle(
            "Value",
            parent=base["BodyText"],
            fontName="AtlasText",
            fontSize=8.3,
            leading=10.3,
            textColor=INK,
        ),
        "value_bold": ParagraphStyle(
            "ValueBold",
            parent=base["BodyText"],
            fontName="AtlasTextBold",
            fontSize=9.2,
            leading=11.2,
            textColor=INK,
        ),
        "link": ParagraphStyle(
            "Link",
            parent=base["BodyText"],
            fontName="AtlasTextBold",
            fontSize=8,
            leading=10,
            textColor=WATER,
        ),
        "footer": ParagraphStyle(
            "Footer",
            parent=base["BodyText"],
            fontName="Atlas",
            fontSize=8,
            leading=9,
            textColor=colors.white,
            alignment=TA_RIGHT,
        ),
    }


def page_canvas(canvas, doc) -> None:
    width, height = PAGE
    canvas.saveState()
    canvas.setFillColor(INK)
    canvas.rect(0, height - 18 * mm, width, 18 * mm, stroke=0, fill=1)
    canvas.setStrokeColor(HIGHLIGHT)
    canvas.setLineWidth(1.2)
    canvas.line(12 * mm, height - 18 * mm, width - 12 * mm, height - 18 * mm)
    canvas.setFont("Atlas", 10)
    canvas.setFillColor(colors.white)
    canvas.drawString(12 * mm, height - 11.5 * mm, "AGUA ABIERTA GUATEMALA / CATÁLOGO MAESTRO")
    canvas.setFont("Atlas", 8)
    canvas.drawRightString(width - 12 * mm, 8 * mm, f"FOLIO {doc.page}")
    canvas.setStrokeColor(RULE)
    canvas.line(12 * mm, 12 * mm, width - 12 * mm, 12 * mm)
    canvas.restoreState()


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(str(text or "")), style)


def link(label: str, href: str, style: ParagraphStyle) -> Paragraph:
    if not href:
        return p("No disponible", style)
    safe_href = escape(href, {'"': "&quot;"})
    return Paragraph(f'<link href="{safe_href}" color="#0A706C"><u>{escape(label)}</u></link>', style)


def resource_block(item: dict, s: dict[str, ParagraphStyle]) -> Table:
    title = Table(
        [[p(f'{item["number"]:02d}', s["label"]), p(item["title"], s["value_bold"]), p(item["accessState"], s["label"])]],
        colWidths=[13 * mm, 198 * mm, 44 * mm],
    )
    title.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PAPER_DEPTH),
                ("TEXTCOLOR", (0, 0), (0, 0), WATER),
                ("BOX", (0, 0), (-1, -1), 0.75, INK),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, RULE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    left = [
        [p("NOMBRE DEL ARCHIVO", s["label"]), p(item["fileName"], s["value"])],
        [p("INSTITUCIÓN", s["label"]), p(item["institution"], s["value"])],
        [p("TEMA", s["label"]), p(item["topic"], s["value"])],
        [p("TERRITORIO / CUENCA", s["label"]), p(item["territory"], s["value"])],
        [p("PERIODO", s["label"]), p(item["period"], s["value"])],
    ]
    right = [
        [p("FORMATO / TAMAÑO", s["label"]), p(f'{item["format"]} · {item["size"]}', s["value"])],
        [p("RESUMEN", s["label"]), p(item["summary"], s["value"])],
        [p("LICENCIA / USO", s["label"]), p(item["license"], s["value"])],
        [p("ARCHIVO LOCAL", s["label"]), link("Abrir copia verificada", item["localPath"].removeprefix("../"), s["link"])],
        [p("PROCEDENCIA", s["label"]), link("Abrir fuente original", item["sourceUrl"], s["link"])],
    ]
    body = Table(
        [[Table(left, colWidths=[34 * mm, 82 * mm]), Table(right, colWidths=[34 * mm, 105 * mm])]],
        colWidths=[116 * mm, 139 * mm],
    )
    body.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.75, INK),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, RULE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    for table in body._cellvalues[0]:
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LINEBELOW", (0, 0), (-1, -2), 0.25, RULE),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 3.5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
                ]
            )
        )
    sha = Table(
        [[p("SHA-256", s["label"]), p(item["sha256"], s["value"])]],
        colWidths=[24 * mm, 231 * mm],
    )
    sha.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PAPER),
                ("BOX", (0, 0), (-1, -1), 0.75, INK),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    block = Table([[title], [body], [sha]], colWidths=[255 * mm])
    block.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return block


def main() -> None:
    register_fonts()
    s = styles()
    catalog = json.loads(DATA.read_text(encoding="utf-8"))
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=PAGE,
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=24 * mm,
        bottomMargin=14 * mm,
        title="Catálogo maestro de fuentes de agua de Guatemala",
        author="Agua Abierta Guatemala",
        subject="Índice verificable de 75 archivos públicos de agua",
    )
    story = [
        Spacer(1, 4 * mm),
        Table(
            [[Paragraph("CATÁLOGO MAESTRO<br/>DE FUENTES DE AGUA<br/>DE GUATEMALA", s["title"]), Paragraph("75 ARCHIVOS VERIFICADOS", s["title"])]],
            colWidths=[170 * mm, 85 * mm],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), INK),
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 9 * mm),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 9 * mm),
                    ("TOPPADDING", (0, 0), (-1, -1), 12 * mm),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 12 * mm),
                    ("LINEBEFORE", (1, 0), (1, 0), 1.5, HIGHLIGHT),
                ]
            ),
        ),
        Spacer(1, 8 * mm),
        Paragraph(
            "Índice de los archivos descargados y conservados para la primera versión del portal. Cada ficha distingue el archivo local de su página de procedencia y mantiene la condición de uso disponible en el inventario. Los enlaces locales son relativos a la carpeta del proyecto; algunos lectores PDF los bloquean por seguridad.",
            ParagraphStyle("Intro", parent=s["value"], fontSize=12, leading=17, textColor=INK),
        ),
        Spacer(1, 5 * mm),
        Table(
            [[p("FECHA DE CORTE", s["label"]), p("21 de octubre de 2026", s["value_bold"]), p("MÉTODO", s["label"]), p("SHA-256 conservado por archivo", s["value_bold"])]],
            colWidths=[35 * mm, 80 * mm, 35 * mm, 105 * mm],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), PAPER_DEPTH),
                    ("BOX", (0, 0), (-1, -1), 0.75, INK),
                    ("INNERGRID", (0, 0), (-1, -1), 0.35, RULE),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            ),
        ),
        Spacer(1, 12 * mm),
        PageBreak(),
    ]
    for index, item in enumerate(catalog):
        story.append(resource_block(item, s))
        story.append(Spacer(1, 5 * mm))
        if index % 2 == 1 and index != len(catalog) - 1:
            story.append(PageBreak())
    doc.build(story, onFirstPage=page_canvas, onLaterPages=page_canvas)
    shutil.copy2(OUTPUT, ROOT / "public" / OUTPUT.name)
    print(OUTPUT)


if __name__ == "__main__":
    main()
