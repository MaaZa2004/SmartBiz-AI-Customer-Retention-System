from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.auth import require_authenticated
from app.services.reports import generate_pdf_report, generate_excel_report

router = APIRouter(prefix="/reports", tags=["Reports Export"])

@router.get("/export")
def export_reports(
    format: str = Query("excel", regex="^(pdf|excel)$", description="Format to export: 'pdf' or 'excel'"),
    db: Session = Depends(get_db),
    current_user = Depends(require_authenticated)
):
    """
    Exports a comprehensive business intelligence report in PDF or Excel format.
    Requires authentication.
    """
    try:
        if format == "pdf":
            pdf_data = generate_pdf_report(db)
            filename = "smartbiz_retention_report.pdf"
            media_type = "application/pdf"
            data_bytes = pdf_data
        else:
            excel_data = generate_excel_report(db)
            filename = "smartbiz_retention_report.xlsx"
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            data_bytes = excel_data
            
        headers = {
            "Content-Disposition": f"attachment; filename={filename}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
        
        return Response(
            content=data_bytes,
            media_type=media_type,
            headers=headers
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report export failed: {str(e)}"
        )
