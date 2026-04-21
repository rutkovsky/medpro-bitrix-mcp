import os
import httpx
from fastmcp import FastMCP

WEBHOOK_URL = os.environ.get("BITRIX_WEBHOOK_URL", "").rstrip("/")

mcp = FastMCP("Bitrix24 MedPro MCP")


@mcp.tool()
def create_lead(name: str, phone: str = "", comment: str = "") -> dict:
    """Put a lead card into Bitrix24 CRM. Parameters: name (lead title), phone (optional), comment (optional)."""
    fields = {"TITLE": name, "STATUS_ID": "NEW", "OPENED": "Y"}
    if phone:
        fields["PHONE"] = [{"VALUE": phone, "VALUE_TYPE": "MOBILE"}]
    if comment:
        fields["COMMENTS"] = comment
    resp = httpx.post(
        f"{WEBHOOK_URL}/crm.lead.add.json",
        json={"fields": fields},
        timeout=15.0,
    )
    return resp.json()


@mcp.tool()
def create_contact(name: str, phone: str = "") -> dict:
    """Put a contact card into Bitrix24 CRM. Parameters: name (full name), phone (optional)."""
    fields = {"NAME": name, "OPENED": "Y"}
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
    from starlette.responses import JSONResponse
    return JSONResponse({"status": "ok"})


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000, path="/mcp")
