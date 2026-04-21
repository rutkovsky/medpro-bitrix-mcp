import os
import json
import httpx
from fastmcp import FastMCP
from starlette.responses import JSONResponse

WEBHOOK_URL = os.environ.get("BITRIX_WEBHOOK_URL", "").rstrip("/")

mcp = FastMCP("Bitrix24 MedPro MCP")


@mcp.tool()
def create_lead(name: str, phone: str = "", appointment_date: str = "", appointment_time: str = "") -> str:
    """Create a lead card in Bitrix24 CRM for a patient appointment.
    Call right after bookAppointment succeeds.

    Args:
        name: Lead title format 'Запись к <ФИО врача>'
        phone: Patient phone example +79161234567
        appointment_date: Appointment date ISO YYYY-MM-DD example 2026-04-24
        appointment_time: Appointment time HH:MM example 11:00
    """
    fields = {"TITLE": name, "STATUS_ID": "NEW", "OPENED": "Y"}
    if phone:
        fields["PHONE"] = [{"VALUE": phone, "VALUE_TYPE": "MOBILE"}]
    if appointment_date and appointment_time:
        fields["UF_CRM_1776790754"] = f"{appointment_date}T{appointment_time}:00"
    elif appointment_date:
        fields["UF_CRM_1776790754"] = f"{appointment_date}T00:00:00"
    try:
        resp = httpx.post(
            f"{WEBHOOK_URL}/crm.lead.add.json",
            json={"fields": fields},
            timeout=15.0,
        )
        data = resp.json()
        lead_id = data.get("result")
        if lead_id:
            return json.dumps({"ok": True, "lead_id": lead_id}, ensure_ascii=False)
        return json.dumps({"ok": False, "error": str(data.get("error_description", data))}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False)


@mcp.tool()
def create_contact(name: str, phone: str = "") -> str:
    """Create a contact card in Bitrix24 CRM for a patient.
    Call right after bookAppointment succeeds, together with create_lead.

    Args:
        name: Full patient name, example 'Иванов Иван Иванович'
        phone: Patient phone, example +79161234567
    """
    fields = {
        "NAME": name,
        "OPENED": "Y",
    }
    if phone:
        fields["PHONE"] = [{"VALUE": phone, "VALUE_TYPE": "MOBILE"}]
    try:
        resp = httpx.post(
            f"{WEBHOOK_URL}/crm.contact.add.json",
            json={"fields": fields},
            timeout=15.0,
        )
        data = resp.json()
        contact_id = data.get("result")
        if contact_id:
            return json.dumps({"ok": True, "contact_id": contact_id}, ensure_ascii=False)
        return json.dumps({"ok": False, "error": str(data.get("error_description", data))}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False)


@mcp.custom_route("/health", methods=["GET"])
async def health(request):
    return JSONResponse({"status": "ok"})


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000, path="/mcp")
