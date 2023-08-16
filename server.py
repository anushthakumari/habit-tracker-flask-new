from flask import Flask, request, redirect, url_for, flash, session
from flask import render_template
from flask_session import Session
from datetime import datetime, date
import random

import users_db_funcs;
import habits_db_funcs;
import org_db_funcs;

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = 'asecrentleywenneed'

Session(app)

def is_session_active():
	if not session.get("user_id"):
		return False
	else:
		return True
	
def set_session(user_id):
	session["user_id"] = user_id;

def get_session():
	return session["user_id"]

@app.route("/")
def main():
	if not is_session_active():
		return redirect(url_for("login"))
	return redirect(url_for("dashboard"))	

@app.route("/logout")
def logout():
	if not is_session_active():
		return redirect(url_for("login"))
	
	set_session(None)
	return redirect(url_for("login"))	

@app.route("/login",  methods=('GET', 'POST'))
def login():
	if is_session_active():
		return redirect(url_for("dashboard"))
	
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['pass']
		valid_user_id = users_db_funcs.check_login(email,password)
		if(valid_user_id == False):
			flash('Invalid Credentials!')
			return render_template('login.html')
			
		else:
			set_session(valid_user_id)
			return redirect(url_for("dashboard"))
			
	else:
		return render_template('login.html')
	
@app.route("/register",  methods=('GET', 'POST'))
def register():
	if is_session_active():
		return redirect(url_for("dashboard"))
	
	if request.method == 'POST':
		email = request.form['email'].strip()
		password = request.form['pass'].strip()
		confirm_pass = request.form['confirmpass'].strip()
		name = request.form['name'].strip()

		if(confirm_pass != password):
			flash("passwords do not matched!")
			return render_template('register.html')

		user = users_db_funcs.get_user_by_email(email)

		if(user != None):
			flash("user already exists!")
			return render_template('register.html')
		
		user_id = users_db_funcs.insert_user(email, password, name)
		set_session(user_id)

		return redirect(url_for("dashboard"))
			
	else:
		return render_template('register.html')
	
@app.route("/challenges")
def compare_page():
	if not is_session_active():
		return redirect(url_for("login"))
	tasks = habits_db_funcs.get_habits_by_day_progress(int(get_session()))

	return render_template('challenges.html', tasks=tasks);

@app.route("/group_challenges")
def group_challenge():
	if not is_session_active():
		return redirect(url_for("login"))
	
	user_id = int(get_session());
	orgs = org_db_funcs.get_orgs_by_user_id(user_id)

	return render_template('group_challenges.html', orgs=orgs);

@app.route("/delete-org/<int:org_id>")
def delete_org(org_id):
	if not is_session_active():
		return redirect(url_for("login"))
	
	user_id = int(get_session());
	org = org_db_funcs.get_org_by_id(org_id)

	if user_id != org["creator_user_id"]:
		flash("You cannot delete this organisation!")
		return redirect("/group_challenges")
	
	org_db_funcs.delete_members(org_id, user_id);
	org_db_funcs.delete_org(org_id);

	return redirect("/group_challenges")

@app.route("/create-org", methods=('POST',))
def create_org():
	if not is_session_active():
		return redirect(url_for("login"))
	
	if request.method == 'POST':
		title = request.form['title'].strip()
		duration = request.form['duration'].strip()

		user_id = int(get_session());

		org_id = org_db_funcs.insert_org(user_id,title, duration);
		org_db_funcs.insert_member(org_id,user_id,"creator");
		return redirect("/group_challenges")


	return redirect("/group_challenges")

@app.route("/org-habits/<int:org_id>")
def org_habits(org_id):
	if not is_session_active():
		return redirect(url_for("login"))
	
	tasks = org_db_funcs.get_org_habits(org_id)

	return render_template('org_habits.html', tasks=tasks, org_id=org_id);
@app.route("/org_habit_details/<int:org_id>")
def org_habits_details(org_id):
	if not is_session_active():
		return redirect(url_for("login"))
	
	user_id = int(get_session())
	habit_details = org_db_funcs.get_org_by_id(org_id)
	org_members = org_db_funcs.get_org_members(org_id)
	user_habit_details = org_db_funcs.get_org_member_by_user_id_org_id(org_id, user_id)

	return render_template('org_habit_details.html', habit=habit_details, org_members=org_members, day_progress=user_habit_details);

