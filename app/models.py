# app/models.py
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean,
    Enum, ForeignKey, JSON, Date, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text
from .database import Base
import enum


class PaymentStatus(enum.Enum):
    PAID = "Paid"
    PARTIAL = "Partial"
    OVERDUE = "Overdue"


class PaymentMethod(enum.Enum):
    CASH = "Cash"
    MOBILE_MONEY = "Mobile Money"
    BANK = "Bank"


class ReminderStatus(enum.Enum):
    SENT = "Sent"
    FAILED = "Failed"


class ReportStatus(enum.Enum):
    PENDING = "Pending"
    GENERATED = "Generated"


class PropertyType(enum.Enum):
    HOSTEL = "hostel"           # Student hostel → "Rooms"
    RESIDENTIAL = "residential" # Normal building → "Units/Apartments"


# ─────────────────────────────────────────────────────────────────────────────

class Landlord(Base):
    __tablename__ = "landlords"

    landlord_id   = Column(Integer, primary_key=True, index=True)
    email         = Column(String, unique=True, index=True)
    phone_number  = Column(String)
    password_hash = Column(String, nullable=True)
    name          = Column(String)
    firebase_uid  = Column(String(128), unique=True, nullable=True)
    fcm_token     = Column(String, nullable=True)
    created_at    = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at    = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))
    settings      = Column(JSON, default={"reminder_interval": "weekly"})

    properties = relationship("Property", back_populates="landlord")


class Property(Base):
    __tablename__ = "properties"

    property_id   = Column(Integer, primary_key=True, index=True)
    landlord_id   = Column(Integer, ForeignKey("landlords.landlord_id"))
    name          = Column(String)
    location      = Column(String, nullable=True)
    # FIX: use plain String instead of SQLAlchemy Enum so we are completely
    # decoupled from the DB-level "propertytype" enum type. The DB has a native
    # PostgreSQL enum with uppercase labels (HOSTEL/RESIDENTIAL) that conflicts
    # with whatever Python-side values_callable we set. By storing as a raw
    # VARCHAR we read exactly what is in the DB and let the schema layer
    # (Pydantic) normalise casing before it reaches the mobile app.
    property_type = Column(String, default="hostel")
    photo      = Column(String, nullable=True)
    photo_urls = Column(JSON, default=list)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))
    is_active  = Column(Boolean, default=True)

    landlord = relationship("Landlord", back_populates="properties")
    rooms    = relationship("Room", back_populates="property")


class Room(Base):
    __tablename__ = "rooms"

    room_id        = Column(Integer, primary_key=True, index=True)
    property_id    = Column(Integer, ForeignKey("properties.property_id"))
    room_number    = Column(String)
    rent_amount    = Column(Float)
    due_date       = Column(Integer)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.OVERDUE)
    is_occupied    = Column(Boolean, default=False)
    updated_at     = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))

    property    = relationship("Property", back_populates="rooms")
    tenants     = relationship("Tenant", back_populates="assigned_room")
    rent_cycles = relationship("RentCycle", back_populates="room")


class Tenant(Base):
    __tablename__ = "tenants"

    tenant_id             = Column(Integer, primary_key=True, index=True)
    landlord_id           = Column(Integer, ForeignKey("landlords.landlord_id"))
    full_name             = Column(String)
    phone_number          = Column(String)
    email                 = Column(String, nullable=True)
    faculty               = Column(String, nullable=True)
    year_of_study         = Column(String, nullable=True)
    guardian_phone_number = Column(String, nullable=True)
    guardian_name         = Column(String, nullable=True)
    guardian_location     = Column(String, nullable=True)

    photo        = Column(String, nullable=True)
    photo_url    = Column(String, nullable=True)
    id_card_url  = Column(String, nullable=True)
    id_card_number = Column(String, nullable=True)

    assigned_room_id    = Column(Integer, ForeignKey("rooms.room_id"), nullable=True)
    balance             = Column(Float, default=0.0)
    created_at          = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at          = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))
    is_active           = Column(Boolean, default=True)

    agreement_signed    = Column(Boolean, default=False)
    agreement_signed_at = Column(DateTime, nullable=True)
    agreement_url       = Column(String, nullable=True)
    agreement_file_id   = Column(String, nullable=True)

    landlord      = relationship("Landlord")
    assigned_room = relationship("Room", back_populates="tenants")
    payments      = relationship("Payment", back_populates="tenant")
    reminders     = relationship("Reminder", back_populates="tenant")


