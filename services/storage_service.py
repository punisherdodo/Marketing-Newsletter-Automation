import json
import sqlite3
from datetime import datetime
from pathlib import Path


class StorageService:
    def __init__(self):
        root = Path(__file__).resolve().parent.parent
        db_dir = root / "data"
        db_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir = root / "data" / "exports"
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = db_dir / "novamind.db"
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        c = self.conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            name TEXT,
            topic TEXT,
            mode TEXT,
            blog_title TEXT,
            blog_outline TEXT,
            blog_draft TEXT,
            newsletters TEXT,
            subject_lines TEXT,
            channels TEXT
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER,
            email TEXT,
            firstname TEXT,
            lastname TEXT,
            company TEXT,
            job_title TEXT,
            assigned_persona TEXT,
            sync_status TEXT,
            FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS performance_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER,
            persona TEXT,
            send_date TEXT,
            open_rate REAL,
            click_rate REAL,
            unsubscribe_rate REAL,
            subject_line_style TEXT,
            content_angle TEXT,
            cta_type TEXT,
            weighted_score REAL,
            FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS content_revisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER,
            revision_type TEXT,
            content TEXT,
            saved_at TEXT,
            FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS custom_keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            persona TEXT NOT NULL,
            keyword TEXT NOT NULL,
            UNIQUE(persona, keyword)
        )""")
        self.conn.commit()

    def insert_campaign(self, topic: str, data: dict, mode: str = "mock",
                        name: str = "", channels: list = None) -> int:
        c = self.conn.cursor()
        c.execute("""
        INSERT INTO campaigns (created_at, name, topic, mode, blog_title, blog_outline,
            blog_draft, newsletters, subject_lines, channels)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
            datetime.now().isoformat(),
            name,
            topic,
            mode,
            data.get("blog_title", ""),
            json.dumps(data.get("blog_outline", [])),
            data.get("blog_draft", ""),
            json.dumps(data.get("newsletters", {})),
            json.dumps(data.get("subject_lines", {})),
            json.dumps(channels or []),
        ))
        self.conn.commit()
        return c.lastrowid

    def save_campaign_json(self, data: dict, campaign_name: str = "") -> Path:
        safe_name = (campaign_name or "campaign").replace(" ", "_")[:30]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.exports_dir / f"{safe_name}_{timestamp}.json"
        export_data = {k: v for k, v in data.items() if k not in ("api_key", "token")}
        with open(filename, "w") as f:
            json.dump(export_data, f, indent=2)
        return filename

    def insert_contacts(self, campaign_id: int, contacts: list):
        c = self.conn.cursor()
        for contact in contacts:
            c.execute("""
            INSERT INTO contacts (campaign_id, email, firstname, lastname, company,
                job_title, assigned_persona, sync_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (
                campaign_id,
                contact.get("email", ""),
                contact.get("firstname", ""),
                contact.get("lastname", ""),
                contact.get("company", ""),
                contact.get("job_title", ""),
                contact.get("assigned_persona", ""),
                contact.get("sync_status", "not_synced"),
            ))
        self.conn.commit()

    def insert_performance_metric(self, row: dict):
        c = self.conn.cursor()
        c.execute("""
        INSERT INTO performance_metrics (campaign_id, persona, send_date, open_rate,
            click_rate, unsubscribe_rate, subject_line_style, content_angle, cta_type, weighted_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
            row["campaign_id"], row["persona"], row.get("send_date", ""),
            row["open_rate"], row["click_rate"], row["unsubscribe_rate"],
            row.get("subject_line_style", ""), row.get("content_angle", ""),
            row.get("cta_type", ""), row.get("weighted_score", 0),
        ))
        self.conn.commit()

    def save_revision(self, campaign_id: int, revision_type: str, content: str):
        c = self.conn.cursor()
        c.execute("""
        INSERT INTO content_revisions (campaign_id, revision_type, content, saved_at)
        VALUES (?, ?, ?, ?)""", (campaign_id, revision_type, content, datetime.now().isoformat()))
        self.conn.commit()

    def save_manual_metrics(self, campaign_id: int, persona: str,
                             open_rate: float, click_rate: float, unsubscribe_rate: float):
        weighted_score = round(0.3 * open_rate + 0.6 * click_rate - 0.1 * unsubscribe_rate, 4)
        self.insert_performance_metric({
            "campaign_id": campaign_id, "persona": persona,
            "send_date": datetime.now().isoformat(), "open_rate": open_rate,
            "click_rate": click_rate, "unsubscribe_rate": unsubscribe_rate,
            "subject_line_style": "manual-entry", "content_angle": "manual-entry",
            "cta_type": "manual-entry", "weighted_score": weighted_score,
        })

    def get_campaigns(self) -> list:
        c = self.conn.cursor()
        c.execute("SELECT id, created_at, name, topic, mode, blog_title FROM campaigns ORDER BY id DESC")
        rows = c.fetchall()
        return [{"id": r[0], "created_at": r[1], "name": r[2], "topic": r[3],
                 "mode": r[4], "blog_title": r[5]} for r in rows]

    def get_campaign(self, campaign_id: int) -> dict:
        c = self.conn.cursor()
        c.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,))
        row = c.fetchone()
        if not row:
            return {}
        keys = ["id", "created_at", "name", "topic", "mode", "blog_title",
                "blog_outline", "blog_draft", "newsletters", "subject_lines", "channels"]
        d = dict(zip(keys, row))
        for field in ["blog_outline", "newsletters", "subject_lines", "channels"]:
            try:
                d[field] = json.loads(d[field]) if d[field] else {}
            except Exception:
                d[field] = {}
        return d

    def get_contacts_for_campaign(self, campaign_id: int) -> list:
        c = self.conn.cursor()
        c.execute("SELECT * FROM contacts WHERE campaign_id = ? ORDER BY id", (campaign_id,))
        rows = c.fetchall()
        keys = ["id", "campaign_id", "email", "firstname", "lastname",
                "company", "job_title", "assigned_persona", "sync_status"]
        return [dict(zip(keys, r)) for r in rows]

    def get_metrics_for_campaign(self, campaign_id: int) -> list:
        c = self.conn.cursor()
        c.execute("""SELECT campaign_id, persona, send_date, open_rate, click_rate,
            unsubscribe_rate, subject_line_style, content_angle, cta_type, weighted_score
            FROM performance_metrics WHERE campaign_id = ? ORDER BY id""", (campaign_id,))
        rows = c.fetchall()
        keys = ["campaign_id", "persona", "send_date", "open_rate", "click_rate",
                "unsubscribe_rate", "subject_line_style", "content_angle", "cta_type", "weighted_score"]
        return [dict(zip(keys, r)) for r in rows]

    def get_all_metrics_history(self) -> list:
        c = self.conn.cursor()
        c.execute("""SELECT campaign_id, persona, send_date, open_rate, click_rate,
            unsubscribe_rate, subject_line_style, content_angle, cta_type, weighted_score
            FROM performance_metrics ORDER BY campaign_id ASC, persona ASC""")
        rows = c.fetchall()
        keys = ["campaign_id", "persona", "send_date", "open_rate", "click_rate",
                "unsubscribe_rate", "subject_line_style", "content_angle", "cta_type", "weighted_score"]
        return [dict(zip(keys, r)) for r in rows]

    def clear_database(self):
        c = self.conn.cursor()
        for table in ["content_revisions", "performance_metrics", "contacts", "campaigns"]:
            c.execute(f"DELETE FROM {table}")
        self.conn.commit()

    def clear_exports(self) -> int:
        count = 0
        for f in self.exports_dir.glob("*.json"):
            f.unlink()
            count += 1
        return count

    def list_exports(self) -> list:
        return sorted(self.exports_dir.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)

    def load_custom_keywords(self) -> dict:
        c = self.conn.cursor()
        c.execute("SELECT persona, keyword FROM custom_keywords ORDER BY persona, keyword")
        rows = c.fetchall()
        result = {}
        for persona, keyword in rows:
            result.setdefault(persona, []).append(keyword)
        return result

    def save_custom_keyword(self, persona: str, keyword: str):
        c = self.conn.cursor()
        c.execute("INSERT OR IGNORE INTO custom_keywords (persona, keyword) VALUES (?, ?)",
                  (persona, keyword.strip().lower()))
        self.conn.commit()

    def delete_custom_keywords(self, persona: str):
        c = self.conn.cursor()
        c.execute("DELETE FROM custom_keywords WHERE persona = ?", (persona,))
        self.conn.commit()

    def get_analytics_summary(self) -> dict:
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM campaigns")
        total_campaigns = c.fetchone()[0]
        c.execute("SELECT COUNT(DISTINCT email) FROM contacts")
        total_contacts = c.fetchone()[0]
        c.execute("SELECT assigned_persona, COUNT(*) FROM contacts GROUP BY assigned_persona ORDER BY COUNT(*) DESC")
        persona_dist = dict(c.fetchall())
        c.execute("SELECT mode, COUNT(*) FROM campaigns GROUP BY mode")
        mode_dist = dict(c.fetchall())
        c.execute("SELECT COUNT(*) FROM contacts WHERE sync_status = 'synced'")
        synced = c.fetchone()[0]
        return {
            "total_campaigns": total_campaigns,
            "total_contacts": total_contacts,
            "persona_distribution": persona_dist,
            "mode_distribution": mode_dist,
            "synced_contacts": synced,
        }