@app.route("/add-org-habit/<int:org_id>",  methods=('POST',))
def addOrghabits(org_id):
	if not is_session_active():
		return redirect(url_for("login"))
	
	if request.method == 'POST':
		title = request.form['title'].strip()
		duration = request.form['duration'].strip()

		user_id = int(get_session())

		org = org_db_funcs.get_org_by_id(org_id)

		if user_id != org["creator_user_id"]:
			flash("You cannot add habit to this organisation!")
			return redirect("/org-habits/"+str(org_id))
		
		org_db_funcs.insert_org_habit(int(org_id), title, int(duration), user_id);

		return redirect("/org-habits/"+str(org_id))
			
	else:
		return redirect("/org-habits/"+str(org_id))
	
	
@app.route("/increment-org-habit-day/<int:org_id>", methods=('GET',))
def add_org_day(org_id):
	if not is_session_active():
		return redirect(url_for("login"))
	
	user_id = int(get_session())
	
	user_progress = org_db_funcs.get_org_member_by_user_id_org_id(org_id, user_id)
	
	if user_progress['updated_at'] == None:
		org_db_funcs.update_user_days(user_progress['completed_days']+1, user_progress['id'])
		return redirect("/org_habit_details/"+str(org_id))
	
	updated_at = datetime.strptime(str(user_progress['updated_at']),  '%Y-%m-%d %H:%M:%S.%f');
	current_date = date.today();

	if updated_at.date() == current_date:
		flash("You have accomplished today's task, you can mark it tommorrow!")
		return redirect("/org_habit_details/"+str(org_id))
	else:
		org_db_funcs.update_user_days(user_progress['completed_days']+1, user_progress['id'])
		return redirect("/org_habit_details/"+str(org_id))	

@app.route("/dash")
def dashboard():
	if not is_session_active():
		return redirect(url_for("login"))
	
	habits = habits_db_funcs.get_uesrs_habit_with_progress(int(get_session()))
	orgs = org_db_funcs.get_orgs_by_user_id(int(get_session()))

	titles = []
	percentages = []
	backgrounds = []
	for row in habits:
		titles.append(row['title'])
		percentages.append(round((row['completed_days'] / row['duration']) *100, 1))
		
		random_number = random.randint(0,16777215)
		hex_number = str(hex(random_number))
		hex_number ='#'+ hex_number[2:]
		backgrounds.append(hex_number)

	return render_template('dashboard.html', habits=habits, titles=titles, percentages=percentages, backgrounds=backgrounds, orgs=orgs);

@app.route("/habit_details/<int:habit_id>/invite", methods=('GET', 'POST'))
def inviteFriend(habit_id):
	if not is_session_active():
		return redirect(url_for("login"))
	
	habit = habits_db_funcs.get_habit_by_id(habit_id)
	
	if request.method == 'POST':

		if habit['user_id'] != int(get_session()):
			flash("You cannot invite friends because you are not the owner!", category="error")
			return render_template('invite.html', habit=habit);

		email = request.form['email'].strip()
		user = users_db_funcs.get_user_by_email(email)

		if(user == None):
			flash("We dont have this user!", category="error")
			return render_template('invite.html', habit=habit);

	
		users_day_progress = habits_db_funcs.get_day_progress_by_user_id_and_habit_id(user['id'], habit_id)

		if len(users_day_progress) > 0:
			flash("This user is already a part of this habit!", category='error')
			return render_template('invite.html', habit=habit);


		habits_db_funcs.insert_into_day_progress(0, habit_id, user['id'])
		flash("User is added!", category='success')
		return render_template('invite.html', habit=habit);

	else:
		return render_template('invite.html', habit=habit);


@app.route("/compare/<int:habit_id>")
def compare_page_details(habit_id):
	if not is_session_active():
		return redirect(url_for("login"))

	habit = habits_db_funcs.get_habit_by_id(habit_id)
	users = habits_db_funcs.get_day_progress_by_habit_id(habit_id)
	return render_template('compare_details.html', habit=habit, users=users);

@app.route("/habits")
def habits():
	if not is_session_active():
		return redirect(url_for("login"))
	
	tasks = habits_db_funcs.get_habits_by_day_progress(int(get_session()))

	return render_template('habits.html', tasks=tasks);

@app.route("/add-habit",  methods=('POST',))
def addTasks():
	if not is_session_active():
		return redirect(url_for("login"))
	
	if request.method == 'POST':
		title = request.form['title'].strip()
		duration = request.form['duration'].strip()

		habit_id = habits_db_funcs.insert_into_habit(title, int(duration), int(get_session()))
		habits_db_funcs.insert_into_day_progress(0, habit_id, int(get_session()))
		return redirect(url_for("habits"))
			
	else:
		return redirect(url_for("habits"))
	
