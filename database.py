import sqlite3

# Path to the database file
db_path = "C:/Users/elias/Desktop/Elias/PROGRAMMING/WalletBudget/site.db"

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# List all tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Print all tables
print("Tables in the database:")
for table in tables:
    print(table[0])

# Close the connection
conn.close()
