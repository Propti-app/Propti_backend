# app/schemas.py
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


class PropertyType(str, Enum):
    HOSTEL = "hostel"
    RESIDENTIAL = "residential"


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
    reminder_interval: int
    default_cycle_days: int

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
    location: Optional[str] = None
    property_type: Optional[PropertyType] = PropertyType.HOSTEL  # FIX: typed, not raw str
    photo: Optional[str] = None


class PropertyResponse(BaseModel):
    property_id: int
    landlord_id: int
    name: str
    location: Optional[str] = None
    # The DB native enum may store "HOSTEL" or "hostel" depending on when the
    # row was inserted. We keep this as a plain str and normalise to lowercase
    # via model_validate so the mobile app always gets "hostel"/"residential".
    property_type: Optional[str] = None
    photo: Optional[str] = None
    photo_urls: Optional[List[str]] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        instance = super().model_validate(obj, *args, **kwargs)
        if instance.property_type:
            instance.property_type = instance.property_type.lower()
        return instance


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
    updated_at: Optional[datetime] = None
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
    email: Optional[str] = None
    faculty: Optional[str] = None
    year_of_study: Optional[str] = None
    guardian_phone_number: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_location: Optional[str] = None
    photo: Optional[str] = None
    photo_url: Optional[str] = None
    id_card_number: Optional[str] = None
    id_card_url: Optional[str] = None
    assigned_room_id: Optional[int] = None
    balance: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool
    agreement_signed: Optional[bool] = False
    agreement_url: Optional[str] = None

    class Config:
        from_attributes = True


class ArchivedTenantResponse(BaseModel):
    archived_tenant_id: int
    original_tenant_id: int
    full_name: str
    phone_number: str
    email: Optional[str] = None
    room_number: Optional[str] = None
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
    tenant_id: Optional[int] = None
    start_date: datetime
    end_date: datetime
    amount: float
    payment_status: PaymentStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

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
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    receipt_number: str
    created_at: datetime
    tenant_name: Optional[str] = None
    room_number: Optional[str] = None
    landlord_name: Optional[str] = None
    landlord_contact: Optional[str] = None
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
    rent_cycle_id: Optional[int] = None
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

class PropertyMetrics(BaseModel):
    property_id: int
    property_name: str
    total_rooms: int
    total_tenants: int
    paid_rooms: int
    partial_rooms: int
    overdue_rooms: int

    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    properties: List[PropertyResponse]
    total_rooms: int
    paid_rooms: int
    partial_rooms: int
    overdue_rooms: int

    class Config:
        from_attributes = True


class EnhancedDashboardResponse(BaseModel):
    expected_rent: float
    total_paid: float
    outstanding_balance: float
    total_tenants: int
    properties: List[PropertyResponse]
    total_rooms: int
    paid_rooms: int
    partial_rooms: int
    overdue_rooms: int
    property_metrics: List[PropertyMetrics]

    class Config:
        from_attributes = True











# # app/schemas.py
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


# class PropertyType(str, Enum):
#     HOSTEL = "hostel"
#     RESIDENTIAL = "residential"


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
#     reminder_interval: int
#     default_cycle_days: int

#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "reminder_interval": 3,
#                 "default_cycle_days": 30
#             }
#         }


# # ============ PROPERTY SCHEMAS ============

# class PropertyCreate(BaseModel):
#     name: str
#     location: Optional[str] = None
#     property_type: Optional[PropertyType] = PropertyType.HOSTEL  # FIX: typed, not raw str
#     photo: Optional[str] = None


# class PropertyResponse(BaseModel):
#     property_id: int
#     landlord_id: int
#     name: str
#     location: Optional[str] = None
#     # FIX: use the PropertyType enum (str-based) so Pydantic serializes it as
#     # "hostel" / "residential" — never as "PropertyType.HOSTEL" or None.
#     property_type: Optional[PropertyType] = None
#     photo: Optional[str] = None
#     photo_urls: Optional[List[str]] = []
#     created_at: datetime
#     updated_at: Optional[datetime] = None
#     is_active: bool

#     class Config:
#         from_attributes = True
#         # Pydantic v2: serialize enum members by their value, not name
#         use_enum_values = True


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
#     updated_at: Optional[datetime] = None
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
#     email: Optional[str] = None
#     faculty: Optional[str] = None
#     year_of_study: Optional[str] = None
#     guardian_phone_number: Optional[str] = None
#     guardian_name: Optional[str] = None
#     guardian_location: Optional[str] = None
#     photo: Optional[str] = None
#     photo_url: Optional[str] = None
#     id_card_number: Optional[str] = None
#     id_card_url: Optional[str] = None
#     assigned_room_id: Optional[int] = None
#     balance: float
#     created_at: datetime
#     updated_at: Optional[datetime] = None
#     is_active: bool
#     agreement_signed: Optional[bool] = False
#     agreement_url: Optional[str] = None

#     class Config:
#         from_attributes = True


