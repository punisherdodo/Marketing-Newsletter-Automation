import os
from datetime import datetime

import requests


class EmailService:
    SENDGRID_URL = "https://api.sendgrid.com/v3/mail/send"

    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("SENDGRID_FROM_EMAIL", "")
        self.from_name = os.getenv("SENDGRID_FROM_NAME", "NovaMind")

    def is_configured(self) -> bool:
        return bool(self.api_key and self.from_email)

    def check_auth(self) -> dict:
        if not self.api_key:
            return {"ok": False, "reason": "SENDGRID_API_KEY is not set."}
        if not self.from_email:
            return {"ok": False, "reason": "SENDGRID_FROM_EMAIL is not set. Add your verified sender email."}
        try:
            url = "https://api.sendgrid.com/v3/user/profile"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                return {"ok": True}
            elif r.status_code == 401:
                return {"ok": False, "reason": "Invalid SendGrid API key. Check SENDGRID_API_KEY."}
            elif r.status_code == 403:
                return {"ok": False, "reason": "Access denied. Your key may have insufficient permissions."}
            else:
                return {"ok": False, "reason": f"SendGrid returned status {r.status_code}."}
        except requests.RequestException as e:
            return {"ok": False, "reason": f"Could not connect to SendGrid: {e}"}

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def send_email(self, to_email: str, to_name: str, subject: str, body: str) -> dict:
        if not self.is_configured():
            return {"ok": False, "email": to_email, "reason": "SendGrid not configured"}
        payload = {
            "personalizations": [{"to": [{"email": to_email.strip(), "name": to_name}]}],
            "from": {"email": self.from_email, "name": self.from_name},
            "subject": subject,
            "content": [{"type": "text/plain", "value": body}],
        }
        try:
            r = requests.post(self.SENDGRID_URL, headers=self._headers(), json=payload, timeout=15)
            if r.status_code == 202:
                return {"ok": True, "email": to_email, "action": "sent"}
            else:
                reason = r.json().get("errors", [{}])[0].get("message", r.text[:200]) if r.text else f"HTTP {r.status_code}"
                return {"ok": False, "email": to_email, "reason": reason}
        except requests.RequestException as e:
            return {"ok": False, "email": to_email, "reason": str(e)}

    def send_campaign(self, contacts: list, newsletters: dict, subject_lines: dict,
                      campaign_title: str, use_newsletters: bool = True) -> list:
        results = []
        content_map = newsletters
        for contact in contacts:
            persona = contact.get("assigned_persona", "")
            subject = subject_lines.get(persona, campaign_title)
            body = content_map.get(persona, "")
            if not body:
                results.append({
                    "email": contact["email"], "persona": persona,
                    "ok": False, "reason": "No content for this persona",
                })
                continue
            name = f"{contact.get('firstname', '')} {contact.get('lastname', '')}".strip()
            result = self.send_email(contact["email"], name, subject, body)
            result["persona"] = persona
            result["subject"] = subject
            result["sent_at"] = datetime.now().isoformat()
            results.append(result)
        return results

    def dry_run(self, contacts: list, newsletters: dict, subject_lines: dict) -> dict:
        preview = []
        missing_content = []
        for c in contacts:
            persona = c.get("assigned_persona", "")
            body = newsletters.get(persona, "")
            subject = subject_lines.get(persona, "No subject")
            if body:
                preview.append({
                    "email": c["email"],
                    "name": f"{c.get('firstname', '')} {c.get('lastname', '')}".strip(),
                    "persona": persona,
                    "subject": subject,
                    "body_preview": body[:120] + "..." if len(body) > 120 else body,
                })
            else:
                missing_content.append(c["email"])
        return {
            "total": len(contacts),
            "will_send": len(preview),
            "missing_content": len(missing_content),
            "preview": preview,
            "missing_list": missing_content,
        }

    def mock_send(self, contacts: list, newsletters: dict, subject_lines: dict,
                  campaign_title: str) -> list:
        return [
            {
                "email": c["email"],
                "persona": c.get("assigned_persona", ""),
                "subject": subject_lines.get(c.get("assigned_persona", ""), campaign_title),
                "ok": True,
                "action": "simulated",
                "sent_at": datetime.now().isoformat(),
            }
            for c in contacts
        ]
