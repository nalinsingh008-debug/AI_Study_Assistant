import pandas as pd

class StudyAnalytics:
    def __init__(self, repository):
        self.repository = repository

    def summary(self):
        records = self.repository.list_sessions()
        columns = ["subject", "study_hours", "tasks_completed", "session_date"]
        df = pd.DataFrame(records)
        if df.empty:
            return {
                "total_sessions": 0, "total_hours": 0.0,
                "total_tasks": 0, "subject_hours": {}
            }
        df["study_hours"] = pd.to_numeric(df["study_hours"], errors="coerce").fillna(0)
        df["tasks_completed"] = pd.to_numeric(
            df["tasks_completed"], errors="coerce"
        ).fillna(0)
        by_subject = df.groupby("subject")["study_hours"].sum()
        return {
            "total_sessions": int(len(df)),
            "total_hours": round(float(df["study_hours"].sum()), 2),
            "total_tasks": int(df["tasks_completed"].sum()),
            "subject_hours": {k: round(float(v), 2) for k, v in by_subject.items()}
        }

    def export_csv(self, output_path="study_report.csv"):
        df = pd.DataFrame(self.repository.list_sessions())
        if df.empty:
            df = pd.DataFrame(columns=[
                "id", "subject", "study_hours", "tasks_completed", "session_date"
            ])
        df.to_csv(output_path, index=False)
        return output_path
