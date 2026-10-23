
from flask import Flask, request, jsonify
from flask_cors import CORS
from threading import Lock

app = Flask(__name__)
CORS(app)

lock = Lock()
next_id = 3

# Fictional tasks for the competition demo.
tasks = [
    {
        "id": 1,
        "patient": "Amina N.",
        "type": "Medication support",
        "details": "Patient reports that medication is running low.",
        "priority": "High",
        "status": "Open",
        "source": "Sample record"
    },
    {
        "id": 2,
        "patient": "Brian K.",
        "type": "Routine follow-up",
        "details": "Check whether the patient needs help with their care plan.",
        "priority": "Normal",
        "status": "Open",
        "source": "Sample record"
    }
]


def add_task(task_type, details, priority="Normal"):
    global next_id

    with lock:
        task = {
            "id": next_id,
            "patient": "USSD demo patient",
            "type": task_type,
            "details": details,
            "priority": priority,
            "status": "Open",
            "source": "USSD simulation"
        }
        next_id += 1
        tasks.insert(0, task)
        return task


@app.get("/")
def home():
    return jsonify({
        "app": "AfyaLink USSD Backend",
        "status": "running",
        "demo": True
    })


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/ussd", methods=["GET", "POST"])
def ussd():
    # Africa's Talking sends the user's menu choices cumulatively,
    # for example: "2" then "2*3".
    text = request.values.get("text", "").strip()
    choices = text.split("*") if text else []

    if not choices:
        response = (
            "CON Welcome to AfyaLink\n"
            "1. Health check-in\n"
            "2. Medication support\n"
            "3. Request CHP\n"
            "4. Health tips\n"
            "0. Exit"
        )

    elif choices[0] == "1":
        if len(choices) == 1:
            response = (
                "CON How are you feeling today?\n"
                "1. Feeling okay\n"
                "2. Feeling unwell\n"
                "0. Back"
            )
        elif choices[1] == "1":
            response = "END Thank you. Your demo check-in is complete."
        elif choices[1] == "2":
            add_task(
                "Health follow-up",
                "Patient reported feeling unwell through USSD.",
                "High"
            )
            response = (
                "END Your request has been recorded for CHP follow-up. "
                "This is a demonstration, not emergency care."
            )
        else:
            response = "END Invalid selection. Please try again."

    elif choices[0] == "2":
        if len(choices) == 1:
            response = (
                "CON Choose medication support:\n"
                "1. Taken as planned\n"
                "2. Running low\n"
                "3. Need help accessing medication\n"
                "0. Back"
            )
        elif choices[1] == "1":
            response = "END Thank you. Your demo response is recorded."
        elif choices[1] == "2":
            add_task(
                "Medication support",
                "Patient reports medication is running low.",
                "High"
            )
            response = (
                "END Your medication support request has been recorded "
                "for CHP follow-up."
            )
        elif choices[1] == "3":
            add_task(
                "Medication access",
                "Patient requests help accessing medication.",
                "High"
            )
            response = (
                "END Your request has been recorded for CHP follow-up."
            )
        else:
            response = "END Invalid selection. Please try again."

    elif choices[0] == "3":
        add_task(
            "CHP support request",
            "Patient requested a CHP follow-up through USSD.",
            "Normal"
        )
        response = "END Your demo request has been recorded."

    elif choices[0] == "4":
        response = (
            "END Health tip: follow your clinician's advice, "
            "take prescribed medicine as directed, and attend follow-ups."
        )

    elif choices[0] == "0":
        response = "END Thank you for using AfyaLink."

    else:
        response = "END Invalid selection. Please try again."

    return response, 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.get("/api/tasks")
def get_tasks():
    with lock:
        return jsonify(tasks)


@app.post("/api/tasks/<int:task_id>/complete")
def complete_task(task_id):
    with lock:
        for task in tasks:
            if task["id"] == task_id:
                task["status"] = "Completed"
                return jsonify(task)

    return jsonify({"error": "Task not found"}), 404


if __name__ == "__main__":
    import os
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
