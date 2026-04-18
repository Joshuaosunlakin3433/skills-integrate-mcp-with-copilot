"""
High School Management System API

A FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
Now with persistent database storage.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os
from pathlib import Path

from src.database import engine, get_db, Base
from src.models import Activity, User, Club

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Sample data to seed database
SAMPLE_ACTIVITIES = [
    {
        "name": "Chess Club",
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
    },
    {
        "name": "Programming Class",
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
    },
    {
        "name": "Gym Class",
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
    },
    {
        "name": "Soccer Team",
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
    },
    {
        "name": "Basketball Team",
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
    },
    {
        "name": "Art Club",
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
    },
    {
        "name": "Drama Club",
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
    },
    {
        "name": "Math Club",
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
    },
    {
        "name": "Debate Team",
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
    },
]

SAMPLE_PARTICIPANTS = {
    "Chess Club": ["michael@mergington.edu", "daniel@mergington.edu"],
    "Programming Class": ["emma@mergington.edu", "sophia@mergington.edu"],
    "Gym Class": ["john@mergington.edu", "olivia@mergington.edu"],
    "Soccer Team": ["liam@mergington.edu", "noah@mergington.edu"],
    "Basketball Team": ["ava@mergington.edu", "mia@mergington.edu"],
    "Art Club": ["amelia@mergington.edu", "harper@mergington.edu"],
    "Drama Club": ["ella@mergington.edu", "scarlett@mergington.edu"],
    "Math Club": ["james@mergington.edu", "benjamin@mergington.edu"],
    "Debate Team": ["charlotte@mergington.edu", "henry@mergington.edu"],
}


@app.on_event("startup")
def startup_event(db: Session = Depends(get_db)):
    """Initialize database with sample data if empty."""
    # This is a simple seed function - in production use proper migrations
    for activity_data in SAMPLE_ACTIVITIES:
        existing = db.query(Activity).filter(
            Activity.name == activity_data["name"]
        ).first()
        if not existing:
            activity = Activity(**activity_data)
            db.add(activity)
    db.commit()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(db: Session = Depends(get_db)):
    """Get all activities with participant counts."""
    activities = db.query(Activity).all()
    result = {}
    for activity in activities:
        result[activity.name] = {
            "description": activity.description,
            "schedule": activity.schedule,
            "max_participants": activity.max_participants,
            "participants": [user.email for user in activity.participants],
            "current_participants": len(activity.participants),
        }
    return result


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(
    activity_name: str,
    email: str,
    db: Session = Depends(get_db)
):
    """Sign up a student for an activity."""
    # Find or create user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, role="student")
        db.add(user)
        db.commit()

    # Find activity
    activity = db.query(Activity).filter(
        Activity.name == activity_name
    ).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Check if already signed up
    if user in activity.participants:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Check capacity
    if len(activity.participants) >= activity.max_participants:
        raise HTTPException(
            status_code=400,
            detail="Activity is at full capacity"
        )

    # Sign up
    activity.participants.append(user)
    db.commit()
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(
    activity_name: str,
    email: str,
    db: Session = Depends(get_db)
):
    """Unregister a student from an activity."""
    # Find user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Find activity
    activity = db.query(Activity).filter(
        Activity.name == activity_name
    ).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Check if signed up
    if user not in activity.participants:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Unregister
    activity.participants.remove(user)
    db.commit()
    return {"message": f"Unregistered {email} from {activity_name}"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
