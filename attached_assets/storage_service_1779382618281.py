import json
import sqlite3
from datetime import datetime
from pathlib import Path


class StorageService:
    def __init__(self):
        root = Path(__file__).resolve().parent.parent
        self.db_path = root / "data" / "novamind.db"
        self.exports_dir = root / "data" / "exports"
        self.exports_dir.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            topic TEXT,
            blog_title TEXT,
            blog_outline TEXT,
            blog_draft TEXT,
            founder_newsletter TEXT,
            ops_newsletter TEXT,
            creative_newsletter TEXT
        )
        """)

        self.cursor.execute("""
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
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS content_revisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER,
            revision_type TEXT,
            content TEXT,
            saved_at TEXT,
            FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
        )
        """)

        self.conn.commit()

    def save_campaign_json(self, data: dict):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.exports_dir / f"campaign_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        return filename

    def insert_campaign(self, topic: str, data: dict):
        founder = data["newsletters"].get("Agency Founder", "")
        ops = data["newsletters"].get("Operations Manager", "")
        creative = data["newsletters"].get("Creative Lead", "")

        self.cursor.execute("""
        INSERT INTO campaigns (
            created_at, topic, blog_title, blog_outline, blog_draft,
            founder_newsletter, ops_newsletter, creative_newsletter
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            topic,
            data["blog_title"],
            json.dumps(data["blog_outline"]),
            data["blog_draft"],
            founder,
            ops,
            creative
        ))

        self.conn.commit()
        return self.cursor.lastrowid

    def insert_performance_metric(self, row: dict):
        self.cursor.execute("""
        INSERT INTO performance_metrics (
            campaign_id, persona, send_date, open_rate, click_rate, unsubscribe_rate,
            subject_line_style, content_angle, cta_type, weighted_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["campaign_id"],
            row["persona"],
            row["send_date"],
            row["open_rate"],
            row["click_rate"],
            row["unsubscribe_rate"],
            row["subject_line_style"],
            row["content_angle"],
            row["cta_type"],
            row["weighted_score"]
        ))
        self.conn.commit()

    def save_manual_metrics(self, campaign_id: int, persona: str, open_rate: float, click_rate: float, unsubscribe_rate: float):
        weighted_score = round(
            0.3 * open_rate +
            0.6 * click_rate -
            0.1 * unsubscribe_rate,
            4
        )

        self.cursor.execute("""
        INSERT INTO performance_metrics (
            campaign_id, persona, send_date, open_rate, click_rate, unsubscribe_rate,
            subject_line_style, content_angle, cta_type, weighted_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            campaign_id,
            persona,
            datetime.now().isoformat(),
            open_rate,
            click_rate,
            unsubscribe_rate,
            "manual-entry",
            "manual-entry",
            "manual-entry",
            weighted_score
        ))
        self.conn.commit()

    def save_revision(self, campaign_id: int, revision_type: str, content: str):
        self.cursor.execute("""
        INSERT INTO content_revisions (
            campaign_id, revision_type, content, saved_at
        ) VALUES (?, ?, ?, ?)
        """, (
            campaign_id,
            revision_type,
            content,
            datetime.now().isoformat()
        ))
        self.conn.commit()

    def get_campaigns(self):
        self.cursor.execute("""
        SELECT id, created_at, topic, blog_title
        FROM campaigns
        ORDER BY id DESC
        """)
        return self.cursor.fetchall()

    def get_all_metrics_history(self):
        self.cursor.execute("""
        SELECT
            campaign_id,
            persona,
            send_date,
            open_rate,
            click_rate,
            unsubscribe_rate,
            subject_line_style,
            content_angle,
            cta_type,
            weighted_score
        FROM performance_metrics
        ORDER BY campaign_id ASC, persona ASC
        """)
        rows = self.cursor.fetchall()

        return [
            {
                "campaign_id": row[0],
                "persona": row[1],
                "send_date": row[2],
                "open_rate": row[3],
                "click_rate": row[4],
                "unsubscribe_rate": row[5],
                "subject_line_style": row[6],
                "content_angle": row[7],
                "cta_type": row[8],
                "weighted_score": row[9]
            }
            for row in rows
        ]

    def get_metrics_for_campaign(self, campaign_id: int):
        self.cursor.execute("""
        SELECT
            campaign_id,
            persona,
            send_date,
            open_rate,
            click_rate,
            unsubscribe_rate,
            subject_line_style,
            content_angle,
            cta_type,
            weighted_score
        FROM performance_metrics
        WHERE campaign_id = ?
        ORDER BY id ASC
        """, (campaign_id,))
        rows = self.cursor.fetchall()

        return [
            {
                "campaign_id": row[0],
                "persona": row[1],
                "send_date": row[2],
                "open_rate": row[3],
                "click_rate": row[4],
                "unsubscribe_rate": row[5],
                "subject_line_style": row[6],
                "content_angle": row[7],
                "cta_type": row[8],
                "weighted_score": row[9]
            }
            for row in rows
        ]
