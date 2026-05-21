import os
from pathlib import Path
from datetime import datetime

import requests
from dotenv import load_dotenv

from services.persona_service import PersonaService


class HubSpotService:
    def __init__(self):
        root = Path(__file__).resolve().parent.parent
        load_dotenv(root / ".env", override=True)

        self.base_url = "https://api.hubapi.com"
        self.token = os.getenv("HUBSPOT_ACCESS_TOKEN")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        self.persona_service = PersonaService()

    def get_contact_by_email(self, email: str):
        url = f"{self.base_url}/crm/v3/objects/contacts/{email}?idProperty=email"
        return requests.get(url, headers=self.headers)

    def create_contact(self, properties: dict):
        url = f"{self.base_url}/crm/v3/objects/contacts"
        return requests.post(url, headers=self.headers, json={"properties": properties})

    def update_contact_by_email(self, email: str, properties: dict):
        url = f"{self.base_url}/crm/v3/objects/contacts/{email}?idProperty=email"
        return requests.patch(url, headers=self.headers, json={"properties": properties})

    def create_contact_property(self, name: str, label: str):
        url = f"{self.base_url}/crm/v3/properties/contacts"
        payload = {
            "groupName": "contactinformation",
            "name": name,
            "label": label,
            "type": "string",
            "fieldType": "text"
        }
        return requests.post(url, headers=self.headers, json=payload)

    def ensure_campaign_log_properties(self):
        props = [
            ("novamind_last_campaign_title", "NovaMind Last Campaign Title"),
            ("novamind_last_newsletter_variant", "NovaMind Last Newsletter Variant"),
            ("novamind_last_send_date", "NovaMind Last Send Date"),
        ]

        results = []
        for name, label in props:
            response = self.create_contact_property(name, label)
            results.append({
                "property": name,
                "status_code": response.status_code,
                "response_text": response.text[:300]
            })
        return results

    def upsert_contact_by_email(self, properties: dict):
        email = properties["email"]
        check_response = self.get_contact_by_email(email)

        if check_response.status_code == 200:
            update_response = self.update_contact_by_email(email, properties)
            return {
                "email": email,
                "persona": properties.get("hs_persona", "Unknown"),
                "action": "updated",
                "status_code": update_response.status_code,
                "response_text": update_response.text[:500]
            }

        create_response = self.create_contact(properties)
        return {
            "email": email,
            "persona": properties.get("hs_persona", "Unknown"),
            "action": "created",
            "status_code": create_response.status_code,
            "response_text": create_response.text[:500]
        }

    def create_sample_contacts(self):
        sample_contacts = [
            {
                "email": "founder.demo@novamind-test.com",
                "firstname": "Ava",
                "lastname": "Stone",
                "job_title": "Founder",
                "company": "BrightSpark Studio"
            },
            {
                "email": "ops.demo@novamind-test.com",
                "firstname": "Liam",
                "lastname": "Cole",
                "job_title": "Operations Manager",
                "company": "Northflow Creative"
            },
            {
                "email": "creative.demo@novamind-test.com",
                "firstname": "Maya",
                "lastname": "Reed",
                "job_title": "Creative Director",
                "company": "Pixel & Co"
            },
            {
                "email": "account.demo@novamind-test.com",
                "firstname": "Jordan",
                "lastname": "Blake",
                "job_title": "Account Director",
                "company": "Signal House"
            },
            {
                "email": "strategy.demo@novamind-test.com",
                "firstname": "Nina",
                "lastname": "Hart",
                "job_title": "Brand Strategist",
                "company": "Studio Current"
            }
        ]

        assigned_contacts = self.persona_service.assign_personas_to_contacts(sample_contacts)
        results = []

        for contact in assigned_contacts:
            properties = {
                "email": contact["email"],
                "firstname": contact["firstname"],
                "lastname": contact["lastname"],
                "company": contact["company"],
                "jobtitle": contact["job_title"],
                "hs_persona": contact["assigned_persona"]
            }

            sync_result = self.upsert_contact_by_email(properties)

            results.append({
                "email": contact["email"],
                "firstname": contact["firstname"],
                "lastname": contact["lastname"],
                "job_title": contact["job_title"],
                "company": contact["company"],
                "assigned_persona": contact["assigned_persona"],
                "crm_action": sync_result["action"],
                "crm_status_code": sync_result["status_code"]
            })

        return results

    def send_newsletters_to_segments(self, contacts: list, newsletters: dict, campaign_title: str):
        send_date = datetime.now().isoformat()
        results = []

        for contact in contacts:
            persona = contact["assigned_persona"]
            newsletter_body = newsletters.get(persona, "")

            send_payload = {
                "to": contact["email"],
                "persona": persona,
                "newsletter_variant": persona,
                "campaign_title": campaign_title,
                "send_date": send_date,
                "body_preview": newsletter_body[:120]
            }

            log_properties = {
                "novamind_last_campaign_title": campaign_title,
                "novamind_last_newsletter_variant": persona,
                "novamind_last_send_date": send_date
            }
            log_response = self.update_contact_by_email(contact["email"], log_properties)

            results.append({
                "email": contact["email"],
                "assigned_persona": persona,
                "newsletter_variant": persona,
                "send_status": "simulated_sent",
                "crm_log_status_code": log_response.status_code,
                "send_payload_preview": str(send_payload)
            })

        return results