class ArchivedTenant(Base):
    __tablename__ = "archived_tenants"

    archived_tenant_id = Column(Integer, primary_key=True, index=True)
    original_tenant_id = Column(Integer)
    landlord_id        = Column(Integer, ForeignKey("landlords.landlord_id"))
    full_name          = Column(String)
    phone_number       = Column(String)
    email              = Column(String, nullable=True)
    room_number        = Column(String, nullable=True)
    balance            = Column(Float)
    agreement_url      = Column(String, nullable=True)
    archived_at        = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))


class RentCycle(Base):
    __tablename__ = "rent_cycles"

    rent_cycle_id  = Column(Integer, primary_key=True, index=True)
    room_id        = Column(Integer, ForeignKey("rooms.room_id"))
    tenant_id      = Column(Integer, ForeignKey("tenants.tenant_id"), nullable=True)
    start_date     = Column(DateTime)
    end_date       = Column(DateTime)
    amount         = Column(Float)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.OVERDUE)
    created_at     = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at     = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))

    room     = relationship("Room", back_populates="rent_cycles")
    payments = relationship("Payment", back_populates="rent_cycle")


class Payment(Base):
    __tablename__ = "payments"

    payment_id     = Column(Integer, primary_key=True, index=True)
    rent_cycle_id  = Column(Integer, ForeignKey("rent_cycles.rent_cycle_id"))
    tenant_id      = Column(Integer, ForeignKey("tenants.tenant_id"))
    amount         = Column(Float)
    payment_date   = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    payment_method = Column(
        Enum(
            PaymentMethod,
            values_callable=lambda x: [e.value for e in x],
            create_constraint=True,
            native_enum=False,
        ),
        default=PaymentMethod.CASH,
    )
    period_start   = Column(Date, nullable=True)
    period_end     = Column(Date, nullable=True)
    receipt_number = Column(String)
    created_at     = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    rent_cycle = relationship("RentCycle", back_populates="payments")
    tenant     = relationship("Tenant", back_populates="payments")


class Reminder(Base):
    __tablename__ = "reminders"

    reminder_id = Column(Integer, primary_key=True, index=True)
    tenant_id   = Column(Integer, ForeignKey("tenants.tenant_id"))
    message     = Column(String)
    medium      = Column(
        Enum(
            PaymentMethod,
            values_callable=lambda x: [e.value for e in x],
            create_constraint=True,
            native_enum=False,
        ),
        default=PaymentMethod.CASH,
    )
    sent_at    = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    status     = Column(Enum(ReminderStatus), default=ReminderStatus.SENT)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    tenant = relationship("Tenant", back_populates="reminders")


class Report(Base):
    __tablename__ = "reports"

    report_id           = Column(Integer, primary_key=True, index=True)
    landlord_id         = Column(Integer, ForeignKey("landlords.landlord_id"))
    rent_cycle_id       = Column(Integer, ForeignKey("rent_cycles.rent_cycle_id"), nullable=True)
    start_date          = Column(Date)
    end_date            = Column(Date)
    total_expected_rent = Column(Float)
    total_paid          = Column(Float)
    total_outstanding   = Column(Float)
    net_income          = Column(Float)
    created_at          = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    status              = Column(Enum(ReportStatus), default=ReportStatus.GENERATED)

















# # app/models.py
# from sqlalchemy import (
#     Column, Integer, String, Float, DateTime, Boolean,
#     Enum, ForeignKey, JSON, Date, Text
# )
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import text
# from .database import Base
# import enum


# class PaymentStatus(enum.Enum):
#     PAID = "Paid"
#     PARTIAL = "Partial"
#     OVERDUE = "Overdue"


