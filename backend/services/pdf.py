import os
import uuid
import markdown

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "generated_proposals")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_pdf_canvas(filepath: str, client_name: str, content: str, language: str = "en", org_name: str = ""):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    
    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.setFillColorRGB(0.31, 0.27, 0.90)
    c.drawString(50, y, f"Sales Proposal: {client_name}")
    
    y -= 22
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(50, y, f"Provider: {org_name or 'Our Company'} | Client: {client_name}")
    
    y -= 15
    c.setStrokeColorRGB(0.85, 0.85, 0.85)
    c.line(50, y, width - 50, y)
    y -= 25
    
    lines = content.split("\n")
    for line in lines:
        if y < 50:
            c.showPage()
            y = height - 50
            
        line_str = line.strip()
        clean_text = line_str.replace("**", "").replace("*", "").replace("###", "").replace("##", "").replace("#", "").strip()
        
        if not clean_text:
            y -= 8
            continue
            
        if line_str.startswith("#"):
            c.setFont("Helvetica-Bold", 11)
            c.setFillColorRGB(0.1, 0.1, 0.2)
            y -= 4
        else:
            c.setFont("Helvetica", 9)
            c.setFillColorRGB(0.2, 0.2, 0.2)
            
        # Wrap line cleanly if long
        max_chars = 95
        while len(clean_text) > max_chars:
            part = clean_text[:max_chars]
            clean_text = clean_text[max_chars:]
            c.drawString(50, y, part)
            y -= 14
            if y < 50:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 9)
                
        if clean_text:
            c.drawString(50, y, clean_text)
            y -= 14
            
    c.save()


def generate_pdf_reportlab(filepath: str, client_name: str, content: str, language: str = "en", org_name: str = ""):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        
        doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#4F46E5'),
            spaceAfter=10
        )
        
        meta_style = ParagraphStyle(
            'DocMeta',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#666666'),
            spaceAfter=14
        )
        
        body_style = ParagraphStyle(
            'BodyTextCustom',
            parent=styles['BodyText'],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6
        )
        
        h2_style = ParagraphStyle(
            'H2Custom',
            parent=styles['Heading2'],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor('#111827'),
            spaceBefore=10,
            spaceAfter=4
        )

        story = []
        header_text = f"Sales Proposal: {client_name}"
        story.append(Paragraph(header_text, title_style))
        story.append(Paragraph(f"Provider: {org_name or 'Our Company'} | Client: {client_name}", meta_style))
        story.append(Spacer(1, 8))
        
        lines = content.split("\n")
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            clean_str = line_str.replace("**", "").replace("*", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if line_str.startswith("#"):
                story.append(Paragraph(clean_str.lstrip("#").strip(), h2_style))
            else:
                story.append(Paragraph(clean_str, body_style))
                
        doc.build(story)
    except Exception as e:
        # Fallback to canvas
        generate_pdf_canvas(filepath, client_name, content, language, org_name)


def generate_pdf(
    client_name: str,
    content: str,
    language: str = "en",
    org_name: str = "",
    brand_color: str = "#4F46E5",
    logo_url: str = "",
) -> str:
    filename = f"proposal_{uuid.uuid4().hex[:12]}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    try:
        from weasyprint import HTML
        content_html = markdown.markdown(content, extensions=["tables", "fenced_code"])
        title = "Sales Proposal" if language == "en" else "عرض أسعار"
        
        html_str = f"""<!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8">
        <style>
          body {{ font-family: sans-serif; padding: 20px; line-height: 1.6; color: #333; }}
          h1 {{ color: {brand_color}; border-bottom: 2px solid {brand_color}; padding-bottom: 5px; }}
          h2 {{ color: #111827; margin-top: 20px; }}
        </style>
        </head>
        <body>
          <h1>{title}: {client_name}</h1>
          <p><strong>Provider:</strong> {org_name or 'Our Company'}</p>
          <hr/>
          {content_html}
        </body>
        </html>"""
        
        HTML(string=html_str).write_pdf(filepath)
    except Exception:
        # Multi-tiered fallback
        generate_pdf_reportlab(filepath, client_name, content, language, org_name)

    return filepath
