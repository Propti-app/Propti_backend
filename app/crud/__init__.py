# app/crud/__init__.py
from .landlord import create_landlord, update_landlord_settings, get_landlord_settings
from .property import create_property
from .room import create_room, get_rooms, update_room
from .tenant import (
    create_tenant, 
    assign_tenant_to_room, 
    deactivate_tenant, 
    vacate_and_archive_tenant,
    get_tenant,           # NEW
    get_tenants,          # NEW
    update_tenant,        # NEW
    get_archived_tenants  # NEW
)
from .rent_cycle import create_rent_cycle, get_rent_cycles
from .payment import create_payment, get_payment_history
from .reminder import create_reminder, schedule_reminders
from .report import create_report, get_dashboard



# # app/crud/__init__.py
# from .landlord import create_landlord, update_landlord_settings, get_landlord_settings
# from .property import create_property
# from .room import create_room, get_rooms, update_room
# from .tenant import (
#     create_tenant, 
#     assign_tenant_to_room, 
#     deactivate_tenant, 
#     vacate_and_archive_tenant,
#     get_tenant,           # NEW
#     get_tenants,          # NEW
#     update_tenant,        # NEW
#     get_archived_tenants  # NEW
# )
# from .rent_cycle import create_rent_cycle, get_rent_cycles
# from .payment import create_payment, get_payment_history
# from .reminder import create_reminder, schedule_reminders
# from .report import create_report, get_dashboard




# # app/crud/__init__.py
# from .landlord import create_landlord, update_landlord_settings, get_landlord_settings
# from .property import create_property
# from .room import create_room, get_rooms, update_room
# from .tenant import (
#     create_tenant, 
#     assign_tenant_to_room, 
#     deactivate_tenant, 
#     vacate_and_archive_tenant,
#     get_tenant,           # NEW
#     get_tenants,          # NEW
#     update_tenant,        # NEW
#     get_archived_tenants  # NEW
# )
# from .rent_cycle import create_rent_cycle, get_rent_cycles
# from .payment import create_payment, get_payment_history
# from .reminder import create_reminder, schedule_reminders
# from .report import create_report, get_dashboard




# # from .landlord import create_landlord, update_landlord_settings, get_landlord_settings
# # from .property import create_property
# # from .room import create_room, get_rooms, update_room
# # from .tenant import create_tenant, assign_tenant_to_room, deactivate_tenant, vacate_and_archive_tenant
# # from .rent_cycle import create_rent_cycle, get_rent_cycles
# # from .payment import create_payment, get_payment_history
# # from .reminder import create_reminder, schedule_reminders
# # from .report import create_report, get_dashboard






































# # # from .landlord import create_landlord
# # # from .property import create_property
# # # from .room import create_room, get_rooms, update_room
# # # from .tenant import create_tenant, assign_tenant_to_room, deactivate_tenant, vacate_and_archive_tenant
# # # from .rent_cycle import create_rent_cycle, get_rent_cycles
# # # from .payment import create_payment



# # # from .landlord import create_landlord
# # # from .property import create_property
# # # from .room import create_room, get_rooms, update_room
# # # from .tenant import create_tenant, assign_tenant_to_room, deactivate_tenant, vacate_and_archive_tenant



# # # from .landlord import create_landlord
# # # from .property import create_property