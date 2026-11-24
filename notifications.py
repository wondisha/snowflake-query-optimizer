"""
Notification system for Snowflake Optimizer
Supports Slack, Teams, and Email alerts
"""

import os
import requests
from typing import List, Dict, Any
from datetime import datetime

class NotificationManager:
    """Manages alerts and notifications"""

    def __init__(self):
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        self.teams_webhook = os.getenv('TEAMS_WEBHOOK_URL')
        self.email_to = os.getenv('ALERT_EMAIL')

    def send_slack_notification(self, title: str, message: str, issues: List[Dict] = None):
        """Send analysis results to Slack"""
        if not self.slack_webhook:
            return False

        blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": title}},
            {"type": "section", "text": {"type": "mrkdwn", "text": message}},
        ]

        if issues:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Issues Found: {len(issues)}*\n" +
                           "\n".join([f"• {issue['description']}" for issue in issues[:5]])
                }
            })

        payload = {"blocks": blocks}

        try:
            response = requests.post(self.slack_webhook, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Slack notification failed: {e}")
            return False

    def send_teams_notification(self, title: str, message: str, color: str = "0078D4"):
        """Send analysis results to Microsoft Teams"""
        if not self.teams_webhook:
            return False

        payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": title,
            "themeColor": color,
            "sections": [{
                "activityTitle": title,
                "text": message,
                "activitySubtitle": f"Generated at {datetime.now().isoformat()}"
            }]
        }

        try:
            response = requests.post(self.teams_webhook, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Teams notification failed: {e}")
            return False

    def send_critical_alert(self, issues: List[Dict]):
        """Send alert for critical issues"""
        if not issues:
            return

        title = f"Critical Snowflake Issues Found ({len(issues)})"
        message = "The following critical optimization opportunities were identified:\n"

        for issue in issues[:3]:
            message += f"\n• **{issue.get('title', 'Unknown')}**\n"
            message += f"  Impact: {issue.get('impact', 'Unknown')}\n"
            message += f"  Action: {issue.get('recommendation', 'Review required')}\n"

        self.send_slack_notification(title, message, issues)
        self.send_teams_notification(title, message, "FF0000")

    def send_weekly_report(self, summary: Dict):
        """Send weekly optimization summary"""
        message = f"""
*Snowflake Optimization Weekly Report*

Total Tables Analyzed: {summary.get('tables', 0)}
Total Issues Found: {summary.get('issues', 0)}
Potential Cost Savings: ${summary.get('savings', 0):.2f}
Database Size: {summary.get('size_gb', 0):.2f} GB

Top Recommendations:
{chr(10).join(['• ' + r for r in summary.get('recommendations', [])])}

Trend: {summary.get('trend', 'Stable')}
"""
        self.send_slack_notification("Weekly Snowflake Report", message)

# Example usage
if __name__ == "__main__":
    manager = NotificationManager()
    manager.send_slack_notification(
        "Test Notification",
        "Agent is online and monitoring your Snowflake databases."
    )
