from datetime import date
from app.analytics import StudyAnalytics

class ReportAutomation:
    def __init__(self, analytics: StudyAnalytics):
        self.analytics = analytics

    def create_daily_report(self, folder="reports"):
        from pathlib import Path
        Path(folder).mkdir(parents=True, exist_ok=True)
        filename = Path(folder) / f"study_report_{date.today().isoformat()}.csv"
        return self.analytics.export_csv(str(filename))