# class PaymentMethod(enum.Enum):
#     CASH = "Cash"
#     MOBILE_MONEY = "Mobile Money"
#     BANK = "Bank"


# class ReminderStatus(enum.Enum):
#     SENT = "Sent"
#     FAILED = "Failed"


# class ReportStatus(enum.Enum):
#     PENDING = "Pending"
#     GENERATED = "Generated"


# class PropertyType(enum.Enum):
#     HOSTEL = "hostel"           # Student hostel → "Rooms"
#     RESIDENTIAL = "residential" # Normal building → "Units/Apartments"


# # ─────────────────────────────────────────────────────────────────────────────

# class Landlord(Base):
#     __tablename__ = "landlords"

#     landlord_id   = Column(Integer, primary_key=True, index=True)
#     email         = Column(String, unique=True, index=True)
#     phone_number  = Column(String)
#     password_hash = Column(String, nullable=True)
#     name          = Column(String)
#     firebase_uid  = Column(String(128), unique=True, nullable=True)
#     fcm_token     = Column(String, nullable=True)
#     created_at    = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
#     updated_at    = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))
#     settings      = Column(JSON, default={"reminder_interval": "weekly"})

#     properties = relationship("Property", back_populates="landlord")


# class Property(Base):
#     __tablename__ = "properties"

#     property_id   = Column(Integer, primary_key=True, index=True)
#     landlord_id   = Column(Integer, ForeignKey("landlords.landlord_id"))
#     name          = Column(String)
#     location      = Column(String, nullable=True)
#     # FIX: use values_callable so SQLAlchemy stores/reads the .value ("hostel" /
#     # "residential") instead of the .name ("HOSTEL" / "RESIDENTIAL").
#     # This matches what is already in the database and what the rest of the
#     # codebase (schemas, mobile app) sends as strings.
#     property_type = Column(
#         Enum(
#             PropertyType,
#             values_callable=lambda x: [e.value for e in x],
#             create_constraint=True,
#             native_enum=False,          # store as VARCHAR, not a DB-level enum
#         ),
#         default=PropertyType.HOSTEL,
#     )
#     photo      = Column(String, nullable=True)
#     photo_urls = Column(JSON, default=list)
#     created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
#     updated_at = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))
#     is_active  = Column(Boolean, default=True)

#     landlord = relationship("Landlord", back_populates="properties")
#     rooms    = relationship("Room", back_populates="property")


# class Room(Base):
#     __tablename__ = "rooms"

#     room_id        = Column(Integer, primary_key=True, index=True)
#     property_id    = Column(Integer, ForeignKey("properties.property_id"))
#     room_number    = Column(String)
#     rent_amount    = Column(Float)
#     due_date       = Column(Integer)
#     payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.OVERDUE)
#     is_occupied    = Column(Boolean, default=False)
#     updated_at     = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))

#     property    = relationship("Property", back_populates="rooms")
#     tenants     = relationship("Tenant", back_populates="assigned_room")
#     rent_cycles = relationship("RentCycle", back_populates="room")


# class Tenant(Base):
#     __tablename__ = "tenants"

#     tenant_id             = Column(Integer, primary_key=True, index=True)
#     landlord_id           = Column(Integer, ForeignKey("landlords.landlord_id"))
#     full_name             = Column(String)
#     phone_number          = Column(String)
#     email                 = Column(String, nullable=True)
#     faculty               = Column(String, nullable=True)
#     year_of_study         = Column(String, nullable=True)
#     guardian_phone_number = Column(String, nullable=True)
#     guardian_name         = Column(String, nullable=True)
#     guardian_location     = Column(String, nullable=True)

#     photo        = Column(String, nullable=True)
#     photo_url    = Column(String, nullable=True)
#     id_card_url  = Column(String, nullable=True)
#     id_card_number = Column(String, nullable=True)

#     assigned_room_id    = Column(Integer, ForeignKey("rooms.room_id"), nullable=True)
#     balance             = Column(Float, default=0.0)
#     created_at          = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
#     updated_at          = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))
#     is_active           = Column(Boolean, default=True)