# class ArchivedTenantResponse(BaseModel):
#     archived_tenant_id: int
#     original_tenant_id: int
#     full_name: str
#     phone_number: str
#     email: Optional[str] = None
#     room_number: Optional[str] = None
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
#     tenant_id: Optional[int] = None
#     start_date: datetime
#     end_date: datetime
#     amount: float
#     payment_status: PaymentStatus
#     created_at: datetime
#     updated_at: Optional[datetime] = None

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
#     period_start: Optional[date] = None
#     period_end: Optional[date] = None
#     receipt_number: str
#     created_at: datetime
#     tenant_name: Optional[str] = None
#     room_number: Optional[str] = None
#     landlord_name: Optional[str] = None
#     landlord_contact: Optional[str] = None
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
#     rent_cycle_id: Optional[int] = None
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

# class PropertyMetrics(BaseModel):
#     property_id: int
#     property_name: str
#     total_rooms: int
#     total_tenants: int
#     paid_rooms: int
#     partial_rooms: int
#     overdue_rooms: int

#     class Config:
#         from_attributes = True


# class DashboardResponse(BaseModel):
#     properties: List[PropertyResponse]
#     total_rooms: int
#     paid_rooms: int
#     partial_rooms: int
#     overdue_rooms: int

#     class Config:
#         from_attributes = True


# class EnhancedDashboardResponse(BaseModel):
#     expected_rent: float
#     total_paid: float
#     outstanding_balance: float
#     total_tenants: int
#     properties: List[PropertyResponse]
#     total_rooms: int
#     paid_rooms: int
#     partial_rooms: int
#     overdue_rooms: int
#     property_metrics: List[PropertyMetrics]

#     class Config:
#         from_attributes = True














# # from pydantic import BaseModel, EmailStr, Field
# # from datetime import datetime, date
# # from typing import Optional, Dict, List
# # from enum import Enum


# # class PaymentStatus(str, Enum):
# #     PAID = "Paid"
# #     PARTIAL = "Partial"
# #     OVERDUE = "Overdue"


# # class PaymentMethod(str, Enum):
# #     CASH = "Cash"
# #     MOBILE_MONEY = "Mobile Money"
# #     BANK = "Bank"


# # class ReminderStatus(str, Enum):
# #     SENT = "Sent"
# #     FAILED = "Failed"


# # class ReportStatus(str, Enum):
# #     PENDING = "Pending"
# #     GENERATED = "Generated"


# # class LandlordSync(BaseModel):
# #     """For syncing Firebase users to database - NO PASSWORD"""
# #     email: EmailStr
# #     full_name: str
# #     phone_number: str

# #     class Config:
# #         from_attributes = True


# # class LandlordCreate(BaseModel):
# #     """Legacy - for old password-based auth"""
# #     email: EmailStr
# #     phone_number: str
# #     name: str
# #     password: str


# # class LandlordResponse(BaseModel):
# #     landlord_id: int
# #     firebase_uid: Optional[str] = None
# #     email: EmailStr
# #     phone_number: str
# #     name: str
# #     created_at: datetime
# #     updated_at: Optional[datetime] = None
# #     settings: Dict

# #     class Config:
# #         from_attributes = True


# # class LandlordSettingsUpdate(BaseModel):
# #     reminder_interval: int
# #     default_cycle_days: int

# #     class Config:
# #         json_schema_extra = {
# #             "example": {
# #                 "reminder_interval": 3,
# #                 "default_cycle_days": 30
# #             }
# #         }


# # # ============ PROPERTY SCHEMAS ============

# # class PropertyCreate(BaseModel):
# #     name: str
# #     location: Optional[str] = None
# #     property_type: Optional[str] = "hostel"
# #     photo: Optional[str] = None


# # class PropertyResponse(BaseModel):
# #     property_id: int
# #     landlord_id: int
# #     name: str
# #     location: Optional[str] = None
# #     property_type: Optional[str] = None
# #     photo: Optional[str] = None
# #     photo_urls: Optional[List[str]] = []
# #     created_at: datetime
# #     updated_at: Optional[datetime] = None
# #     is_active: bool

# #     class Config:
# #         from_attributes = True


# # # ============ ROOM SCHEMAS ============

# # class RoomCreate(BaseModel):
# #     room_number: str
# #     rent_amount: float
# #     due_date: int


# # class RoomResponse(BaseModel):
# #     room_id: int
# #     property_id: int
# #     room_number: str
# #     rent_amount: float
# #     due_date: int
# #     payment_status: PaymentStatus
# #     updated_at: Optional[datetime] = None
# #     tenant: Optional['TenantResponse'] = None

# #     class Config:
# #         from_attributes = True


# # class TenantCreate(BaseModel):
# #     full_name: str
# #     phone_number: str
# #     email: Optional[EmailStr] = None
# #     faculty: Optional[str] = None
# #     year_of_study: Optional[str] = None
# #     guardian_phone_number: Optional[str] = None
# #     guardian_name: Optional[str] = None
# #     guardian_location: Optional[str] = None
# #     photo: Optional[str] = None
# #     id_card_number: Optional[str] = None


