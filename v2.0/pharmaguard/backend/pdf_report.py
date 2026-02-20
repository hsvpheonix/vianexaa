from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from datetime import datetime


def generate_pdf(data, file_path="report.pdf"):

    doc = SimpleDocTemplate(
        file_path,
        rightMargin=40,
        leftMargin=40,
        topMargin=60,
        bottomMargin=40
    )

    elements = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Title'],
        fontSize=20,
        spaceAfter=20
    )

    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10
    )

    normal_style = styles["Normal"]

    # ========================
    # Header
    # ========================

    elements.append(Paragraph("PharmaGuard™ Clinical Pharmacogenomics Report", title_style))
    elements.append(Paragraph(
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        styles["Italic"]
    ))
    elements.append(Spacer(1, 0.4 * inch))

    # ========================
    # Risk Banner
    # ========================

    recommendation = data["result"]["recommendation"]

    if "Safe" in recommendation:
        banner_color = colors.green
    elif "Reduce" in recommendation or "Adjust" in recommendation:
        banner_color = colors.orange
    else:
        banner_color = colors.red

    banner_table = Table([[f" RISK STATUS: {recommendation.upper()} "]],
                         colWidths=[6 * inch])

    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), banner_color),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(banner_table)
    elements.append(Spacer(1, 0.4 * inch))

    # ========================
    # Patient Drug Assessment Table
    # ========================

    elements.append(Paragraph("Patient Drug Assessment", section_style))

    assessment_data = [
        ["Drug", data["drug"]],
        ["Recommendation", recommendation],
        ["Confidence Score", f"{int(data['result']['confidence']*100)}%"],
    ]

    assessment_table = Table(assessment_data, colWidths=[2 * inch, 4 * inch])

    assessment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))

    elements.append(assessment_table)
    elements.append(Spacer(1, 0.5 * inch))

    # ========================
    # Genetic Findings
    # ========================

    if data["result"].get("gene"):
        elements.append(Paragraph("Genetic Findings", section_style))

        gene_data = [
            ["Gene", data["result"]["gene"]],
            ["Phenotype", data["result"]["phenotype"]],
        ]

        gene_table = Table(gene_data, colWidths=[2 * inch, 4 * inch])
        gene_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))

        elements.append(gene_table)
        elements.append(Spacer(1, 0.5 * inch))

    # ========================
    # Clinical Explanation
    # ========================

    if data.get("explanation"):
        elements.append(Paragraph("Clinical Interpretation", section_style))
        elements.append(Spacer(1, 0.2 * inch))
        elements.append(Paragraph(data["explanation"], normal_style))
        elements.append(Spacer(1, 0.5 * inch))

    # ========================
    # Footer Disclaimer
    # ========================

    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(
        "Disclaimer: This report is generated using rule-based pharmacogenomic "
        "evaluation aligned with CPIC-style clinical guidelines. "
        "Clinical decisions should be validated by a licensed healthcare professional.",
        styles["Italic"]
    ))

    doc.build(elements)

    return file_path
