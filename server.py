from flask import Flask, request, redirect, url_for, flash, session
from flask import render_template
from flask_session import Session
from datetime import datetime, date
import random

from models.users import get_user_details_by_email, insert_user, is_valid_creds
from models.habits import insert_habit, delete_habit_by_id, get_habit_by_id, upadte_habit, update_day_progress_complete_day, insert_day_progress, delete_day_progress_by_habit_id_user_id, get_progress_by_user_id_habit_id, get_habits_by_day_progress, get_users_by_habit_id, get_day_progress_by_user_id_habit_id_all, get_day_progress_by_habit_id, get_uesrs_habit_with_progress

# creates a Flask application
app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisIShabitTracjer%7lp'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

def is_logged_in():
	if not session.get("user_id"):
		return False
	else:
		return True
	
def set_login_session(user_id):
	session["user_id"] = user_id;

def get_login_session():
	return session["user_id"]


@app.route("/")
def home():
	message = "Hello, World"
	return render_template('login.html', message=message);

@app.route("/logout")
def logout():
	if not is_logged_in():
		return redirect(url_for("loginPage"))
	
	set_login_session(None)
	return redirect(url_for("loginPage"))	

@app.route("/login",  methods=('GET', 'POST'))
def loginPage():
	if is_logged_in():
		return redirect(url_for("dash"))
	
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['pass']
		valid_user_id = is_valid_creds(email,password)
		if(valid_user_id == False):
			flash('Invalid Credentials!')
			return render_template('login.html')
			
		else:
			set_login_session(valid_user_id)
			return redirect(url_for("dash"))
			
	else:
		return render_template('login.html')
	
@app.route("/register",  methods=('GET', 'POST'))
def registerPage():
	if is_logged_in():
		return redirect(url_for("dash"))
	
	if request.method == 'POST':
		email = request.form['email'].strip()
		password = request.form['pass'].strip()
		confirm_pass = request.form['confirmpass'].strip()
		name = request.form['name'].strip()

		if(confirm_pass != password):
			flash("passwords do not matched!")
			return render_template('register.html')

		user = get_user_details_by_email(email)

		if(user != None):
			flash("user with this email already exists!")
			return render_template('register.html')
		
		user_id = insert_user(email, password, name)
		set_login_session(user_id)

		return redirect(url_for("dash"))
			
	else:
		return render_template('register.html')
		

@app.route("/dash")
def dash():
	if not is_logged_in():
		return redirect(url_for("loginPage"))
	
	habits = get_uesrs_habit_with_progress(int(get_login_session()))

	titles = []
	percentages = []
	backgrounds = []
	for row in habits:
		# row['percent'] = 
		titles.append(row['title'])
		percentages.append(round((row['completed_days'] / row['duration']) *100, 1))
		
		random_number = random.randint(0,16777215)
		hex_number = str(hex(random_number))
		hex_number ='#'+ hex_number[2:]
		backgrounds.append(hex_number)

	return render_template('dashboard.html', habits=habits, titles=titles, percentages=percentages, backgrounds=backgrounds);

@app.route("/compare")
def compare():
	if not is_logged_in():
		return redirect(url_for("loginPage"))
	tasks = get_habits_by_day_progress(int(get_login_session()))

	return render_template('compare.html', tasks=tasks);

@app.route("/compare/<int:habit_id>")
def compare_de(habit_id):
	if not is_logged_in():
		return redirect(url_for("loginPage"))

	habit = get_habit_by_id(habit_id)
	users = get_day_progress_by_habit_id(habit_id)
	return render_template('compare_details.html', habit=habit, users=users);

@app.route("/progress")
def progress():
	if not is_logged_in():
		return redirect(url_for("loginPage"))
	habits = get_uesrs_habit_with_progress(int(get_login_session()))
	return render_template('progress.html', habits=habits);

@app.route("/tasks")
def tasks():
	if not is_logged_in():
		return redirect(url_for("loginPage"))
	
	tasks = get_habits_by_day_progress(int(get_login_session()))

	return render_template('tasks.html', tasks=tasks);

@app.route("/add-new-task",  methods=('POST',))
def addNewTask():
	if not is_logged_in():
		return redirect(url_for("loginPage"))
	
	if request.method == 'POST':
		title = request.form['title'].strip()
		duration = request.form['duration'].strip()

		habit_id = insert_habit(title, int(duration), int(get_login_session()))
		insert_day_progress(0, habit_id, int(get_login_session()))
		return redirect(url_for("tasks"))
			
	else:
		return redirect(url_for("tasks"))
	
