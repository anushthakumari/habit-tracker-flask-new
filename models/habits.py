import dbconnection
from datetime import datetime

def insert_habit(title="", duration=0, user_id=0):
    conn = dbconnection()
    habit = conn.execute("insert into habits (title, duration, user_id) values (?, ?, ?) RETURNING id",(title, duration, user_id)).fetchone()
    conn.commit()
    conn.close()
    (id, ) = habit if habit else None
    return id

def insert_day_progress(completed_days=0, habit_id=0, user_id=0):
    conn = dbconnection()
    habit = conn.execute("insert into day_progress (completed_days, user_id, habit_id) values (?, ?, ?) RETURNING id",(completed_days, user_id, habit_id)).fetchone()
    conn.commit()
    conn.close()
    (id, ) = habit if habit else None
    return id

def upadte_habit(title="", duration=0, habit_id=0):
    conn = dbconnection()
    current_timestamp = datetime.now()
    conn.execute("UPDATE habits SET title = ?, duration = ?, updated_at = ? WHERE id = ?",(title, duration, current_timestamp,  habit_id))
    conn.commit()
    conn.close()
    return True

def get_habits_by_user_id(user_id=0):
    conn = dbconnection()
    habits = conn.execute("select * from habits where user_id=?",(user_id,)).fetchall()
    conn.commit()
    conn.close()
    return habits

def get_habits_by_day_progress(user_id=0):
    conn = dbconnection()
    habits = conn.execute("select habits.*, day_progress.completed_days from day_progress inner join habits on day_progress.habit_id=habits.id where day_progress.user_id=?",(user_id,)).fetchall()
    conn.commit()
    conn.close()
    return habits

def get_progress_by_user_id_habit_id(user_id=0, habit_id=0):
    conn = dbconnection()
    habits = conn.execute("select * from day_progress where user_id=? and habit_id=?",(user_id,habit_id)).fetchone()
    conn.commit()
    conn.close()
    return habits

def get_users_by_habit_id(habit_id=0, user_id=0):
    conn = dbconnection()
    if user_id != 0:
        habits = conn.execute("select users.* from day_progress inner join users on users.id=day_progress.user_id where day_progress.habit_id=? and day_progress.user_id != ?",(habit_id, user_id)).fetchall()
        conn.commit()
        conn.close()
        return habits
    else:
        habits = conn.execute("select users.* from day_progress inner join users on users.id=day_progress.user_id where day_progress.habit_id=?",(habit_id,)).fetchall()
        conn.commit()
        conn.close()
        return habits


def delete_habit_by_id(id=0):
    conn = dbconnection()
    conn.execute("delete from habits where id=?",(id,))
    conn.commit()
    conn.close()
    return True

def delete_day_progress_by_habit_id_user_id(habit_id=0):
    conn = dbconnection()
    conn.execute("delete from day_progress where habit_id=?",(habit_id,))
    conn.commit()
    conn.close()
    return True

def get_habit_by_id(id=0):
    conn = dbconnection()
    habit = conn.execute("SELECT * FROM habits WHERE id = ?",(id,)).fetchone()
    conn.close()
    return habit

def update_day_progress_complete_day(completed_day=1,habit_id=0, user_id=0):
    conn = dbconnection()
    current_timestamp = datetime.now()
    conn.execute("UPDATE day_progress SET completed_days = ?, updated_at = ? WHERE user_id = ? and habit_id = ?",(completed_day, current_timestamp, user_id, habit_id))
    conn.commit()
    conn.close()
    return True

def get_day_progress_by_user_id_habit_id_all(user_id=0, habit_id=0):
    conn = dbconnection()
    habits = conn.execute("select * from day_progress where user_id=? and habit_id=?",(user_id,habit_id)).fetchall()
    conn.commit()
    conn.close()
    return habits

def get_day_progress_by_habit_id(habit_id=0):
    conn = dbconnection()
    habits = conn.execute("select day_progress.*, users.email, users.name from day_progress inner join users on day_progress.user_id=users.id where day_progress.habit_id=? order by day_progress.completed_days desc",(habit_id,)).fetchall()
    conn.commit()
    conn.close()
    return habits

def get_uesrs_habit_with_progress(user_id=0):
    conn = dbconnection()
    habits = conn.execute("select habits.title, habits.duration, day_progress.completed_days from day_progress inner join habits on habits.id=day_progress.habit_id where day_progress.user_id=? order by day_progress.completed_days desc",(user_id,)).fetchall()
    conn.commit()
    conn.close()
    return habits