@app.route("/delete-task/<int:habit_id>")
def deleteTask(habit_id):
	if not is_session_active():
		return redirect(url_for("login"))
	
	habit = habits_db_funcs.get_habit_by_id(habit_id)

	if habit['user_id'] != int(get_session()):
		flash("Unable to delete this habit.")
		return redirect(url_for("habits"))
	
	habits_db_funcs.delete_day_progress_by_habit_id_user_id(habit_id)
	habits_db_funcs.delete_habit_by_id(habit_id)
	return redirect(url_for("habits"))

@app.route("/habit_details/<int:habit_id>", methods=('GET', 'POST'))
def habit_details(habit_id):
	if not is_session_active():
		return redirect(url_for("login"))
	
	habit = habits_db_funcs.get_habit_by_id(habit_id)

	if habit == None:
		return redirect(url_for("habits"))
	
	if request.method == 'POST':
		title = request.form['title'].strip()
		duration = request.form['duration'].strip()

		day_progress = habits_db_funcs.get_progress_by_user_id_habit_id(int(get_session()), habit_id)
		
		if day_progress['user_id'] != habit['user_id']:
			flash("unable to edit, you are not the owner!")
			users = habits_db_funcs.get_users_by_habit_id(habit_id, int(get_session()))
			return render_template('habit_details.html', habit=habits_db_funcs.get_habit_by_id(habit_id), day_progress=day_progress, users=users);

		habits_db_funcs.upadte_habit(title, int(duration), habit_id)
		day_progress = habits_db_funcs.get_progress_by_user_id_habit_id(int(get_session()), habit_id)
		users = habits_db_funcs.get_users_by_habit_id(habit_id, int(get_session()))
		return render_template('habit_details.html', habit=habits_db_funcs.get_habit_by_id(habit_id), day_progress=day_progress, users=users);

	day_progress = habits_db_funcs.get_progress_by_user_id_habit_id(int(get_session()), habit_id)
	users = habits_db_funcs.get_users_by_habit_id(habit_id, int(get_session()))
	return render_template('habit_details.html', habit=habit, day_progress=day_progress, users=users);

@app.route("/increment-habit-day/<int:habit_id>", methods=('GET',))
def add_day(habit_id):
	if not is_session_active():
		return redirect(url_for("login"))
	
	habit = habits_db_funcs.get_habit_by_id(habit_id)
	day_progress = habits_db_funcs.get_progress_by_user_id_habit_id(int(get_session()), habit_id)

	if habit == None:
		return redirect(url_for("habits"))
	
	if day_progress['updated_at'] == None:
		habits_db_funcs.update_day_progress_complete_day(day_progress['completed_days']+1, habit_id, int(get_session()))
		return redirect("/habit_details/"+str(habit_id))
	
	updated_at = datetime.strptime(str(day_progress['updated_at']),  '%Y-%m-%d %H:%M:%S.%f');
	current_date = date.today();

	if updated_at.date() == current_date:
		flash("You have accomplished today's task, you can mark it tommorrow!")
		return redirect("/habit_details/"+str(habit_id))
	else:
		habits_db_funcs.update_day_progress_complete_day(day_progress['completed_days']+1, habit_id, int(get_session()))
		return redirect("/habit_details/"+str(habit_id))	
	

@app.route("/org_habit_details/<int:habit_id>/invite", methods=('GET', 'POST'))
def invite_org_mem(habit_id):
	if not is_session_active():
		return redirect(url_for("login"))
	
	org = org_db_funcs.get_org_by_id(habit_id);
	if request.method == 'POST':

		if org['creator_user_id'] != int(get_session()):
			flash("You cannot invite member because you are not the owner of the organisation!", category="error")
			return render_template('invite_members.html', habit=org);

		email = request.form['email'].strip()
		user = users_db_funcs.get_user_by_email(email)

		if(user == None):
			flash("We dont have this user!", category="error")
			return render_template('invite_members.html', habit=org);

	
		users_day_progress = org_db_funcs.get_org_member_by_user_id_org_id(habit_id, user['id'])
		print(users_day_progress)
		if users_day_progress != None:
			flash("This user is already a part of this habit!", category='error')
			return render_template('invite_members.html', habit=org);


		org_db_funcs.insert_member(habit_id, user['id']);
		flash("User is added!", category='success')
		return render_template('invite_members.html', habit=org);

	else:
		return render_template('invite_members.html', habit=org);

if __name__ == "__main__":
	app.run(debug=False, port=80)