# # class TenantResponse(BaseModel):
# #     tenant_id: int
# #     full_name: str
# #     phone_number: str
# #     email: Optional[str] = None
# #     faculty: Optional[str] = None
# #     year_of_study: Optional[str] = None
# #     guardian_phone_number: Optional[str] = None
# #     guardian_name: Optional[str] = None
# #     guardian_location: Optional[str] = None
# #     photo: Optional[str] = None
# #     photo_url: Optional[str] = None
# #     id_card_number: Optional[str] = None
# #     id_card_url: Optional[str] = None
# #     assigned_room_id: Optional[int] = None
# #     balance: float
# #     created_at: datetime
# #     updated_at: Optional[datetime] = None
# #     is_active: bool
# #     agreement_signed: Optional[bool] = False
# #     agreement_url: Optional[str] = None

# #     class Config:
# #         from_attributes = True


# # class ArchivedTenantResponse(BaseModel):
# #     archived_tenant_id: int
# #     original_tenant_id: int
# #     full_name: str
# #     phone_number: str
# #     email: Optional[str] = None
# #     room_number: Optional[str] = None
# #     balance: float
# #     archived_at: datetime

# #     class Config:
# #         from_attributes = True


# # # ============ RENT CYCLE SCHEMAS ============

# # class RentCycleCreate(BaseModel):
# #     room_id: int
# #     tenant_id: Optional[int] = None
# #     start_date: datetime
# #     end_date: datetime
# #     amount: float


# # class RentCycleResponse(BaseModel):
# #     rent_cycle_id: int
# #     room_id: int
# #     tenant_id: Optional[int] = None
# #     start_date: datetime
# #     end_date: datetime
# #     amount: float
# #     payment_status: PaymentStatus
# #     created_at: datetime
# #     updated_at: Optional[datetime] = None

# #     class Config:
# #         from_attributes = True


# # # ============ PAYMENT SCHEMAS ============

# # class PaymentCreate(BaseModel):
# #     rent_cycle_id: int
# #     tenant_id: int
# #     amount: float
# #     payment_method: PaymentMethod
# #     period_start: date
# #     period_end: date


# # class PaymentResponse(BaseModel):
# #     payment_id: int
# #     rent_cycle_id: int
# #     tenant_id: int
# #     amount: float
# #     payment_date: datetime
# #     payment_method: PaymentMethod
# #     period_start: Optional[date] = None
# #     period_end: Optional[date] = None
# #     receipt_number: str
# #     created_at: datetime
# #     tenant_name: Optional[str] = None
# #     room_number: Optional[str] = None
# #     landlord_name: Optional[str] = None
# #     landlord_contact: Optional[str] = None
# #     remaining_balance: float

# #     class Config:
# #         from_attributes = True


# # class PaymentHistoryResponse(BaseModel):
# #     payments: List[PaymentResponse]

# #     class Config:
# #         from_attributes = True


# # # ============ REMINDER SCHEMAS ============

# # class ReminderResponse(BaseModel):
# #     reminder_id: int
# #     tenant_id: int
# #     message: str
# #     medium: PaymentMethod
# #     sent_at: datetime
# #     status: ReminderStatus
# #     created_at: datetime

# #     class Config:
# #         from_attributes = True


# # # ============ REPORT SCHEMAS ============

# # class ReportCreate(BaseModel):
# #     rent_cycle_id: Optional[int] = None
# #     start_date: date
# #     end_date: date


# # class ReportResponse(BaseModel):
# #     report_id: int
# #     landlord_id: int
# #     rent_cycle_id: Optional[int] = None
# #     start_date: date
# #     end_date: date
# #     total_expected_rent: float
# #     total_paid: float
# #     total_outstanding: float
# #     net_income: float
# #     created_at: datetime
# #     status: ReportStatus

# #     class Config:
# #         from_attributes = True


# # # ============ DASHBOARD SCHEMAS ============

# # class PropertyMetrics(BaseModel):
# #     property_id: int
# #     property_name: str
# #     total_rooms: int
# #     total_tenants: int
# #     paid_rooms: int
# #     partial_rooms: int
# #     overdue_rooms: int

# #     class Config:
# #         from_attributes = True


# # class DashboardResponse(BaseModel):
# #     properties: List[PropertyResponse]
# #     total_rooms: int
# #     paid_rooms: int
# #     partial_rooms: int
# #     overdue_rooms: int

# #     class Config:
# #         from_attributes = True


# # class EnhancedDashboardResponse(BaseModel):
# #     expected_rent: float
# #     total_paid: float
# #     outstanding_balance: float
# #     total_tenants: int
# #     properties: List[PropertyResponse]
# #     total_rooms: int
# #     paid_rooms: int
# #     partial_rooms: int
# #     overdue_rooms: int
# #     property_metrics: List[PropertyMetrics]

# #     class Config:
# #         from_attributes = True



