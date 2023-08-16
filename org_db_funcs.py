import db
from datetime import datetime

def insert_org(creator_user_id="", name="", duration=0):
    conn = db()
    user = conn.execute("insert into organizations (name, creator_user_id, habit_name, duration) values (?, ?, ?, ?) RETURNING id",(name,creator_user_id, name, duration)).fetchone()
    conn.commit()
    conn.close()
    (id, ) = user if user else None
    return id

def insert_member(org_id, user_id, role="member"):
    conn = db()
    user = conn.execute("insert into members (organization_id, user_id, role) values (?, ?, ?) RETURNING id",(org_id,user_id, role)).fetchone()
    conn.commit()
    conn.close()
    (id, ) = user if user else None
    return id

def get_orgs_by_user_id(user_id=0):
    conn = db()
    habits = conn.execute("select organizations.* from members inner join organizations on members.organization_id = organizations.id where members.user_id=?",(user_id,)).fetchall()
    conn.commit()
    conn.close()
    return habits

def get_org_by_id(org_id=0):
    conn = db()
    habits = conn.execute("select * from organizations where id=?",(org_id,)).fetchall()
    conn.commit()
    conn.close()
    return habits[0]

def delete_org(org_id=0):
    conn = db()
    conn.execute("delete from organizations where id=?",(org_id,))
    conn.commit()
    conn.close()

def delete_members(org_id=0, user_id=0):
    conn = db()
    conn.execute("delete from members where organization_id=? and user_id=?",(org_id,user_id))
    conn.commit()
    conn.close()

def insert_org_habit(org_id, habit_name, duration, created_by_user_id):
    conn = db()
    user = conn.execute("insert into organization_habits(organization_id, habit_name, duration, created_by_user_id) values (?, ?, ?, ?) RETURNING id",(org_id,habit_name, duration, created_by_user_id)).fetchone()
    conn.commit()
    conn.close()
    (id, ) = user if user else None
    return id

def get_org_habits(org_id):
    conn = db()
    habits = conn.execute("select * from organization_habits where organization_id=?",(org_id,)).fetchall()
    conn.commit()
    conn.close()
    return habits

def delete_members(org_id=0, user_id=0):
    conn = db()
    conn.execute("delete from members where organization_id=? and user_id=?",(org_id,user_id))
    conn.commit()
    conn.close()

def delete_org_habits(habit_id=0):
    conn = db()
    conn.execute("delete from organization_habits where id=?",(habit_id))
    conn.commit()
    conn.close()

def get_org_habits_by_id(id):
    conn = db()
    habits = conn.execute("select * from organization_habits where id=?",(id,)).fetchall()
    conn.commit()
    conn.close()
    return habits[0]

def get_org_members(org_id):
    conn = db()
    habits = conn.execute("select * from members inner join users on members.user_id=users.id where members.organization_id=?",(org_id,)).fetchall()
    conn.commit()
    conn.close()
    return habits

def get_org_member_by_user_id_org_id(org_id, user_id):
    conn = db()
    habits = conn.execute("select * from members inner join users on members.user_id=users.id where members.organization_id=? and members.user_id=?",(org_id,user_id)).fetchone()
    conn.commit()
    conn.close()
    return habits

def update_user_days(completed_day,mem_id):
    conn = db()
    current_timestamp = datetime.now()
    conn.execute("UPDATE members SET completed_days = ?, updated_at = ? WHERE id = ?",(completed_day, current_timestamp, mem_id))
    conn.commit()
    conn.close()
    return True