#     agreement_signed    = Column(Boolean, default=False)
#     agreement_signed_at = Column(DateTime, nullable=True)
#     agreement_url       = Column(String, nullable=True)
#     agreement_file_id   = Column(String, nullable=True)

#     landlord      = relationship("Landlord")
#     assigned_room = relationship("Room", back_populates="tenants")
#     payments      = relationship("Payment", back_populates="tenant")
#     reminders     = relationship("Reminder", back_populates="tenant")


# class ArchivedTenant(Base):
#     __tablename__ = "archived_tenants"

#     archived_tenant_id = Column(Integer, primary_key=True, index=True)
#     original_tenant_id = Column(Integer)
#     landlord_id        = Column(Integer, ForeignKey("landlords.landlord_id"))
#     full_name          = Column(String)
#     phone_number       = Column(String)
#     email              = Column(String, nullable=True)
#     room_number        = Column(String, nullable=True)
#     balance            = Column(Float)
#     agreement_url      = Column(String, nullable=True)
#     archived_at        = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))


# class RentCycle(Base):
#     __tablename__ = "rent_cycles"

#     rent_cycle_id  = Column(Integer, primary_key=True, index=True)
#     room_id        = Column(Integer, ForeignKey("rooms.room_id"))
#     tenant_id      = Column(Integer, ForeignKey("tenants.tenant_id"), nullable=True)
#     start_date     = Column(DateTime)
#     end_date       = Column(DateTime)
#     amount         = Column(Float)
#     payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.OVERDUE)
#     created_at     = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
#     updated_at     = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))

#     room     = relationship("Room", back_populates="rent_cycles")
#     payments = relationship("Payment", back_populates="rent_cycle")


# class Payment(Base):
#     __tablename__ = "payments"

#     payment_id     = Column(Integer, primary_key=True, index=True)
#     rent_cycle_id  = Column(Integer, ForeignKey("rent_cycles.rent_cycle_id"))
#     tenant_id      = Column(Integer, ForeignKey("tenants.tenant_id"))
#     amount         = Column(Float)
#     payment_date   = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
#     payment_method = Column(
#         Enum(
#             PaymentMethod,
#             values_callable=lambda x: [e.value for e in x],
#             create_constraint=True,
#             native_enum=False,
#         ),
#         default=PaymentMethod.CASH,
#     )
#     period_start   = Column(Date, nullable=True)
#     period_end     = Column(Date, nullable=True)
#     receipt_number = Column(String)
#     created_at     = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

#     rent_cycle = relationship("RentCycle", back_populates="payments")
#     tenant     = relationship("Tenant", back_populates="payments")


# class Reminder(Base):
#     __tablename__ = "reminders"

#     reminder_id = Column(Integer, primary_key=True, index=True)
#     tenant_id   = Column(Integer, ForeignKey("tenants.tenant_id"))
#     message     = Column(String)
#     medium      = Column(
#         Enum(
#             PaymentMethod,
#             values_callable=lambda x: [e.value for e in x],
#             create_constraint=True,
#             native_enum=False,
#         ),
#         default=PaymentMethod.CASH,
#     )
#     sent_at    = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
#     status     = Column(Enum(ReminderStatus), default=ReminderStatus.SENT)
#     created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

#     tenant = relationship("Tenant", back_populates="reminders")


# class Report(Base):
#     __tablename__ = "reports"

#     report_id           = Column(Integer, primary_key=True, index=True)
#     landlord_id         = Column(Integer, ForeignKey("landlords.landlord_id"))
#     rent_cycle_id       = Column(Integer, ForeignKey("rent_cycles.rent_cycle_id"), nullable=True)
#     start_date          = Column(Date)
#     end_date            = Column(Date)
#     total_expected_rent = Column(Float)
#     total_paid          = Column(Float)
#     total_outstanding   = Column(Float)
#     net_income          = Column(Float)
#     created_at          = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
#     status              = Column(Enum(ReportStatus), default=ReportStatus.GENERATED)
















