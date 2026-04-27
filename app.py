from flask import Flask, render_template, request,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import matplotlib #crear los graficos
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    content = db.Column(db.String(200),nullable=False)
    completed = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.now())

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        task_content= request.form.get('content')
        new_todo = Todo(content=task_content)
        db.session.add(new_todo)
        db.session.commit()
        return redirect("/")
    else:
        tasks = Todo.query.all()
        return render_template("index.html", tasks=tasks)
    
if __name__ == '__main__':
    app.run(debug=True, port=5001)