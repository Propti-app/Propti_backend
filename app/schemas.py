from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from typing import Optional, Dict, List
from enum import Enum

class PaymentStatus(str, Enum):
    PAID = "Paid"
    PARTIAL = "Partial"
    OVERDUE = "Overdue"

class PaymentMethod(str, Enum):
    CASH = "Cash"
    MOBILE_MONEY = "Mobile Money"
    BANK = "Bank"

class ReminderStatus(str, Enum):
    SENT = "Sent"
    FAILED = "Failed"

class ReportStatus(str, Enum):
    PENDING = "Pending"
    GENERATED = "Generated"


class LandlordSync(BaseModel):
    """For syncing Firebase users to database - NO PASSWORD"""
    email: EmailStr
    full_name: str
    phone_number: str
    
    class Config:
        from_attributes = True


class LandlordCreate(BaseModel):
    """Legacy - for old password-based auth"""
    email: EmailStr
    phone_number: str
    name: str
    password: str

class LandlordResponse(BaseModel):
    landlord_id: int
    firebase_uid: Optional[str] = None  
    email: EmailStr
    phone_number: str
    name: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    settings: Dict
    
    class Config:
        from_attributes = True

class LandlordSettingsUpdate(BaseModel):
    reminder_interval: int  # Days before due date to send reminder
    default_cycle_days: int  # Default rent cycle length in days
    
    class Config:
        json_schema_extra = {
            "example": {
                "reminder_interval": 3,
                "default_cycle_days": 30
            }
        }

# ============ PROPERTY SCHEMAS ============

class PropertyCreate(BaseModel):
    name: str
    photo: Optional[str] = None

class PropertyResponse(BaseModel):
    property_id: int
    landlord_id: int
    name: str
    photo: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True

# ============ ROOM SCHEMAS ============

class RoomCreate(BaseModel):
    room_number: str
    rent_amount: float
    due_date: int

class RoomResponse(BaseModel):
    room_id: int
    property_id: int
    room_number: str
    rent_amount: float
    due_date: int
    payment_status: PaymentStatus
    updated_at: Optional[datetime]
    tenant: Optional['TenantResponse'] = None
    
    class Config:
        from_attributes = True


class TenantCreate(BaseModel):
    full_name: str
    phone_number: str
    email: Optional[EmailStr] = None
    faculty: Optional[str] = None
    year_of_study: Optional[str] = None
    guardian_phone_number: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_location: Optional[str] = None
    photo: Optional[str] = None
    id_card_number: Optional[str] = None

class TenantResponse(BaseModel):
    tenant_id: int
    full_name: str
    phone_number: str
    email: Optional[str]
    faculty: Optional[str]
    year_of_study: Optional[str]
    guardian_phone_number: Optional[str]
    guardian_name: Optional[str]
    guardian_location: Optional[str]
    photo: Optional[str]
    id_card_number: Optional[str]
    assigned_room_id: Optional[int]
    balance: float
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True

class ArchivedTenantResponse(BaseModel):
    archived_tenant_id: int
    original_tenant_id: int
    full_name: str
    phone_number: str
    email: Optional[str]
    balance: float
    archived_at: datetime
    
    class Config:
        from_attributes = True

# ============ RENT CYCLE SCHEMAS ============

class RentCycleCreate(BaseModel):
    room_id: int
    tenant_id: Optional[int] = None
    start_date: datetime
    end_date: datetime
    amount: float

class RentCycleResponse(BaseModel):
    rent_cycle_id: int
    room_id: int
    tenant_id: Optional[int]
    start_date: datetime
    end_date: datetime
    amount: float
    payment_status: PaymentStatus
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# ============ PAYMENT SCHEMAS ============

class PaymentCreate(BaseModel):
    rent_cycle_id: int
    tenant_id: int
    amount: float
    payment_method: PaymentMethod
    period_start: date
    period_end: date

