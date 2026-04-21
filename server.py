@mcp.tool()
def create_lead(name: str, phone: str = "", appointment_date: str = "", appointment_time: str = "") -> dict:
    """Put a lead card into Bitrix24 CRM. Parameters: name (lead title), phone (optional), appointment_date (YYYY-MM-DD), appointment_time (HH:MM)."""
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
    """Put a contact card into Bitrix24 CRM. Parameters: name (full patient name like 'Иванов Иван Иванович'), phone (optional)."""
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
