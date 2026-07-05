"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Team practice and competitive games for basketball enthusiasts",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["alex@mergington.edu", "nina@mergington.edu"]
    },
    "Swimming Club": {
        "description": "Improve swim techniques and compete in friendly meets",
        "schedule": "Tuesdays and Thursdays, 4:30 PM - 6:00 PM",
        "max_participants": 20,
        "participants": ["luke@mergington.edu", "mia@mergington.edu"]
    },
    "Art Workshop": {
        "description": "Explore painting, drawing, and mixed media art projects",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["sara@mergington.edu", "kevin@mergington.edu"]
    },
    "Drama Club": {
        "description": "Practice acting, stage production, and performance skills",
        "schedule": "Thursdays, 3:30 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ava@mergington.edu", "liam@mergington.edu"]
    },
    "Debate Team": {
        "description": "Prepare for debate competitions and develop persuasive speaking",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 16,
        "participants": ["eva@mergington.edu", "noah@mergington.edu"]
    },
    "Science Olympiad": {
        "description": "Work on science challenges, experiments, and competition events",
        "schedule": "Tuesdays, 5:00 PM - 6:30 PM",
        "max_participants": 18,
        "participants": ["mason@mergington.edu", "zoe@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Practice drills, teamwork, and competitive soccer matches",
        "schedule": "Mondays, Wednesdays, Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["ethan@mergington.edu", "chloe@mergington.edu"]
    },
    "Volleyball Club": {
        "description": "Learn volleyball skills, strategy, and play friendly matches",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["mia@mergington.edu", "jack@mergington.edu"]
    },
    "Track and Field": {
        "description": "Train for running, jumping, and throwing events",
        "schedule": "Wednesdays and Fridays, 4:00 PM - 6:00 PM",
        "max_participants": 25,
        "participants": ["sophia@mergington.edu", "oliver@mergington.edu"]
    },
    "Photography Club": {
        "description": "Explore photography techniques and share creative photo projects",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["ava@mergington.edu", "zyra@mergington.edu"]
    },
    "Creative Writing Workshop": {
        "description": "Write poetry, stories, and develop narrative voice",
        "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["olivia@mergington.edu", "sam@mergington.edu"]
    },
    "Music Ensemble": {
        "description": "Practice instrumental and vocal music together for performances",
        "schedule": "Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["nina@mergington.edu", "liam@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging math problems and prepare for competitions",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["emma@mergington.edu", "mason@mergington.edu"]
    },
    "Robotics Team": {
        "description": "Build robots, program them, and compete in robotics challenges",
        "schedule": "Fridays, 3:30 PM - 5:30 PM",
        "max_participants": 14,
        "participants": ["kevin@mergington.edu", "sara@mergington.edu"]
    },
    "History Society": {
        "description": "Discuss historical events, research topics, and host presentations",
        "schedule": "Mondays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["noah@mergington.edu", "zoe@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student already signed up for this activity")

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}
