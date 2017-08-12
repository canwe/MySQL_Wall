from flask import Flask, render_template, request, redirect, session, flash
import re
from mysqlconnection import MySQLConnector
import md5
FIRSTLAST_REGEX = re.compile(r'^(?=.*[0-9]).+$')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
UPPERDIGIT_REGEX = re.compile(r'^(?=.*[0-9])(?=.*[A-Z]).+$')
app = Flask(__name__)
app.secret_key = 'ItsSecretKey'
mysql = MySQLConnector(app,'theWall')

@app.route('/')
def root_route():
    return render_template("index.html")

@app.route('/wall')
def home():
    query = "SELECT messages.id, messages.data , DATE_FORMAT(messages.created_at,'%M %D %Y') AS update_at, CONCAT(users.first_name,' ',users.last_name) AS name FROM messages JOIN users ON messages.user_id = users.id"
    messages = mysql.query_db(query)

    query = "SELECT comments.id, comments.message_id, comments.data , DATE_FORMAT(comments.created_at,'%M %D %Y') AS update_at, CONCAT(users.first_name,' ',users.last_name) AS name FROM comments JOIN users ON comments.user_id = users.id"
    comments = mysql.query_db(query)

    # query = "DELETE comment FROM comments WHERE comments.id == "

    return render_template("wall.html",messages = messages, comments = comments)

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = md5.new(request.form['password']).hexdigest()
    query = "SELECT users.id,users.email as email, users.password as passwd, concat_ws(' ', users.first_name, users.last_name) as name FROM users where users.email = :email and users.password = :password"
    data = {
        "email" : email,
        "password" : password
    }
    info = mysql.query_db(query, data)
    if info:
        session['user_id'] = info[0]["id"]
        flash("Welcome Back " + info[0]["name"])
        return redirect("/wall")

    flash("Didn't found Matches for email and password! Failed to login")
    return redirect("/")

@app.route('/register',methods=['POST'])
def register():
    # print request.form
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    flag=0;

    if len(first_name) < 1:
        flash("First Name cannot be empty!")
        # return redirect('/')
        flag += 1;
    elif FIRSTLAST_REGEX.match(first_name):
        flash("Invalid First Name")
        # return redirect('/')
        flag += 1;

    if len(last_name) < 1:
        flash("Last Name cannot be empty!")
        # return redirect('/')
        flag += 1;
    elif FIRSTLAST_REGEX.match(last_name):
        flash("Invalid Last Name")
        # return redirect('/')
        flag += 1;

    if len(email) < 1:
        flash("Email cannot be empty!")
        # return redirect('/')
        flag += 1;
    elif not EMAIL_REGEX.match(email):
        flash("Invalid Email")
        # return redirect('/')
        flag += 1;  

    if len(password) < 1:
        flash("Password cannot be empty!")
        # return redirect('/')
        flag += 1;
    elif len(password) < 8:
        flash("Password must be longer than 8 characters!")
        # return redirect('/')
        flag += 1;
    elif not UPPERDIGIT_REGEX.match(password):
        flash("Password must contain at least one upper case letter and one digit")
        # return redirect('/')
        flag += 1;

    if len(confirm_password) < 1:
        flash("Please confirm password")
        # return redirect('/')
        flag += 1;

    if password != confirm_password:
        flash("Password must match!")
        # return redirect('/')
        flag += 1;

    if flag > 0:
        return redirect('/')
    
    password = md5.new(password).hexdigest()
    query = "SELECT users.email as email, users.password as passwd, concat_ws(' ', users.first_name, users.last_name) as name FROM users where users.email = :email"
    data = {
        "email" : email,
        "first_name" : first_name,
        "last_name" : last_name,
        "password" : password,
    }
    
    info = mysql.query_db(query, data)
    if info:
        flash("Email already exist in database!!")
        return redirect("/")

    query = "INSERT into users (users.first_name, users.last_name, users.email, users.password, users.created_at, users.updated_at) value (:first_name,:last_name,:email,:password,now(),now())"

    mysql.query_db(query, data)

    flash("Thank you for register " + first_name + " " + last_name)
    return render_template('register.html')

@app.route('/message/user<id>', methods=['POST'])
def message():
    message = request.form['message']
    query = "INSERT into messages(messages.data,messages.user_id, messages.created_at, messages.updated_at) value(:message,:id, NOW(), NOW())"
    print session["user_id"]
    data = {
        "message" : message,
        "id" : session["user_id"],
    }
    info = mysql.query_db(query, data)
    return redirect("/wall")

@app.route('/comment', methods=['POST'])
def comment():
    comment_id = request.form['comment_id']
    comment = request.form['comment']
    query = "INSERT into comments(comments.data,comments.user_id,comments.message_id, comments.created_at, comments.updated_at) value(:comment,:user_id, :message_id, NOW(), NOW())"
    data = {
        "comment" : comment,
        "user_id" : session["user_id"],
        "message_id" : comment_id,
    }
    info = mysql.query_db(query, data)
    return redirect("/wall")




@app.route('/wall',methods=['POST'])
def return_route():
    return redirect("/wall")

app.run(debug=True)