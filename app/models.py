from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum, ForeignKey, JSON, Date
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

class Landlord(Base):
    __tablename__ = "landlords"
    landlord_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String)
    password_hash = Column(String, nullable=True)
    name = Column(String)
    firebase_uid = Column(String(128), unique=True, nullable=True)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))
    settings = Column(JSON, default={"reminder_interval": "weekly"})
    properties = relationship("Property", back_populates="landlord")

class Property(Base):
    __tablename__ = "properties"
    property_id = Column(Integer, primary_key=True, index=True)
    landlord_id = Column(Integer, ForeignKey("landlords.landlord_id"))
    name = Column(String)
    photo = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))
    is_active = Column(Boolean, default=True)
    landlord = relationship("Landlord", back_populates="properties")
    rooms = relationship("Room", back_populates="property")

class Room(Base):
    __tablename__ = "rooms"
    room_id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.property_id"))
    room_number = Column(String)
    rent_amount = Column(Float)
    due_date = Column(Integer)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.OVERDUE)
    is_occupied = Column(Boolean, default=False)  # ← ADDED THIS
    updated_at = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))
    property = relationship("Property", back_populates="rooms")
    tenants = relationship("Tenant", back_populates="assigned_room")
    rent_cycles = relationship("RentCycle", back_populates="room")

class Tenant(Base):
    __tablename__ = "tenants"
    tenant_id = Column(Integer, primary_key=True, index=True)
    landlord_id = Column(Integer, ForeignKey("landlords.landlord_id"))  # ← ADDED THIS
    full_name = Column(String)
    phone_number = Column(String)
    email = Column(String, nullable=True)
    faculty = Column(String, nullable=True)
    year_of_study = Column(String, nullable=True)
    guardian_phone_number = Column(String, nullable=True)
    guardian_name = Column(String, nullable=True)
    guardian_location = Column(String, nullable=True)
    photo = Column(String, nullable=True)
    id_card_number = Column(String, nullable=True)
    assigned_room_id = Column(Integer, ForeignKey("rooms.room_id"), nullable=True)
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))
    is_active = Column(Boolean, default=True)
    landlord = relationship("Landlord")  # ← ADDED THIS
    assigned_room = relationship("Room", back_populates="tenants")
    payments = relationship("Payment", back_populates="tenant")
    reminders = relationship("Reminder", back_populates="tenant")

class ArchivedTenant(Base):
    __tablename__ = "archived_tenants"
    archived_tenant_id = Column(Integer, primary_key=True, index=True)
    original_tenant_id = Column(Integer)
    landlord_id = Column(Integer, ForeignKey("landlords.landlord_id"))  # ← ADDED THIS
    full_name = Column(String)
    phone_number = Column(String)
    email = Column(String, nullable=True)
    room_number = Column(String, nullable=True)  # ← ADDED THIS
    final_balance = Column(Float)  # ← CHANGED from 'balance'
    archived_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

class RentCycle(Base):
    __tablename__ = "rent_cycles"
    rent_cycle_id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.room_id"))
    tenant_id = Column(Integer, ForeignKey("tenants.tenant_id"), nullable=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    amount = Column(Float)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.OVERDUE)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))
    room = relationship("Room", back_populates="rent_cycles")
    payments = relationship("Payment", back_populates="rent_cycle")

class Payment(Base):
    __tablename__ = "payments"
    payment_id = Column(Integer, primary_key=True, index=True)
    rent_cycle_id = Column(Integer, ForeignKey("rent_cycles.rent_cycle_id"))
    tenant_id = Column(Integer, ForeignKey("tenants.tenant_id"))
    amount = Column(Float)
    payment_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    payment_method = Column(Enum(PaymentMethod, values_callable=lambda x: [e.value for e in x], create_constraint=True, native_enum=False), default=PaymentMethod.CASH)
    period_start = Column(Date, nullable=True)
    period_end = Column(Date, nullable=True)
    receipt_number = Column(String)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    rent_cycle = relationship("RentCycle", back_populates="payments")
    tenant = relationship("Tenant", back_populates="payments")

