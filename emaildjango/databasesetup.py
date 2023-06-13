from django.db import connections


def createTable():
    with connections['default'].cursor() as cursor:
        cursor.execute(""" CREATE TABLE IF NOT EXISTS employees(
            id serial PRIMARY KEY,
            email VARCHAR(255) NOT NULL,
            password VARCHAR(255),
            isManager BOOLEAN NOT NULL,
            age INT NOT NULL,
            activation_token VARCHAR(32)
            )
            """)
        connections['default'].commit()
        

def insertData():
    with connections['default'].cursor() as cursor:
        cursor.execute("""
                       INSERT INTO employees(email,isManager,age)
                       VALUES
                       ('076bct038.nadika@pcampus.edu.np','False',22),
                       ('nadikapoudel16@gmail.com','False',22)
                       """)
        connections['default'].commit()
        
def createSession():
    with connections['default'].cursor() as cursor:
        cursor.execute(""" CREATE TABLE IF NOT EXISTS sessions(
            session_key VARCHAR(40) NOT NULL PRIMARY KEY,
            user_id INT NOT NULL
            )
            """)
        connections['default'].commit()
        
# def dropTable():
#     with connections['default'].cursor() as cursor:
#         cursor.execute(""" DROP TABLE IF EXISTS employees""")
#         connections['default'].commit()


    

        