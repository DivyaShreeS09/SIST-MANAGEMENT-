import os
import csv
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from accounts.models import User

CSV_FILE = "2025 AIML Student Data.xlsx.csv"
DEFAULT_PASSWORD = "password123"

created_count = 0
updated_count = 0

print("Opening CSV file...")

with open(CSV_FILE, newline="", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)
    rows = list(reader)

print(f"Rows found: {len(rows)}")
print(f"Columns found: {reader.fieldnames}")

for i, row in enumerate(rows, start=1):
    name = str(row.get("Name", "")).strip()
    reg = str(row.get("Registration_number", "")).strip()
    dept = str(row.get("Program", "")).strip()
    section = str(row.get("Section", "")).strip()
    email = str(row.get("Email", "")).strip()

    if not reg or reg.lower() == "nan":
        continue

    existing = User.objects.filter(username=reg).first()

    if existing:
        existing.full_name = name
        existing.register_no = reg
        existing.department = dept
        existing.program = dept
        existing.section = section
        existing.email = email
        existing.role = "STUDENT"
        existing.hosteller = False
        existing.save()
        updated_count += 1
    else:
        User.objects.create_user(
            username=reg,
            password=DEFAULT_PASSWORD,
            full_name=name,
            register_no=reg,
            department=dept,
            program=dept,
            section=section,
            email=email,
            role="STUDENT",
            hosteller=False,
        )
        created_count += 1

    if i % 25 == 0:
        print(f"Processed {i} rows...")

print(f"Import complete. Created: {created_count}, Updated: {updated_count}")