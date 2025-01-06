import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# Path to your SQLite database
db_path = "C:/Users/elias/Desktop/Elias/PROGRAMMING/WalletBudget/var/app-instance/site.db"  # Update this to the correct path
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Function to list all tables in the database
def list_tables():
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in the database:")
    for table in tables:
        print(f"- {table[0]}")

# Function to count rows in the user table
def count_users():
    cursor.execute("SELECT COUNT(*) FROM user;")
    count = cursor.fetchone()[0]
    print(f"\nNumber of users in the database: {count}")

# Function to query all users in the user table
def query_users():
    cursor.execute("SELECT * FROM user;")
    users = cursor.fetchall()
    print("\nUsers in the database:")
    if not users:
        print("No users found!")
    else:
        for user in users:
            print(f"ID: {user[0]}, Username: {user[1]}, Password Hash: {user[2]}")

# Function to retrieve the hashed password for a specific user
def get_hashed_password(username):
    cursor.execute("SELECT password FROM user WHERE username = ?", (username,))
    result = cursor.fetchone()
    if result:
        print(f"\nHashed password for user '{username}': {result[0]}")
    else:
        print(f"\nUser '{username}' not found!")

# Function to verify if a password matches the stored hash
def verify_password(username, plain_password):
    cursor.execute("SELECT password FROM user WHERE username = ?", (username,))
    result = cursor.fetchone()
    if result:
        hashed_password = result[0]
        if check_password_hash(hashed_password, plain_password):
            print(f"Password for user '{username}' is correct!")
        else:
            print(f"Password for user '{username}' is incorrect!")
    else:
        print(f"\nUser '{username}' not found!")

# Function to export the hashed password to a file
def export_hashed_password(username):
    cursor.execute("SELECT password FROM user WHERE username = ?", (username,))
    result = cursor.fetchone()
    if result:
        hashed_password = result[0]
        filename = f"{username}_hash.txt"
        with open(filename, "w") as file:
            file.write(f"Username: {username}\nHashed Password: {hashed_password}")
        print(f"Hashed password for '{username}' has been exported to {filename}")
    else:
        print(f"\nUser '{username}' not found!")

# Run the functions
if __name__ == "__main__":
    print("Interacting with the SQLite database...\n")

    # List all tables
    list_tables()

    # Count users in the database
    count_users()

    # Query all users
    query_users()

    # Uncomment the function you want to test below:

    # Retrieve the hashed password for a specific user
    # get_hashed_password("Pantelis")  # Replace "Pantelis" with the username

    # Verify a user's password
    # verify_password("Pantelis", "your_plain_password")  # Replace with username and plain-text password

    # Export the hashed password to a file
    # export_hashed_password("Pantelis")  # Replace "Pantelis" with the username

# Close the connection
conn.close()