class PaymentResponse(BaseModel):
    payment_id: int
    rent_cycle_id: int
    tenant_id: int
    amount: float
    payment_date: datetime
    payment_method: PaymentMethod
    period_start: date
    period_end: date
    receipt_number: str
    created_at: datetime
    tenant_name: str
    room_number: str
    landlord_name: str
    landlord_contact: str
    remaining_balance: float
    
    class Config:
        from_attributes = True

class PaymentHistoryResponse(BaseModel):
    payments: List[PaymentResponse]
    
    class Config:
        from_attributes = True

# ============ REMINDER SCHEMAS ============

class ReminderResponse(BaseModel):
    reminder_id: int
    tenant_id: int
    message: str
    medium: PaymentMethod
    sent_at: datetime
    status: ReminderStatus
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============ REPORT SCHEMAS ============

class ReportCreate(BaseModel):
    rent_cycle_id: Optional[int] = None
    start_date: date
    end_date: date

class ReportResponse(BaseModel):
    report_id: int
    landlord_id: int
    rent_cycle_id: Optional[int]
    start_date: date
    end_date: date
    total_expected_rent: float
    total_paid: float
    total_outstanding: float
    net_income: float
    created_at: datetime
    status: ReportStatus
    
    class Config:
        from_attributes = True

# ============ DASHBOARD SCHEMAS ============

class DashboardResponse(BaseModel):
    properties: List[PropertyResponse]
    total_rooms: int
    paid_rooms: int
    partial_rooms: int
    overdue_rooms: int
    
    class Config:
        from_attributes = True





# from pydantic import BaseModel, EmailStr, Field
# from datetime import datetime, date
# from typing import Optional, Dict, List
# from enum import Enum

# class PaymentStatus(str, Enum):
#     PAID = "Paid"
#     PARTIAL = "Partial"
#     OVERDUE = "Overdue"

# class PaymentMethod(str, Enum):
#     CASH = "Cash"
#     MOBILE_MONEY = "Mobile Money"
#     BANK = "Bank"

# class ReminderStatus(str, Enum):
#     SENT = "Sent"
#     FAILED = "Failed"

# class ReportStatus(str, Enum):
#     PENDING = "Pending"
#     GENERATED = "Generated"


# class LandlordSync(BaseModel):
#     """For syncing Firebase users to database - NO PASSWORD"""
#     email: EmailStr
#     full_name: str
#     phone_number: str
    
#     class Config:
#         from_attributes = True



# class LandlordCreate(BaseModel):
#     """Legacy - for old password-based auth"""
#     email: EmailStr
#     phone_number: str
#     name: str
#     password: str

# class LandlordResponse(BaseModel):
#     landlord_id: int
#     firebase_uid: Optional[str] = None  
#     email: EmailStr
#     phone_number: str
#     name: str
#     created_at: datetime
#     updated_at: Optional[datetime] = None
#     settings: Dict
    
#     class Config:
#         from_attributes = True

# class LandlordSettingsUpdate(BaseModel):
#     reminder_interval: str
    

# # ============ PROPERTY SCHEMAS ============

# class PropertyCreate(BaseModel):
#     name: str
#     photo: Optional[str] = None

# class PropertyResponse(BaseModel):
#     property_id: int
#     landlord_id: int
#     name: str
#     photo: Optional[str]
#     created_at: datetime
#     updated_at: Optional[datetime]
#     is_active: bool
    
#     class Config:
#         from_attributes = True

# # ============ ROOM SCHEMAS ============

# class RoomCreate(BaseModel):
#     room_number: str
#     rent_amount: float
#     due_date: int

# class RoomResponse(BaseModel):
#     room_id: int
#     property_id: int
#     room_number: str
#     rent_amount: float
#     due_date: int
#     payment_status: PaymentStatus
#     updated_at: Optional[datetime]
#     tenant: Optional['TenantResponse'] = None
    
#     class Config:
#         from_attributes = True