# # # app/models.py  ← REPLACE ENTIRE FILE
# # from sqlalchemy import (
# #     Column, Integer, String, Float, DateTime, Boolean,
# #     Enum, ForeignKey, JSON, Date, Text
# # )
# # from sqlalchemy.orm import relationship
# # from sqlalchemy.sql import text
# # from .database import Base
# # import enum


# # class PaymentStatus(enum.Enum):
# #     PAID = "Paid"
# #     PARTIAL = "Partial"
# #     OVERDUE = "Overdue"


# # class PaymentMethod(enum.Enum):
# #     CASH = "Cash"
# #     MOBILE_MONEY = "Mobile Money"
# #     BANK = "Bank"


# # class ReminderStatus(enum.Enum):
# #     SENT = "Sent"
# #     FAILED = "Failed"


# # class ReportStatus(enum.Enum):
# #     PENDING = "Pending"
# #     GENERATED = "Generated"


# # class PropertyType(enum.Enum):
# #     HOSTEL = "hostel"           # Student hostel → "Rooms"
# #     RESIDENTIAL = "residential" # Normal building → "Units/Apartments"


# # # ─────────────────────────────────────────────────────────────────────────────

# # class Landlord(Base):
# #     __tablename__ = "landlords"

# #     landlord_id  = Column(Integer, primary_key=True, index=True)
# #     email        = Column(String, unique=True, index=True)
# #     phone_number = Column(String)
# #     password_hash = Column(String, nullable=True)
# #     name         = Column(String)
# #     firebase_uid = Column(String(128), unique=True, nullable=True)
# #     fcm_token    = Column(String, nullable=True)   # ← FCM push token
# #     created_at   = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
# #     updated_at   = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))
# #     settings     = Column(JSON, default={"reminder_interval": "weekly"})

# #     properties   = relationship("Property", back_populates="landlord")


# # class Property(Base):
# #     __tablename__ = "properties"

# #     property_id   = Column(Integer, primary_key=True, index=True)
# #     landlord_id   = Column(Integer, ForeignKey("landlords.landlord_id"))
# #     name          = Column(String)
# #     location      = Column(String, nullable=True)
# #     property_type = Column(
# #         Enum(PropertyType), default=PropertyType.HOSTEL
# #     )  # ← hostel vs residential
# #     photo         = Column(String, nullable=True)           # legacy single photo
# #     photo_urls    = Column(JSON, default=list)              # ← Appwrite URLs list
# #     created_at    = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
# #     updated_at    = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))
# #     is_active     = Column(Boolean, default=True)

# #     landlord = relationship("Landlord", back_populates="properties")
# #     rooms    = relationship("Room", back_populates="property")


# # class Room(Base):
# #     __tablename__ = "rooms"

# #     room_id        = Column(Integer, primary_key=True, index=True)
# #     property_id    = Column(Integer, ForeignKey("properties.property_id"))
# #     room_number    = Column(String)
# #     rent_amount    = Column(Float)
# #     due_date       = Column(Integer)
# #     payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.OVERDUE)
# #     is_occupied    = Column(Boolean, default=False)
# #     updated_at     = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))

# #     property    = relationship("Property", back_populates="rooms")
# #     tenants     = relationship("Tenant", back_populates="assigned_room")
# #     rent_cycles = relationship("RentCycle", back_populates="room")


# # class Tenant(Base):
# #     __tablename__ = "tenants"

# #     tenant_id            = Column(Integer, primary_key=True, index=True)
# #     landlord_id          = Column(Integer, ForeignKey("landlords.landlord_id"))
# #     full_name            = Column(String)
# #     phone_number         = Column(String)
# #     email                = Column(String, nullable=True)
# #     faculty              = Column(String, nullable=True)
# #     year_of_study        = Column(String, nullable=True)
# #     guardian_phone_number= Column(String, nullable=True)
# #     guardian_name        = Column(String, nullable=True)
# #     guardian_location    = Column(String, nullable=True)

# #     # ── Appwrite media ──────────────────────────────────────────────────────
# #     photo                = Column(String, nullable=True)  # legacy
# #     photo_url            = Column(String, nullable=True)  # ← Appwrite URL
# #     id_card_url          = Column(String, nullable=True)  # ← Appwrite ID scan URL
# #     id_card_number       = Column(String, nullable=True)