class Reminder(Base):
    __tablename__ = "reminders"
    reminder_id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.tenant_id"))
    message = Column(String)
    medium = Column(Enum(PaymentMethod, values_callable=lambda x: [e.value for e in x], create_constraint=True, native_enum=False), default=PaymentMethod.CASH)
    sent_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    status = Column(Enum(ReminderStatus), default=ReminderStatus.SENT)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    tenant = relationship("Tenant", back_populates="reminders")

class Report(Base):
    __tablename__ = "reports"
    report_id = Column(Integer, primary_key=True, index=True)
    landlord_id = Column(Integer, ForeignKey("landlords.landlord_id"))
    rent_cycle_id = Column(Integer, ForeignKey("rent_cycles.rent_cycle_id"), nullable=True)
    start_date = Column(Date)
    end_date = Column(Date)
    total_expected_rent = Column(Float)
    total_paid = Column(Float)
    total_outstanding = Column(Float)
    net_income = Column(Float)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    status = Column(Enum(ReportStatus), default=ReportStatus.GENERATED)

















# from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum, ForeignKey, JSON, Date
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
# class Landlord(Base):
#     __tablename__ = "landlords"
#     landlord_id = Column(Integer, primary_key=True, index=True)
#     email = Column(String, unique=True, index=True)
#     phone_number = Column(String)
#     password_hash = Column(String, nullable=True)  # ← ADD nullable=True
#     name = Column(String)
#     firebase_uid = Column(String(128), unique=True, nullable=True)  # ← ADD THIS ENTIRE LINE
#     created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
#     updated_at = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))
#     settings = Column(JSON, default={"reminder_interval": "weekly"})
#     properties = relationship("Property", back_populates="landlord")

# class Property(Base):
#     __tablename__ = "properties"
#     property_id = Column(Integer, primary_key=True, index=True)
#     landlord_id = Column(Integer, ForeignKey("landlords.landlord_id"))
#     name = Column(String)
#     photo = Column(String, nullable=True)
#     created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
#     updated_at = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))
#     is_active = Column(Boolean, default=True)
#     landlord = relationship("Landlord", back_populates="properties")
#     rooms = relationship("Room", back_populates="property")

# class Room(Base):
#     __tablename__ = "rooms"
#     room_id = Column(Integer, primary_key=True, index=True)
#     property_id = Column(Integer, ForeignKey("properties.property_id"))
#     room_number = Column(String)
#     rent_amount = Column(Float)
#     due_date = Column(Integer)
#     payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.OVERDUE)
#     updated_at = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))
#     property = relationship("Property", back_populates="rooms")
#     tenants = relationship("Tenant", back_populates="assigned_room")
#     rent_cycles = relationship("RentCycle", back_populates="room")

# class Tenant(Base):
#     __tablename__ = "tenants"
#     tenant_id = Column(Integer, primary_key=True, index=True)
#     landlord_id = Column(Integer, ForeignKey("landlords.landlord_id"))  # ← ADD THIS LINE
#     full_name = Column(String)
#     phone_number = Column(String)
#     email = Column(String, nullable=True)
#     faculty = Column(String, nullable=True)
#     year_of_study = Column(String, nullable=True)
#     guardian_phone_number = Column(String, nullable=True)
#     guardian_name = Column(String, nullable=True)
#     guardian_location = Column(String, nullable=True)
#     photo = Column(String, nullable=True)
#     id_card_number = Column(String, nullable=True)
#     assigned_room_id = Column(Integer, ForeignKey("rooms.room_id"), nullable=True)
#     balance = Column(Float, default=0.0)
#     created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
#     updated_at = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))
#     is_active = Column(Boolean, default=True)
#     landlord = relationship("Landlord")  # ← ADD THIS LINE
#     assigned_room = relationship("Room", back_populates="tenants")
#     payments = relationship("Payment", back_populates="tenant")
#     reminders = relationship("Reminder", back_populates="tenant")    