# class TenantCreate(BaseModel):
#     full_name: str
#     phone_number: str
#     email: Optional[EmailStr] = None
#     faculty: Optional[str] = None
#     year_of_study: Optional[str] = None
#     guardian_phone_number: Optional[str] = None
#     guardian_name: Optional[str] = None
#     guardian_location: Optional[str] = None
#     photo: Optional[str] = None
#     id_card_number: Optional[str] = None

# class TenantResponse(BaseModel):
#     tenant_id: int
#     full_name: str
#     phone_number: str
#     email: Optional[str]
#     faculty: Optional[str]
#     year_of_study: Optional[str]
#     guardian_phone_number: Optional[str]
#     guardian_name: Optional[str]
#     guardian_location: Optional[str]
#     photo: Optional[str]
#     id_card_number: Optional[str]
#     assigned_room_id: Optional[int]
#     balance: float
#     created_at: datetime
#     updated_at: Optional[datetime]
#     is_active: bool
    
#     class Config:
#         from_attributes = True

# class ArchivedTenantResponse(BaseModel):
#     archived_tenant_id: int
#     original_tenant_id: int
#     full_name: str
#     phone_number: str
#     email: Optional[str]
#     balance: float
#     archived_at: datetime
    
#     class Config:
#         from_attributes = True

# # ============ RENT CYCLE SCHEMAS ============

# class RentCycleCreate(BaseModel):
#     room_id: int
#     tenant_id: Optional[int] = None
#     start_date: datetime
#     end_date: datetime
#     amount: float

# class RentCycleResponse(BaseModel):
#     rent_cycle_id: int
#     room_id: int
#     tenant_id: Optional[int]
#     start_date: datetime
#     end_date: datetime
#     amount: float
#     payment_status: PaymentStatus
#     created_at: datetime
#     updated_at: Optional[datetime]
    
#     class Config:
#         from_attributes = True

# # ============ PAYMENT SCHEMAS ============

# class PaymentCreate(BaseModel):
#     rent_cycle_id: int
#     tenant_id: int
#     amount: float
#     payment_method: PaymentMethod
#     period_start: date
#     period_end: date

# class PaymentResponse(BaseModel):
#     payment_id: int
#     rent_cycle_id: int
#     tenant_id: int
#     amount: float
#     payment_date: datetime
#     payment_method: PaymentMethod
#     period_start: date
#     period_end: date
#     receipt_number: str
#     created_at: datetime
#     tenant_name: str
#     room_number: str
#     landlord_name: str
#     landlord_contact: str
#     remaining_balance: float
    
#     class Config:
#         from_attributes = True

# class PaymentHistoryResponse(BaseModel):
#     payments: List[PaymentResponse]
    
#     class Config:
#         from_attributes = True

# # ============ REMINDER SCHEMAS ============

# class ReminderResponse(BaseModel):
#     reminder_id: int
#     tenant_id: int
#     message: str
#     medium: PaymentMethod
#     sent_at: datetime
#     status: ReminderStatus
#     created_at: datetime
    
#     class Config:
#         from_attributes = True

# # ============ REPORT SCHEMAS ============

# class ReportCreate(BaseModel):
#     rent_cycle_id: Optional[int] = None
#     start_date: date
#     end_date: date

# class ReportResponse(BaseModel):
#     report_id: int
#     landlord_id: int
#     rent_cycle_id: Optional[int]
#     start_date: date
#     end_date: date
#     total_expected_rent: float
#     total_paid: float
#     total_outstanding: float
#     net_income: float
#     created_at: datetime
#     status: ReportStatus
    
#     class Config:
#         from_attributes = True

# # ============ DASHBOARD SCHEMAS ============

# class DashboardResponse(BaseModel):
#     properties: List[PropertyResponse]
#     total_rooms: int
#     paid_rooms: int
#     partial_rooms: int
#     overdue_rooms: int
    
#     class Config:
#         from_attributes = True