# #     assigned_room_id     = Column(Integer, ForeignKey("rooms.room_id"), nullable=True)
# #     balance              = Column(Float, default=0.0)
# #     created_at           = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
# #     updated_at           = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))
# #     is_active            = Column(Boolean, default=True)

# #     # ── Agreement ───────────────────────────────────────────────────────────
# #     agreement_signed     = Column(Boolean, default=False)
# #     agreement_signed_at  = Column(DateTime, nullable=True)
# #     agreement_url        = Column(String, nullable=True)   # ← Appwrite PDF URL
# #     agreement_file_id    = Column(String, nullable=True)   # ← Appwrite file ID

# #     landlord     = relationship("Landlord")
# #     assigned_room= relationship("Room", back_populates="tenants")
# #     payments     = relationship("Payment", back_populates="tenant")
# #     reminders    = relationship("Reminder", back_populates="tenant")


# # class ArchivedTenant(Base):
# #     __tablename__ = "archived_tenants"

# #     archived_tenant_id = Column(Integer, primary_key=True, index=True)
# #     original_tenant_id = Column(Integer)
# #     landlord_id        = Column(Integer, ForeignKey("landlords.landlord_id"))
# #     full_name          = Column(String)
# #     phone_number       = Column(String)
# #     email              = Column(String, nullable=True)
# #     room_number        = Column(String, nullable=True)
# #     balance            = Column(Float)
# #     agreement_url      = Column(String, nullable=True)  # keep agreement after vacating
# #     archived_at        = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))


# # class RentCycle(Base):
# #     __tablename__ = "rent_cycles"

# #     rent_cycle_id  = Column(Integer, primary_key=True, index=True)
# #     room_id        = Column(Integer, ForeignKey("rooms.room_id"))
# #     tenant_id      = Column(Integer, ForeignKey("tenants.tenant_id"), nullable=True)
# #     start_date     = Column(DateTime)
# #     end_date       = Column(DateTime)
# #     amount         = Column(Float)
# #     payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.OVERDUE)
# #     created_at     = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
# #     updated_at     = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))

# #     room     = relationship("Room", back_populates="rent_cycles")
# #     payments = relationship("Payment", back_populates="rent_cycle")


# # class Payment(Base):
# #     __tablename__ = "payments"

# #     payment_id     = Column(Integer, primary_key=True, index=True)
# #     rent_cycle_id  = Column(Integer, ForeignKey("rent_cycles.rent_cycle_id"))
# #     tenant_id      = Column(Integer, ForeignKey("tenants.tenant_id"))
# #     amount         = Column(Float)
# #     payment_date   = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
# #     payment_method = Column(
# #         Enum(PaymentMethod,
# #              values_callable=lambda x: [e.value for e in x],
# #              create_constraint=True,
# #              native_enum=False),
# #         default=PaymentMethod.CASH,
# #     )
# #     period_start   = Column(Date, nullable=True)
# #     period_end     = Column(Date, nullable=True)
# #     receipt_number = Column(String)
# #     created_at     = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

# #     rent_cycle = relationship("RentCycle", back_populates="payments")
# #     tenant     = relationship("Tenant", back_populates="payments")


# # class Reminder(Base):
# #     __tablename__ = "reminders"

# #     reminder_id = Column(Integer, primary_key=True, index=True)
# #     tenant_id   = Column(Integer, ForeignKey("tenants.tenant_id"))
# #     message     = Column(String)
# #     medium      = Column(
# #         Enum(PaymentMethod,
# #              values_callable=lambda x: [e.value for e in x],
# #              create_constraint=True,
# #              native_enum=False),
# #         default=PaymentMethod.CASH,
# #     )
# #     sent_at    = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
# #     status     = Column(Enum(ReminderStatus), default=ReminderStatus.SENT)
# #     created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

# #     tenant = relationship("Tenant", back_populates="reminders")


# # class Report(Base):
# #     __tablename__ = "reports"