@app.route("/delete-task/<int:habit_id>")
def deleteTask(habit_id):
	if not is_logged_in():
		return redirect(url_for("loginPage"))
	
	habit = get_habit_by_id(habit_id)

	# must be an owner to delete the habit!
	if habit['user_id'] != int(get_login_session()):
		flash("You cannot delete the habit!!")
		return redirect(url_for("tasks"))
	
	delete_day_progress_by_habit_id_user_id(habit_id)
	delete_habit_by_id(habit_id)
	return redirect(url_for("tasks"))

@app.route("/habit_details/<int:habit_id>", methods=('GET', 'POST'))
def getHabitDetails(habit_id):
	if not is_logged_in():
		return redirect(url_for("loginPage"))
	
	habit = get_habit_by_id(habit_id)

	if habit == None:
		return redirect(url_for("tasks"))
	
	if request.method == 'POST':
		title = request.form['title'].strip()
		duration = request.form['duration'].strip()

		day_progress = get_progress_by_user_id_habit_id(int(get_login_session()), habit_id)
		
		if day_progress['user_id'] != habit['user_id']:
			flash("You cannot edit this!")
			users = get_users_by_habit_id(habit_id, int(get_login_session()))
			return render_template('habit_details.html', habit=get_habit_by_id(habit_id), day_progress=day_progress, users=users);

		upadte_habit(title, int(duration), habit_id)
		day_progress = get_progress_by_user_id_habit_id(int(get_login_session()), habit_id)
		users = get_users_by_habit_id(habit_id, int(get_login_session()))
		return render_template('habit_details.html', habit=get_habit_by_id(habit_id), day_progress=day_progress, users=users);

	day_progress = get_progress_by_user_id_habit_id(int(get_login_session()), habit_id)
	users = get_users_by_habit_id(habit_id, int(get_login_session()))
	return render_template('habit_details.html', habit=habit, day_progress=day_progress, users=users);

@app.route("/increment-habit-day/<int:habit_id>", methods=('GET',))
def incrementHabitDay(habit_id):
	if not is_logged_in():
		return redirect(url_for("loginPage"))
	
	habit = get_habit_by_id(habit_id)
	day_progress = get_progress_by_user_id_habit_id(int(get_login_session()), habit_id)

	if habit == None:
		return redirect(url_for("tasks"))
	
	if day_progress['updated_at'] == None:
		update_day_progress_complete_day(day_progress['completed_days']+1, habit_id, int(get_login_session()))
		return redirect("/habit_details/"+str(habit_id))
	
	updated_at = datetime.strptime(str(day_progress['updated_at']),  '%Y-%m-%d %H:%M:%S.%f');
	current_date = date.today();

	# if last marked day was today then do not let them mark
	if updated_at.date() == current_date:
		flash("You cannot mark a day as complete beacuse you have already marked a day today!")
		return redirect("/habit_details/"+str(habit_id))
	else:
		update_day_progress_complete_day(day_progress['completed_days']+1, habit_id, int(get_login_session()))
		return redirect("/habit_details/"+str(habit_id))


@app.route("/habit_details/<int:habit_id>/invite", methods=('GET', 'POST'))
def addFriend(habit_id):
	if not is_logged_in():
		return redirect(url_for("loginPage"))
	
	habit = get_habit_by_id(habit_id)
	
	if request.method == 'POST':

		if habit['user_id'] != int(get_login_session()):
			flash("You cannot invite friends because you are not the owner!", category="error")
			return render_template('addfriend.html', habit=habit);

		email = request.form['email'].strip()
		user = get_user_details_by_email(email)

		if(user == None):
			flash("User with this email doesn't exists!", category="error")
			return render_template('addfriend.html', habit=habit);

	
		users_day_progress = get_day_progress_by_user_id_habit_id_all(user['id'], habit_id)

		if len(users_day_progress) > 0:
			flash("This user is already a part of this habit!", category='error')
			return render_template('addfriend.html', habit=habit);


		insert_day_progress(0, habit_id, user['id'])
		flash("User is added!", category='success')
		return render_template('addfriend.html', habit=habit);

	else:
		return render_template('addfriend.html', habit=habit);

	
	


# run the application
if __name__ == "__main__":
	app.run(debug=True,port=80)
