# app/utils/notifications.py
"""
FCM push notifications via Firebase Admin SDK.
Called from payment reminders, agreement signing, payment confirmation.
"""
import os
from firebase_admin import messaging
import firebase_admin


def send_push_notification(
    fcm_token: str,
    title: str,
    body: str,
    data: dict | None = None,
) -> bool:
    """
    Send a single FCM push notification.
    Returns True on success, False on failure (logs error, never raises).
    """
    if not fcm_token:
        return False

    try:
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data={k: str(v) for k, v in (data or {}).items()},
            token=fcm_token,
            android=messaging.AndroidConfig(
                priority="high",
                notification=messaging.AndroidNotification(
                    icon="ic_notification",
                    color="#1FBF75",
                    sound="default",
                ),
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(sound="default", badge=1)
                )
            ),
        )
        messaging.send(message)
        return True
    except Exception as e:
        print(f"[Propti FCM] Notification failed: {e}")
        return False


# ── Convenience wrappers ─────────────────────────────────────────────────────

def notify_payment_received(fcm_token: str, tenant_name: str, amount: int, balance: int):
    send_push_notification(
        fcm_token,
        title="Payment Received ✓",
        body=f"{tenant_name} paid {amount:,} FCFA. Remaining balance: {balance:,} FCFA.",
        data={"type": "payment_received"},
    )


def notify_rent_due(fcm_token: str, tenant_name: str, amount: int, due_day: int):
    send_push_notification(
        fcm_token,
        title="Rent Due Reminder",
        body=f"{tenant_name}'s rent of {amount:,} FCFA is due on the {due_day}.",
        data={"type": "rent_due"},
    )


def notify_overdue_rent(fcm_token: str, tenant_name: str, balance: int, days_late: int):
    send_push_notification(
        fcm_token,
        title=f"Overdue Rent — {days_late} Days",
        body=f"{tenant_name} owes {balance:,} FCFA and is {days_late} days late.",
        data={"type": "rent_overdue"},
    )


def notify_agreement_signed(fcm_token: str, tenant_name: str, unit: str):
    send_push_notification(
        fcm_token,
        title="Agreement Signed",
        body=f"{tenant_name} has signed the tenancy agreement for {unit}.",
        data={"type": "agreement_signed"},
    )


def notify_tenant_vacated(fcm_token: str, tenant_name: str, unit: str):
    send_push_notification(
        fcm_token,
        title="Tenant Vacated",
        body=f"{tenant_name} has been checked out of {unit}.",
        data={"type": "tenant_vacated"},
    )