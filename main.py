from datetime import date
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field
from app.database import initialize_database
from app.models import StudySession
from app.repository import StudyRepository
from app.analytics import StudyAnalytics
from app.predictor import PerformancePredictor
from app.automation import ReportAutomation

initialize_database()
repository = StudyRepository()
analytics = StudyAnalytics(repository)
predictor = PerformancePredictor()
automation = ReportAutomation(analytics)

app = FastAPI(title="AI Study Assistant Pro", version="1.0.0")

class SessionInput(BaseModel):
    subject: str = Field(min_length=1, max_length=80)
    study_hours: float = Field(ge=0, le=24)
    tasks_completed: int = Field(ge=0, le=1000)
    session_date: str = Field(default_factory=lambda: date.today().isoformat())

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!doctype html><html><head><title>AI Study Assistant Pro</title>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <style>
    body{font-family:Arial;margin:0;background:#f3f6fb;color:#17243a}
    main{max-width:900px;margin:35px auto;padding:22px}
    .card{background:white;padding:22px;border-radius:14px;margin:14px 0;box-shadow:0 3px 14px #dce3ee}
    input,button{padding:11px;margin:5px;border:1px solid #ccd5e2;border-radius:8px}
    button{background:#2459d3;color:white;cursor:pointer;border:0}
    pre{white-space:pre-wrap}
    </style></head><body><main>
    <h1>📚 AI Study Assistant Pro</h1>
    <p>Track study sessions, analyse your progress and estimate your study score.</p>
    <div class="card"><h2>Add a study session</h2>
    <input id="subject" placeholder="Subject e.g. Python">
    <input id="hours" type="number" min="0" step=".5" placeholder="Study hours">
    <input id="tasks" type="number" min="0" placeholder="Tasks completed">
    <button onclick="addSession()">Save session</button><p id="status"></p></div>
    <div class="card"><h2>Your study analytics</h2>
    <button onclick="loadSummary()">Refresh summary</button>
    <pre id="summary">Click refresh to view your data.</pre></div>
    <div class="card"><h2>AI score estimate</h2>
    <input id="phours" type="number" min="0" placeholder="Planned study hours">
    <input id="ptasks" type="number" min="0" placeholder="Planned tasks">
    <button onclick="predict()">Estimate score</button><p id="prediction"></p></div>
    <div class="card"><h2>Reports</h2>
    <button onclick="makeReport()">Generate CSV report</button><p id="report"></p>
    <a href="/docs">Open API documentation</a></div></main>
    <script>
    async function addSession(){
      try{
        const r=await fetch('/sessions',{method:'POST',headers:{'Content-Type':'application/json'},
          body:JSON.stringify({subject:subject.value,study_hours:Number(hours.value),
          tasks_completed:Number(tasks.value)})});
        const d=await r.json(); status.textContent=r.ok?'Saved session #'+d.id:JSON.stringify(d);
        if(r.ok)loadSummary();
      }catch(e){status.textContent='Could not save session: '+e}
    }
    async function loadSummary(){
      const r=await fetch('/analytics'); summary.textContent=JSON.stringify(await r.json(),null,2);
    }
    async function predict(){
      const r=await fetch('/predict',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({study_hours:Number(phours.value),tasks_completed:Number(ptasks.value)})});
      const d=await r.json(); prediction.textContent=r.ok?'Estimated score: '+d.estimated_score+'/100':JSON.stringify(d);
    }
    async function makeReport(){
      const r=await fetch('/reports/daily',{method:'POST'}); const d=await r.json();
      report.textContent=r.ok?'Report created: '+d.path:JSON.stringify(d);
    }
    </script></body></html>
    """

@app.post("/sessions")
def create_session(payload: SessionInput):
    try:
        session = StudySession(payload.subject, payload.study_hours,
                               payload.tasks_completed, payload.session_date)
        new_id = repository.add_session(session)
        return {"message": "Study session saved", "id": new_id}
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.get("/sessions")
def get_sessions():
    try:
        return {"sessions": repository.list_sessions()}
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@app.get("/analytics")
def get_analytics():
    try:
        return analytics.summary()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analytics error: {exc}") from exc

@app.post("/predict")
def predict(payload: dict):
    try:
        hours = float(payload["study_hours"])
        tasks = int(payload["tasks_completed"])
        return {"estimated_score": predictor.predict_score(hours, tasks)}
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid prediction input: {exc}") from exc

@app.post("/reports/daily")
def daily_report():
    try:
        path = automation.create_daily_report()
        return {"message": "Report generated", "path": path}
    except (OSError, RuntimeError) as exc:
        raise HTTPException(status_code=500, detail=f"Report failed: {exc}") from exc

@app.get("/reports/download")
def download_report():
    path = Path("study_report.csv")
    analytics.export_csv(str(path))
    return FileResponse(path, media_type="text/csv", filename="study_report.csv")
