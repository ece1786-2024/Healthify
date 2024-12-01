import sqlite3
database="user_profiles.db"
connection = sqlite3.connect(database)
cursor = connection.cursor()

# Fetch the table structure (columns)
cursor.execute("PRAGMA table_info(user_profiles);")
columns = [column[1] for column in cursor.fetchall()]

# Fetch the user's data
cursor.execute("SELECT * FROM user_profiles;")
rows = cursor.fetchall()

# Close the connection
connection.close()

print(columns, rows)