# app/api/routers/reports.py - ENHANCED VERSION
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ... import schemas, models
from ...database import get_db
from ...utils.auth import get_current_landlord_id

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/", response_model=schemas.ReportResponse)
def create_report(
    report: schemas.ReportCreate,
    landlord_id: int = Depends(get_current_landlord_id),
    db: Session = Depends(get_db)
):
    """Create a financial report for a date range"""
    from ... import crud
    
    db_report = crud.create_report(db, landlord_id, report)
    if not db_report:
        raise HTTPException(status_code=404, detail="Report creation failed")
    return db_report


@router.get("/dashboard")
def get_enhanced_dashboard(
    landlord_id: int = Depends(get_current_landlord_id),
    db: Session = Depends(get_db)
):
    """
    Get enhanced dashboard with comprehensive metrics
    
    Returns:
    - expected_rent: Aggregate of all assigned room rents (black)
    - total_paid: Total payments received (green)
    - outstanding_balance: Sum of all tenant balances (red)
    - total_tenants: Count of active tenants (blue)
    - total_rooms, paid_rooms, partial_rooms, overdue_rooms
    - property_metrics: Per-property breakdown
    """
    from ...crud.report import get_enhanced_dashboard
    
    dashboard = get_enhanced_dashboard(db, landlord_id)
    return dashboard


@router.get("/archived-tenants")
def get_archived_tenants(
    landlord_id: int = Depends(get_current_landlord_id),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get list of archived tenants"""
    from ...crud.report import get_archived_tenants
    
    archived = get_archived_tenants(db, landlord_id, skip, limit)
    return {"archived_tenants": archived}







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
#     """
#     Legacy dashboard endpoint - returns basic metrics
#     Kept for backward compatibility
#     """
#     dashboard = crud.get_dashboard(db, landlord_id)
#     return dashboard


# @router.get("/dashboard/enhanced", response_model=schemas.EnhancedDashboardResponse)
# def get_enhanced_dashboard(
#     landlord_id: int = Depends(get_current_landlord_id),
#     db: Session = Depends(get_db)
# ):
#     """
#     Enhanced dashboard endpoint with comprehensive metrics:
#     - Expected rent and total paid
#     - Outstanding balance across all tenants
#     - Total active tenants count
#     - Overall room payment status breakdown
#     - Per-property metrics and breakdowns
    
#     Perfect for Cameroonian landlords managing multiple properties!
#     """
#     dashboard = crud.get_enhanced_dashboard(db, landlord_id)
#     return dashboard


# @router.get("/archived-tenants", response_model=list[schemas.ArchivedTenantResponse])
# def get_archived_tenants(
#     skip: int = 0,
#     limit: int = 100,
#     landlord_id: int = Depends(get_current_landlord_id),
#     db: Session = Depends(get_db)
# ):
#     """
#     Get list of archived tenants for the landlord
#     """
#     archived = crud.get_archived_tenants(db, landlord_id, skip, limit)
#     return archived


# # #File needs a change 







# # from fastapi import APIRouter, Depends, HTTPException
# # from sqlalchemy.orm import Session
# # from ... import schemas, crud, models
# # from ...database import get_db
# # from ...utils.auth import get_current_landlord_id

# # router = APIRouter(prefix="/reports", tags=["Reports"])

# # @router.post("/", response_model=schemas.ReportResponse)
# # def create_report(
# #     report: schemas.ReportCreate,
# #     landlord_id: int = Depends(get_current_landlord_id),
# #     db: Session = Depends(get_db)
# # ):
# #     db_report = crud.create_report(db, landlord_id, report)
# #     if not db_report:
# #         raise HTTPException(status_code=404, detail="Report creation failed")
# #     return db_report

# # @router.get("/dashboard", response_model=schemas.DashboardResponse)
# # def get_dashboard(
# #     landlord_id: int = Depends(get_current_landlord_id),
# #     db: Session = Depends(get_db)
# # ):
# #     dashboard = crud.get_dashboard(db, landlord_id)
# #     return dashboard