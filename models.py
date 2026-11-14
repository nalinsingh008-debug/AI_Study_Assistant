from dataclasses import dataclass

@dataclass
class StudySession:
    subject: str
    study_hours: float
    tasks_completed: int
    session_date: str

    def validate(self):
        if not self.subject.strip():
            raise ValueError("Subject cannot be empty.")
        if self.study_hours < 0:
            raise ValueError("Study hours cannot be negative.")
        if self.tasks_completed < 0:
            raise ValueError("Tasks completed cannot be negative.")
        if not self.session_date.strip():
            raise ValueError("Session date is required.")
