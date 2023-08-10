import dbconnection

def get_user_details_by_email(email=""):
    conn = dbconnection()
    user = conn.execute("SELECT * FROM users WHERE email = ?",(email,)).fetchone()
    conn.close()
    return user

def insert_user(email="", password="", name=""):
    conn = dbconnection()
    user = conn.execute("insert into users (name, email, pass) values (?, ?, ?) RETURNING id",(name,email,password)).fetchone()
    conn.commit()
    conn.close()
    (id, ) = user if user else None
    print(id)
    return id

def is_valid_creds(email, password):
   user = get_user_details_by_email(email)
   if(user is None):
      return False
   else:
    if(user["email"] == email and user['pass']==password):
      return user['id']
    else:
      return False
