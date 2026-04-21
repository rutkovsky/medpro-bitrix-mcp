import os
import httpx
from fastmcp import FastMCP
from starlette.responses import JSONResponse

WEBHOOK_URL = os.environ.get("BITRIX_WEBHOOK_URL", "").rstrip("/")

mcp = FastMCP("Bitrix24 MedPro MCP")


@mcp.tool()
def create_lead(name: str, phone: str = "", appointment_date: str = "", appointment_time: str = "") -> dict:
    """Create a lead card in Bitrix24 CRM for a patient appointment.
    Call right after bookAppointment succeeds.

    Args:
        name: Lead title, format 'Запись — <ФИО пациента> к <ФИО врача>'
        phone: Patient phone, example +79161234567
        appointment_date: Appointment date ISO YYYY-MM-DD, example 2026-04-24
        appointment_time: Appointment time HH:MM, example 11:00
    """
    fields = {"TITLE": name, "STATUS_ID": "NEW", "OPENED": "Y"}
    if phone:
        fields["PHONE"] = [{"VALUE": phone, "VALUE_TYPE": "MOBILE"}]
    comment_parts = []
    if appointment_date:
        comment_parts.append(f"Дата: {appointment_date}")
    if appointment_time:
        comment_parts.append(f"Время: {appointment_time}")
    if comment_parts:
        fields["COMMENTS"] = " | ".join(comment_parts)
    resp = httpx.post(
        f"{WEBHOOK_URL}/crm.lead.add.json",
        json={"fields": fields},
        timeout=15.0,
    )
    return resp.json()


@mcp.tool()
def create_contact(name: str, phone: str = "") -> dict:
    """Create a contact card in Bitrix24 CRM for a patient.
    Call right after bookAppointment succeeds, together with create_lead.

    Args:
        name: Full patient name order 'Фамилия Имя Отчество', example 'Иванов Иван Иванович'
        phone: Patient phone, example +79161234567
    """
    parts = name.strip().split()
    last_name = parts[0] if len(parts) >= 1 else ""
    first_name = parts[1] if len(parts) >= 2 else name
    second_name = parts[2] if len(parts) >= 3 else ""
    fields = {
        "NAME": first_name,
        "LAST_NAME": last_name,
        "SECOND_NAME": second_name,
        "OPENED": "Y",
    }
    if phone:
        fields["PHONE"] = [{"VALUE": phone, "VALUE_TYPE": "MOBILE"}]
    resp = httpx.post(
        f"{WEBHOOK_URL}/crm.contact.add.json",
        json={"fields": fields},
        timeout=15.0,
    )
    return resp.json()


@mcp.custom_route("/health", methods=["GET"])
async def health(request):
    return JSONResponse({"status": "ok"})


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000, path="/mcp")
