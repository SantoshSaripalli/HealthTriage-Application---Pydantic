import asyncio
from dataclasses import dataclass
from typing import Any
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

load_dotenv()


@dataclass
class Patient:
    id: int
    first_name: str
    last_name: str
    age: int
    vitals: dict[str, Any]


class DatabaseConn:
    def __init__(self, db: dict[int, Patient]):
        self._db = db

    def get_patient_name(self, patient_id: int) -> str:
        patient = self._db[patient_id]
        return f"{patient.first_name} {patient.last_name}"

    def get_latest_vitals(self, patient_id: int) -> dict[str, Any]:
        return self._db[patient_id].vitals


Patient_DB = {
    1: Patient(id=1, first_name="John", last_name="Doe", age=18,
               vitals={"heart_rate": 72, "blood_pressure": "30/80", "blood_sugar": "100/80"}),
    2: Patient(id=2, first_name="Jane", last_name="Smith", age=45,
               vitals={"heart_rate": 88, "blood_pressure": "160/100", "blood_sugar": "95/80"}),
    3: Patient(id=3, first_name="Robert", last_name="Brown", age=62,
               vitals={"heart_rate": 118, "blood_pressure": "90/60", "blood_sugar": "110/70",
                       "chest_pain": "severe", "symptoms": "crushing chest pain, left arm pain, sweating, nausea"}),
}

conn = DatabaseConn(Patient_DB)

@dataclass
class TriageDependencies:
    patient_id: int
    db: DatabaseConn

class Triageoutput(BaseModel):
    response_text: str = Field(description="Triage recommendation for the patient.")
    triage_level: str = Field(description="Triage level for the patient.")
    escalate: bool = Field(description="Escalate for the human nurse.")

triage_agent = Agent(
    "anthropic:claude-sonnet-4-5",
    deps_type=TriageDependencies,
    output_type=Triageoutput,
    system_prompt=(
        "You are a medical triage assistant. Given a patient's name and vitals, "
        "assess their condition and provide a triage recommendation. "
        "Assign a triage level (e.g. immediate, urgent, less urgent, non-urgent) "
        "and determine whether to escalate to a human nurse."
    ),
)

@triage_agent.tool
def get_patient_info(ctx: RunContext[TriageDependencies]) -> dict[str, Any]:
    """Fetch the patient's name and latest vitals from the database."""
    name = ctx.deps.db.get_patient_name(ctx.deps.patient_id)
    vitals = ctx.deps.db.get_latest_vitals(ctx.deps.patient_id)
    return {"name": name, "vitals": vitals}

async def main():
    for patient_id in Patient_DB:
        deps = TriageDependencies(patient_id=patient_id, db=conn)
        result = await triage_agent.run(
            "Fetch the patient info and include their name and vitals in your recommendation.", deps=deps
        )
        print(f"Patient ID: {patient_id}")
        print(f"Recommendation: {result.output.response_text}")
        print(f"Triage Level: {result.output.triage_level}")
        print(f"Escalate: {result.output.escalate}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