# #     report_id           = Column(Integer, primary_key=True, index=True)
# #     landlord_id         = Column(Integer, ForeignKey("landlords.landlord_id"))
# #     rent_cycle_id       = Column(Integer, ForeignKey("rent_cycles.rent_cycle_id"), nullable=True)
# #     start_date          = Column(Date)
# #     end_date            = Column(Date)
# #     total_expected_rent = Column(Float)
# #     total_paid          = Column(Float)
# #     total_outstanding   = Column(Float)
# #     net_income          = Column(Float)
# #     created_at          = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
# #     status              = Column(Enum(ReportStatus), default=ReportStatus.GENERATED)






























# # # from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum, ForeignKey, JSON, Date
# # # from sqlalchemy.orm import relationship
# # # from sqlalchemy.sql import text
# # # from .database import Base
# # # import enum

# # # class PaymentStatus(enum.Enum):
# # #     PAID = "Paid"
# # #     PARTIAL = "Partial"
# # #     OVERDUE = "Overdue"

# # # class PaymentMethod(enum.Enum):
# # #     CASH = "Cash"
# # #     MOBILE_MONEY = "Mobile Money"
# # #     BANK = "Bank"

# # # class ReminderStatus(enum.Enum):
# # #     SENT = "Sent"
# # #     FAILED = "Failed"

# # # class ReportStatus(enum.Enum):
# # #     PENDING = "Pending"
# # #     GENERATED = "Generated"

# # # class Landlord(Base):
# # #     __tablename__ = "landlords"
# # #     landlord_id = Column(Integer, primary_key=True, index=True)
# # #     email = Column(String, unique=True, index=True)
# # #     phone_number = Column(String)
# # #     password_hash = Column(String, nullable=True)
# # #     name = Column(String)
# # #     firebase_uid = Column(String(128), unique=True, nullable=True)
# # #     created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
# # #     updated_at = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))
# # #     settings = Column(JSON, default={"reminder_interval": "weekly"})
# # #     properties = relationship("Property", back_populates="landlord")

# # # class Property(Base):
# # #     __tablename__ = "properties"
# # #     property_id = Column(Integer, primary_key=True, index=True)
# # #     landlord_id = Column(Integer, ForeignKey("landlords.landlord_id"))
# # #     name = Column(String)
# # #     photo = Column(String, nullable=True)
# # #     created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
# # #     updated_at = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))
# # #     is_active = Column(Boolean, default=True)
# # #     landlord = relationship("Landlord", back_populates="properties")
# # #     rooms = relationship("Room", back_populates="property")

# # # class Room(Base):
# # #     __tablename__ = "rooms"
# # #     room_id = Column(Integer, primary_key=True, index=True)
# # #     property_id = Column(Integer, ForeignKey("properties.property_id"))
# # #     room_number = Column(String)
# # #     rent_amount = Column(Float)
# # #     due_date = Column(Integer)
# # #     payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.OVERDUE)
# # #     is_occupied = Column(Boolean, default=False)  # ← ADDED THIS
# # #     updated_at = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))
# # #     property = relationship("Property", back_populates="rooms")
# # #     tenants = relationship("Tenant", back_populates="assigned_room")
# # #     rent_cycles = relationship("RentCycle", back_populates="room")

# # # class Tenant(Base):
# # #     __tablename__ = "tenants"
# # #     tenant_id = Column(Integer, primary_key=True, index=True)
# # #     landlord_id = Column(Integer, ForeignKey("landlords.landlord_id"))  # ← ADDED THIS
# # #     full_name = Column(String)
# # #     phone_number = Column(String)
# # #     email = Column(String, nullable=True)
# # #     faculty = Column(String, nullable=True)
# # #     year_of_study = Column(String, nullable=True)
# # #     guardian_phone_number = Column(String, nullable=True)
# # #     guardian_name = Column(String, nullable=True)
# # #     guardian_location = Column(String, nullable=True)
# # #     photo = Column(String, nullable=True)
# # #     id_card_number = Column(String, nullable=True)
# # #     assigned_room_id = Column(Integer, ForeignKey("rooms.room_id"), nullable=True)
# # #     balance = Column(Float, default=0.0)
# # #     created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
# # #     updated_at = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))
# # #     is_active = Column(Boolean, default=True)
# # #     landlord = relationship("Landlord")  # ← ADDED THIS
# # #     assigned_room = relationship("Room", back_populates="tenants")
# # #     payments = relationship("Payment", back_populates="tenant")
# # #     reminders = relationship("Reminder", back_populates="tenant")

