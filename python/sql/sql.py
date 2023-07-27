"""Python-Database"""

print("\n############################## %s ##################################\n" %(__doc__))

import mysql.connector

# create database connection
db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "root",
    charset = "utf8")

cursor = db.cursor()

# create database
cursor.execute("DROP DATABASE IF EXISTS runoob_db")

cursor.execute("CREATE DATABASE runoob_db")

sql = "SHOW DATABASES"

cursor.execute(sql)

print(sql + ": ")

for c in cursor:
    print(c)

print()

# connnect database
db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "root",
    database = "runoob_db",
    charset = "utf8")

cursor = db.cursor()

# create table
cursor.execute("DROP TABLE IF EXISTS employee")

cursor.execute(
    """CREATE TABLE employee (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    first_name  CHAR(20) NOT NULL,
    last_name  CHAR(20),
    age INT,  
    sex CHAR(1),
    income FLOAT )""")

sql = "SHOW TABLES"

cursor.execute(sql)
 
print(sql + ": ")

for c in cursor:
    print(c)
    
print()

# insert
try:
    # cursor.execute(
    #     """INSERT INTO employee(first_name,
    #     last_name, age, sex, income)
    #     VALUES ('%s', '%s', '%s', '%s', '%s')""" %
    #     ("Mac", "Mohan", 20, 'M', 2000))

    # cursor.execute(
    #     """INSERT INTO employee(first_name,
    #     last_name, age, sex, income)
    #     VALUES ('%s', '%s', '%s', '%s', '%s')""" %
    #     ("Lan", "Jane", 30, 'F', 1000))

    cursor.executemany(
        """INSERT INTO employee(first_name,
            last_name, age, sex, income)
            VALUES (%s, %s, %s, %s, %s)""",
        [("Mac", "Mohan", 20, 'M', 2000), 
            ("Lan", "Jane", 30, 'F', 1000)])

    db.commit()
except:
    db.rollback()

# query
try:
    sql = "SELECT * FROM employee"

    cursor.execute(sql)

    results = cursor.fetchall()

    print(sql + ": ")

    for row in results:
        print(row)

    print()
except:
    print("Error: unable to fecth data")

# delete
try:
    # cursor.execute("DELETE FROM employee WHERE age > %s", (20,))

    sql = "DELETE FROM employee WHERE age > %s" %(20)

    cursor.execute(sql)

    db.commit()

    print(sql + "\n")
except:
    db.rollback()

# update
try:
    # cursor.execute("UPDATE employee SET age = age + 1 WHERE sex = %s", ('M', ))

    sql = "UPDATE employee SET age = age + 1 WHERE sex = '%s'" %('M')

    cursor.execute(sql)

    db.commit()

    print(sql + "\n")
except:
    db.rollback()

try:
    # cursor.execute("SELECT * FROM employee WHERE income > %s", (1000,))

    sql = "SELECT * FROM employee WHERE income > %s" %(1000)

    cursor.execute(sql)

    results = cursor.fetchall()

    print(sql + ": ")

    for row in results:
        print(row)

    print()
except:
    print("Error: unable to fecth data")

db.close()
