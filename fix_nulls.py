import sqlite3
import os

# Point to your actual DB file (change if needed)
db_path = os.path.join(os.getcwd(), 'db.sqlite3')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Replace NULLs with defaults
cursor.execute("UPDATE directory_escort SET phone_number = 'N/A' WHERE phone_number IS NULL;")
cursor.execute("UPDATE directory_escort SET services = 'Not specified' WHERE services IS NULL;")
cursor.execute("UPDATE directory_escort SET user_id = 1 WHERE user_id IS NULL;")


conn.commit()
conn.close()

print("✅ Null values replaced successfully.")

from django.contrib.auth.models import User
print(User.objects.all())
