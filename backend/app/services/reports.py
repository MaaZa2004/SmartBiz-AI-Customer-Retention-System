import io
from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# openpyxl imports for Excel generation
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from app.models.models import Customer, Prediction, Recommendation, Sale

def generate_pdf_report(db: Session) -> bytes:
    """Generates an executive-level PDF report summarizing decision intelligence and recommendations."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#0B0F19'),
        spaceAfter=15
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=15,
        spaceAfter=10
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#374151')
    )
    
    table_text = ParagraphStyle(
        'TableText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1F2937')
    )
    
    table_header_text = ParagraphStyle(
        'TableHeaderText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=colors.white
    )

    story = []
    
    # 1. Header/Title
    story.append(Paragraph("SmartBiz AI: Decision Intelligence Report", title_style))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", body_style))
    story.append(Spacer(1, 15))
    
    # 2. Executive Summary KPIs
    total_customers = db.query(Customer).count()
    churned_customers = db.query(Customer).filter(Customer.churn == 1).count()
    churn_rate = (churned_customers / total_customers * 100) if total_customers > 0 else 0.0
    
    total_revenue = db.query(Customer.total_spending).as_scalar()
    total_rev_val = db.query(Customer).value(Customer.total_spending.label("total"))
    sum_rev = db.query(Customer).with_entities(Customer.total_spending).all()
    total_spending_sum = sum(float(x[0]) for x in sum_rev if x[0] is not None)
    
    story.append(Paragraph("Executive Summary", section_heading))
    kpi_data = [
        [
            Paragraph("<b>Total Customer Base:</b>", body_style),
            Paragraph(f"{total_customers:,}", body_style),
            Paragraph("<b>Total Spending (Revenue):</b>", body_style),
            Paragraph(f"${total_spending_sum:,.2f}", body_style)
        ],
        [
            Paragraph("<b>Customers Marked At-Risk:</b>", body_style),
            Paragraph(f"{churned_customers:,}", body_style),
            Paragraph("<b>System Churn Rate:</b>", body_style),
            Paragraph(f"{churn_rate:.2f}%", body_style)
        ]
    ]
    kpi_table = Table(kpi_data, colWidths=[150, 100, 150, 120])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F3F4F6')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 20))
    
    # 3. Priority Recommendations Table
    story.append(Paragraph("High-Priority Business Recommendations", section_heading))
    
    recs = db.query(Recommendation).filter(Recommendation.priority == "High").order_by(Recommendation.created_at.desc()).limit(15).all()
    
    if not recs:
        story.append(Paragraph("No high-priority recommendations generated yet. Run the Decision Engine for at-risk customers.", body_style))
    else:
        table_data = [[
            Paragraph("Customer ID", table_header_text),
            Paragraph("Action Type", table_header_text),
            Paragraph("Recommendation Plan", table_header_text),
            Paragraph("Priority", table_header_text)
        ]]
        
        for r in recs:
            table_data.append([
                Paragraph(r.customer_id, table_text),
                Paragraph(r.action_type.title(), table_text),
                Paragraph(r.recommendation_text, table_text),
                Paragraph(f"<b>{r.priority}</b>", ParagraphStyle('RedText', parent=table_text, textColor=colors.HexColor('#EF4444')))
            ])
            
        rec_table = Table(table_data, colWidths=[80, 100, 290, 60])
        rec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(rec_table)
        
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

def generate_excel_report(db: Session) -> bytes:
    """Generates a structured, multi-sheet Excel workbook representing business intelligence data."""
    wb = openpyxl.Workbook()
    
    # Styles Setup
    header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    kpi_fill = PatternFill(start_color="F3F4F6", end_color="F3F4F6", fill_type="solid")
    
    title_font = Font(name="Calibri", size=16, bold=True, color="1E3A8A")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    bold_font = Font(name="Calibri", size=11, bold=True)
    regular_font = Font(name="Calibri", size=11)
    
    thin_border = Border(
        left=Side(style='thin', color='CCCCCC'),
        right=Side(style='thin', color='CCCCCC'),
        top=Side(style='thin', color='CCCCCC'),
        bottom=Side(style='thin', color='CCCCCC')
    )
    
    # --- SHEET 1: OVERVIEW ---
    ws_overview = wb.active
    ws_overview.title = "Executive Summary"
    ws_overview.views.sheetView[0].showGridLines = True
    
    ws_overview.cell(row=2, column=2, value="SmartBiz AI - Executive Summary").font = title_font
    ws_overview.cell(row=3, column=2, value=f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}").font = Font(name="Calibri", size=10, italic=True)
    
    # Calculate values
    total_customers = db.query(Customer).count()
    churned_customers = db.query(Customer).filter(Customer.churn == 1).count()
    churn_rate = (churned_customers / total_customers * 100) if total_customers > 0 else 0.0
    
    sum_rev = db.query(Customer).with_entities(Customer.total_spending).all()
    total_spending_sum = sum(float(x[0]) for x in sum_rev if x[0] is not None)
    
    kpis = [
        ("Total Customer Base", total_customers, "#,##0"),
        ("At-Risk Customers (High Churn)", churned_customers, "#,##0"),
        ("System Churn Rate", churn_rate / 100.0, "0.00%"),
        ("Total Sales Revenue", total_spending_sum, "$#,##0.00")
    ]
    
    # Render KPI Cards in grid
    for idx, (kpi_name, kpi_val, val_format) in enumerate(kpis):
        row_idx = 5 + idx
        ws_overview.cell(row=row_idx, column=2, value=kpi_name).font = bold_font
        ws_overview.cell(row=row_idx, column=2).fill = kpi_fill
        ws_overview.cell(row=row_idx, column=2).border = thin_border
        
        val_cell = ws_overview.cell(row=row_idx, column=3, value=kpi_val)
        val_cell.font = regular_font
        val_cell.number_format = val_format
        val_cell.fill = kpi_fill
        val_cell.border = thin_border
        
    # --- SHEET 2: AT-RISK CUSTOMERS ---
    ws_cust = wb.create_sheet(title="At-Risk Customers")
    ws_cust.views.sheetView[0].showGridLines = True
    
    headers = [
        "Customer ID", "Name", "Gender", "Age", "Tenure (Months)", 
        "Satisfaction Score", "Num Orders", "Total Spending", 
        "Days Since Last Order", "Cashback Amount", "Has Complained"
    ]
    
    # Write headers
    for col_idx, h in enumerate(headers, start=1):
        cell = ws_cust.cell(row=1, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")
        
    # Fetch churned customers
    churned_list = db.query(Customer).filter(Customer.churn == 1).order_by(Customer.total_spending.desc()).all()
    
    for r_idx, c in enumerate(churned_list, start=2):
        ws_cust.cell(row=r_idx, column=1, value=c.id).font = regular_font
        ws_cust.cell(row=r_idx, column=2, value=c.name).font = regular_font
        ws_cust.cell(row=r_idx, column=3, value=c.gender).font = regular_font
        ws_cust.cell(row=r_idx, column=4, value=c.age).font = regular_font
        ws_cust.cell(row=r_idx, column=5, value=c.tenure).font = regular_font
        ws_cust.cell(row=r_idx, column=6, value=c.satisfaction_score).font = regular_font
        ws_cust.cell(row=r_idx, column=7, value=c.num_orders).font = regular_font
        
        spend = ws_cust.cell(row=r_idx, column=8, value=float(c.total_spending))
        spend.number_format = "$#,##0.00"
        spend.font = regular_font
        
        ws_cust.cell(row=r_idx, column=9, value=c.days_since_last_order).font = regular_font
        
        cash = ws_cust.cell(row=r_idx, column=10, value=float(c.cashback_amount))
        cash.number_format = "$#,##0.00"
        cash.font = regular_font
        
        ws_cust.cell(row=r_idx, column=11, value="Yes" if c.complain == 1 else "No").font = regular_font
        
        # Apply borders to cells
        for col_idx in range(1, 12):
            ws_cust.cell(row=r_idx, column=col_idx).border = thin_border
            
    # Autofit column widths
    for col in ws_cust.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws_cust.column_dimensions[col_letter].width = max(max_len + 3, 10)
        
    # --- SHEET 3: RECOMMENDATIONS ---
    ws_recs = wb.create_sheet(title="Next-Best-Actions")
    ws_recs.views.sheetView[0].showGridLines = True
    
    rec_headers = ["Customer ID", "Recommendation text", "Action Type", "Priority", "Created At"]
    for col_idx, h in enumerate(rec_headers, start=1):
        cell = ws_recs.cell(row=1, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")
        
    all_recs = db.query(Recommendation).order_by(Recommendation.priority.desc(), Recommendation.created_at.desc()).all()
    
    for r_idx, r in enumerate(all_recs, start=2):
        ws_recs.cell(row=r_idx, column=1, value=r.customer_id).font = regular_font
        ws_recs.cell(row=r_idx, column=2, value=r.recommendation_text).font = regular_font
        ws_recs.cell(row=r_idx, column=3, value=r.action_type.title()).font = regular_font
        
        prio_cell = ws_recs.cell(row=r_idx, column=4, value=r.priority)
        prio_cell.font = bold_font
        if r.priority == "High":
            prio_cell.font = Font(name="Calibri", bold=True, color="FF0000") # Red text
        
        ws_recs.cell(row=r_idx, column=5, value=r.created_at.strftime("%Y-%m-%d %H:%M:%S")).font = regular_font
        
        for col_idx in range(1, 6):
            ws_recs.cell(row=r_idx, column=col_idx).border = thin_border
            
    # Autofit column widths for Sheet 3
    for col in ws_recs.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws_recs.column_dimensions[col_letter].width = max(min(max_len + 3, 50), 10) # limit wide text columns to 50
        
    # Write workbook to bytes
    excel_bytes = io.BytesIO()
    wb.save(excel_bytes)
    excel_data = excel_bytes.getvalue()
    excel_bytes.close()
    return excel_data
