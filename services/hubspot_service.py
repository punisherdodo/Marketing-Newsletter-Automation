import os
from datetime import datetime

import requests


class HubSpotService:
    BASE_URL = "https://api.hubapi.com"

    def __init__(self):
        self.token = os.getenv("HUBSPOT_ACCESS_TOKEN")
        self._authenticated = None

    def is_configured(self) -> bool:
        return bool(self.token)

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def check_auth(self) -> dict:
        if not self.token:
            return {"ok": False, "reason": "HUBSPOT_ACCESS_TOKEN is not set."}
        try:
            url = f"{self.BASE_URL}/crm/v3/objects/contacts?limit=1"
            r = requests.get(url, headers=self._headers(), timeout=10)
            if r.status_code == 200:
                self._authenticated = True
                return {"ok": True}
            elif r.status_code == 401:
                self._authenticated = False
                return {"ok": False, "reason": "Invalid token. Check your HUBSPOT_ACCESS_TOKEN."}
            elif r.status_code == 403:
                self._authenticated = False
                return {"ok": False, "reason": "Access denied. Your token may lack required scopes."}
            else:
                self._authenticated = False
                return {"ok": False, "reason": f"HubSpot returned status {r.status_code}."}
        except requests.RequestException as e:
            self._authenticated = False
            return {"ok": False, "reason": f"Could not connect to HubSpot: {e}"}

    def _ensure_property(self, name: str, label: str) -> dict:
        url = f"{self.BASE_URL}/crm/v3/properties/contacts"
        payload = {
            "groupName": "contactinformation",
            "name": name,
            "label": label,
            "type": "string",
            "fieldType": "text",
        }
        try:
            r = requests.post(url, headers=self._headers(), json=payload, timeout=10)
            if r.status_code in (200, 201):
                return {"property": name, "status": "created"}
            elif r.status_code == 409:
                return {"property": name, "status": "already_exists"}
            else:
                return {"property": name, "status": "error", "detail": r.text[:200]}
        except requests.RequestException as e:
            return {"property": name, "status": "error", "detail": str(e)}

    def ensure_campaign_log_properties(self) -> list:
        props = [
            ("novamind_last_campaign_title", "NovaMind Last Campaign Title"),
            ("novamind_last_newsletter_variant", "NovaMind Last Newsletter Variant"),
            ("novamind_last_send_date", "NovaMind Last Send Date"),
        ]
        return [self._ensure_property(name, label) for name, label in props]

    def _get_contact(self, email: str):
        url = f"{self.BASE_URL}/crm/v3/objects/contacts/{email}?idProperty=email"
        return requests.get(url, headers=self._headers(), timeout=10)

    def _create_contact(self, properties: dict):
        url = f"{self.BASE_URL}/crm/v3/objects/contacts"
        return requests.post(url, headers=self._headers(), json={"properties": properties}, timeout=10)

    def _update_contact(self, email: str, properties: dict):
        url = f"{self.BASE_URL}/crm/v3/objects/contacts/{email}?idProperty=email"
        return requests.patch(url, headers=self._headers(), json={"properties": properties}, timeout=10)

    def upsert_contact(self, properties: dict) -> dict:
        email = properties["email"]
        try:
            check = self._get_contact(email)
            if check.status_code == 200:
                r = self._update_contact(email, properties)
                return {
                    "email": email,
                    "action": "updated",
                    "status_code": r.status_code,
                    "success": r.status_code in (200, 204),
                }
            r = self._create_contact(properties)
            return {
                "email": email,
                "action": "created",
                "status_code": r.status_code,
                "success": r.status_code in (200, 201),
            }
        except requests.RequestException as e:
            return {"email": email, "action": "error", "success": False, "detail": str(e)}

    def sync_contacts(self, contacts: list, campaign_title: str = "") -> list:
        if not self.is_configured():
            return []
        self.ensure_campaign_log_properties()
        results = []
        send_date = datetime.now().isoformat()
        for contact in contacts:
            properties = {
                "email": contact["email"],
                "firstname": contact.get("firstname", ""),
                "lastname": contact.get("lastname", ""),
                "company": contact.get("company", ""),
                "jobtitle": contact.get("job_title", ""),
                "hs_persona": contact.get("assigned_persona", ""),
                "novamind_last_campaign_title": campaign_title,
                "novamind_last_newsletter_variant": contact.get("assigned_persona", ""),
                "novamind_last_send_date": send_date,
            }
            result = self.upsert_contact(properties)
            result["assigned_persona"] = contact.get("assigned_persona", "")
            results.append(result)
        return results

    def dry_run(self, contacts: list) -> dict:
        valid = []
        invalid = []
        for c in contacts:
            if c.get("email") and "@" in c["email"] and c.get("firstname") and c.get("lastname"):
                valid.append(c)
            else:
                invalid.append(c)
        return {
            "total": len(contacts),
            "valid": len(valid),
            "invalid": len(invalid),
            "valid_contacts": valid,
            "invalid_contacts": invalid,
            "ready_to_sync": len(valid) > 0,
        }