# # class Tenant(Base):
# #     __tablename__ = "tenants"
# #     tenant_id = Column(Integer, primary_key=True, index=True)
# #     full_name = Column(String)
# #     phone_number = Column(String)
# #     email = Column(String, nullable=True)
# #     faculty = Column(String, nullable=True)
# #     year_of_study = Column(String, nullable=True)
# #     guardian_phone_number = Column(String, nullable=True)
# #     guardian_name = Column(String, nullable=True)
# #     guardian_location = Column(String, nullable=True)
# #     photo = Column(String, nullable=True)
# #     id_card_number = Column(String, nullable=True)
# #     assigned_room_id = Column(Integer, ForeignKey("rooms.room_id"), nullable=True)
# #     balance = Column(Float, default=0.0)
# #     created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
# #     updated_at = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))
# #     is_active = Column(Boolean, default=True)
# #     assigned_room = relationship("Room", back_populates="tenants")
# #     payments = relationship("Payment", back_populates="tenant")
# #     reminders = relationship("Reminder", back_populates="tenant")

# class ArchivedTenant(Base):
#     __tablename__ = "archived_tenants"
#     archived_tenant_id = Column(Integer, primary_key=True, index=True)
#     original_tenant_id = Column(Integer)
#     full_name = Column(String)
#     phone_number = Column(String)
#     email = Column(String, nullable=True)
#     balance = Column(Float)
#     archived_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

# class RentCycle(Base):
#     __tablename__ = "rent_cycles"
#     rent_cycle_id = Column(Integer, primary_key=True, index=True)
#     room_id = Column(Integer, ForeignKey("rooms.room_id"))
#     tenant_id = Column(Integer, ForeignKey("tenants.tenant_id"), nullable=True)
#     start_date = Column(DateTime)
#     end_date = Column(DateTime)
#     amount = Column(Float)
#     payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.OVERDUE)
#     created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
#     updated_at = Column(DateTime, onupdate=text("CURRENT_TIMESTAMP"))
#     room = relationship("Room", back_populates="rent_cycles")
#     payments = relationship("Payment", back_populates="rent_cycle")

# class Payment(Base):
#     __tablename__ = "payments"
#     payment_id = Column(Integer, primary_key=True, index=True)
#     rent_cycle_id = Column(Integer, ForeignKey("rent_cycles.rent_cycle_id"))
#     tenant_id = Column(Integer, ForeignKey("tenants.tenant_id"))
#     amount = Column(Float)
#     payment_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
#     payment_method = Column(Enum(PaymentMethod, values_callable=lambda x: [e.value for e in x], create_constraint=True, native_enum=False), default=PaymentMethod.CASH)
#     period_start = Column(Date, nullable=True)
#     period_end = Column(Date, nullable=True)
#     receipt_number = Column(String)
#     created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
#     rent_cycle = relationship("RentCycle", back_populates="payments")
#     tenant = relationship("Tenant", back_populates="payments")
    

# class Reminder(Base):
#     __tablename__ = "reminders"
#     reminder_id = Column(Integer, primary_key=True, index=True)
#     tenant_id = Column(Integer, ForeignKey("tenants.tenant_id"))
#     message = Column(String)
#     medium = Column(Enum(PaymentMethod, values_callable=lambda x: [e.value for e in x], create_constraint=True, native_enum=False), default=PaymentMethod.CASH)
#     sent_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
#     status = Column(Enum(ReminderStatus), default=ReminderStatus.SENT)
#     created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
#     tenant = relationship("Tenant", back_populates="reminders")

# class Report(Base):
#     __tablename__ = "reports"
#     report_id = Column(Integer, primary_key=True, index=True)
#     landlord_id = Column(Integer, ForeignKey("landlords.landlord_id"))
#     rent_cycle_id = Column(Integer, ForeignKey("rent_cycles.rent_cycle_id"), nullable=True)
#     start_date = Column(Date)
#     end_date = Column(Date)
#     total_expected_rent = Column(Float)
#     total_paid = Column(Float)
#     total_outstanding = Column(Float)
#     net_income = Column(Float)
#     created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
#     status = Column(Enum(ReportStatus), default=ReportStatus.GENERATED)








