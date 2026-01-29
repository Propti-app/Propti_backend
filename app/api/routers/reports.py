










# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from ... import schemas, crud, models
# from ...database import get_db
# from ...utils.auth import get_current_landlord_id

# router = APIRouter(prefix="/reports", tags=["Reports"])

# @router.post("/", response_model=schemas.ReportResponse)
# def create_report(
#     report: schemas.ReportCreate,
#     landlord_id: int = Depends(get_current_landlord_id),
#     db: Session = Depends(get_db)
# ):
#     db_report = crud.create_report(db, landlord_id, report)
#     if not db_report:
#         raise HTTPException(status_code=404, detail="Report creation failed")
#     return db_report

# @router.get("/dashboard", response_model=schemas.DashboardResponse)
# def get_dashboard(
#     landlord_id: int = Depends(get_current_landlord_id),
#     db: Session = Depends(get_db)
# ):
#     dashboard = crud.get_dashboard(db, landlord_id)
#     return dashboard