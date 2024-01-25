from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/sg'
db = SQLAlchemy(app)

# Define your models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class UserProject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

class TaskProject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userproject_id = db.Column(db.Integer, db.ForeignKey('user_project.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)


# API endpoint to add UserProject entry
@app.route("/add_user_project", methods=["POST"])
def add_user_project():
    data = request.get_json()

    user_id = data.get("user_id")
    project_name = data.get("project_name")

    user_project = UserProject.query.filter_by(
        user_id=user_id,
        project_id=Project.query.filter_by(name=project_name).first().id,
    ).first()

    if not user_project:
        # Create the project if it doesn't exist
        project = Project.query.filter_by(name=project_name).first()
        if not project:
            project = Project(name=project_name)
            db.session.add(project)
            db.session.commit()

        # Create the UserProject entry
        user_project = UserProject(user_id=user_id, project_id=project.id)
        db.session.add(user_project)
        db.session.commit()

        return jsonify({"message": "UserProject entry added successfully"})
    else:
        return jsonify({"message": "UserProject entry already exists"})


# API endpoint to add TaskProject entry
@app.route("/add_task_project", methods=["POST"])
def add_task_project():
    data = request.get_json()

    user_project_id = data.get("user_project_id")
    task_id = data.get("task_id")

    task_project = TaskProject.query.filter_by(
        userproject_id=user_project_id, task_id=task_id
    ).first()

    if not task_project:
        # Create the TaskProject entry
        task_project = TaskProject(userproject_id=user_project_id, task_id=task_id)
        db.session.add(task_project)
        db.session.commit()

        return jsonify({"message": "TaskProject entry added successfully"})
    else:
        return jsonify({"message": "TaskProject entry already exists"})


# API endpoint to get TaskProject entry
@app.route("/get_task_project", methods=["GET"])
def get_task_project():
    data = request.args

    user_id = int(data.get("user_id"))

    # Fetch data from the TaskProject table
    task_project_data = (
        db.session.query(
            User.id.label("User_id"),
            User.name.label("User_name"),
            Project.id.label("Project_id"),
            Project.name.label("Project_name"),
            Task.id.label("Task_id"),
            Task.name.label("Task_name"),
        )
        .join(UserProject, UserProject.id == TaskProject.userproject_id)
        .join(User, User.id == UserProject.user_id)
        .join(Project, Project.id == UserProject.project_id)
        .join(Task, Task.id == TaskProject.task_id)
        .filter(User.id == user_id)
        .all()
    )

    result = []
    for entry in task_project_data:
        result.append(
            {
                "User_id": entry.User_id,
                "User_name": entry.User_name,
                "Project_id": entry.Project_id,
                "Project_name": entry.Project_name,
                "Task_id": entry.Task_id,
                "Task_name": entry.Task_name,
            }
        )

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
