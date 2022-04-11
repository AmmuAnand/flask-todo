"""Setup at app startup"""
import os
import sqlalchemy
from flask import Flask, redirect, render_template, request, url_for
from yaml import load, Loader



def init_connection_engine():
    """ initialize database setup
    Takes in os variables from environment if on GCP
    Reads in local variables that will be ignored in public repository.
    Returns:
        pool -- a connection to GCP MySQL
    """

    #print("inside init_connection method")
    # detect env local or gcp
    if os.environ.get('GAE_ENV') != 'standard':
        try:
            variables = load(open("app.yaml"), Loader=Loader)
        except OSError as e:
            print("Make sure you have the app.yaml file setup")
            os.exit()

        env_variables = variables['env_variables']
        for var in env_variables:
            os.environ[var] = env_variables[var]
    #print("CREATING SQLALCHEMY ENGINE")

    pool = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL(
            drivername="mysql+pymysql",
            username=os.environ.get('MYSQL_USER'),
            password=os.environ.get('MYSQL_PASSWORD'),
            database=os.environ.get('MYSQL_DB'),
            host=os.environ.get('MYSQL_HOST')
        )
    )

    return pool


app = Flask(__name__)
db = init_connection_engine()


@app.route("/")
def home():
    """ Show all data"""
    conn = db.connect()
    query_results = conn.execute("Select * from todo;").fetchall()
    conn.close()
    todo_list = []
    for result in query_results:
        item = {
            "id": result[0],
            "title": result[1],
            "complete": result[2]
        }
        todo_list.append(item)

    
    # todo_list = Todo.query.all()
    # print(todo_list)
    return render_template("base.html", todo_list = todo_list)

@app.route("/add", methods=['POST'])
def add():
    """Adding new task"""
    title = request.form.get("title") #get from form
    conn = db.connect()
    query = 'Insert Into todo (title) VALUES ("{}");'.format(title)
    conn.execute(query)
    query_results = conn.execute("Select LAST_INSERT_ID();")
    query_results = [x for x in query_results]
    # print(query_results)
    conn.close()
    
    # new_todo = Todo(title=title, complete=False)
    # db.session.add(new_todo)
    # db.session.commit()    

    return redirect(url_for("home"))

@app.route("/update/<todo_id>")
def update(todo_id):
    """updating the created task"""
    #print(todo_id)
    conn = db.connect()
    status = conn.execute('select complete from todo where id = {};'.format(todo_id))
    #print("Status of the task is: ", status.scalar())
    if status.scalar() == 0:
        #print("Status is non completed and setting to complete")
        query = 'Update todo set complete = "{}" where id = {};'.format(1, todo_id)
        
    else:
        #print("status is completed and setting to non complete")
        query = 'Update todo set complete = "{}" where id = {};'.format(0, todo_id)
        
    conn.execute(query)
    conn.close()

    # todo = Todo.query.filter_by(id=todo_id).first()
    # todo.complete = not todo.complete
    # db.session.commit()    

    return redirect(url_for("home"))

@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    """deleting created task"""
    conn = db.connect()
    #print(todo_id)
    query = 'Delete From todo where id={};'.format(todo_id)
    conn.execute(query)
    conn.close()
    # todo = Todo.query.filter_by(id=todo_id).first()
    # db.session.delete(todo)
    # db.session.commit()    

    return redirect(url_for("home"))

if __name__ == '__main__':
    db.create_all()

    app.run(debug=True)