# # # class ArchivedTenant(Base):
# # #     __tablename__ = "archived_tenants"
# # #     archived_tenant_id = Column(Integer, primary_key=True, index=True)
# # #     original_tenant_id = Column(Integer)
# # #     landlord_id = Column(Integer, ForeignKey("landlords.landlord_id"))  # ← ADDED THIS
# # #     full_name = Column(String)
# # #     phone_number = Column(String)
# # #     email = Column(String, nullable=True)
# # #     room_number = Column(String, nullable=True)  # ← ADDED THIS
# # #     final_balance = Column(Float)  # ← CHANGED from 'balance'
# # #     archived_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

# # # class RentCycle(Base):
# # #     __tablename__ = "rent_cycles"
# # #     rent_cycle_id = Column(Integer, primary_key=True, index=True)
# # #     room_id = Column(Integer, ForeignKey("rooms.room_id"))
# # #     tenant_id = Column(Integer, ForeignKey("tenants.tenant_id"), nullable=True)
# # #     start_date = Column(DateTime)
# # #     end_date = Column(DateTime)
# # #     amount = Column(Float)
# # #     payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.OVERDUE)
# # #     created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
# # #     updated_at = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))
# # #     room = relationship("Room", back_populates="rent_cycles")
# # #     payments = relationship("Payment", back_populates="rent_cycle")

# # # class Payment(Base):
# # #     __tablename__ = "payments"
# # #     payment_id = Column(Integer, primary_key=True, index=True)
# # #     rent_cycle_id = Column(Integer, ForeignKey("rent_cycles.rent_cycle_id"))
# # #     tenant_id = Column(Integer, ForeignKey("tenants.tenant_id"))
# # #     amount = Column(Float)
# # #     payment_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
# # #     payment_method = Column(Enum(PaymentMethod, values_callable=lambda x: [e.value for e in x], create_constraint=True, native_enum=False), default=PaymentMethod.CASH)
# # #     period_start = Column(Date, nullable=True)
# # #     period_end = Column(Date, nullable=True)
# # #     receipt_number = Column(String)
# # #     created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
# # #     rent_cycle = relationship("RentCycle", back_populates="payments")
# # #     tenant = relationship("Tenant", back_populates="payments")

# # # class Reminder(Base):
# # #     __tablename__ = "reminders"
# # #     reminder_id = Column(Integer, primary_key=True, index=True)
# # #     tenant_id = Column(Integer, ForeignKey("tenants.tenant_id"))
# # #     message = Column(String)
# # #     medium = Column(Enum(PaymentMethod, values_callable=lambda x: [e.value for e in x], create_constraint=True, native_enum=False), default=PaymentMethod.CASH)
# # #     sent_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
# # #     status = Column(Enum(ReminderStatus), default=ReminderStatus.SENT)
# # #     created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
# # #     tenant = relationship("Tenant", back_populates="reminders")

# # # class Report(Base):
# # #     __tablename__ = "reports"
# # #     report_id = Column(Integer, primary_key=True, index=True)
# # #     landlord_id = Column(Integer, ForeignKey("landlords.landlord_id"))
# # #     rent_cycle_id = Column(Integer, ForeignKey("rent_cycles.rent_cycle_id"), nullable=True)
# # #     start_date = Column(Date)
# # #     end_date = Column(Date)
# # #     total_expected_rent = Column(Float)
# # #     total_paid = Column(Float)
# # #     total_outstanding = Column(Float)
# # #     net_income = Column(Float)
# # #     created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
# # #     status = Column(Enum(ReportStatus), default=ReportStatus.GENERATED)














