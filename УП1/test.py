import pytest
import sqlite3
from health_monitoring_lib import Patient
from app import create_db_and_tables


def test_edit_patient(tmp_path):
    db_file = tmp_path / "test_db.db"
    create_db_and_tables(db_file)

    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()
    cursor.execute("INSERT INTO patients (first_name, last_name, date_of_birth, gender, address, phone_number, email) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   ("Мефодий Лазаревич", "Чистяков", "1961-02-05", "Other", "37533 Hood Turnpike Apt. 928", "+7 987 442-30-28", "maria.walters@example.com"))
    conn.commit()
    cursor.execute("SELECT patient_id FROM patients WHERE email = ?", ("maria.walters@example.com",))
    patient_id = cursor.fetchone()[0]

    #Simulate edit operation
    cursor.execute("UPDATE patients SET address = ? WHERE patient_id = ?", ("1011 Elm St", patient_id))
    conn.commit()

    cursor.execute("SELECT address FROM patients WHERE patient_id = ?", (patient_id,))
    updated_address = cursor.fetchone()[0]
    assert updated_address == "1011 Elm St"

    conn.close()

def test_patient_creation():
    patient = Patient("2", "Валерия Константиновна", "Осипова", "1985-11-23", "Male", "55478 Sarah Plain Apt. 860", "+7 989 698-46-10", "thomas.pittman@example.com")
    assert patient.first_name == "Валерия Константиновна"
    assert patient.last_name == "Осипова"
    assert patient.email == "thomas.pittman@example.com"

def test_add_duplicate_patient(tmp_path):
    db_file = tmp_path / "test_db.db"
    create_db_and_tables(db_file)
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()
    cursor.execute("INSERT INTO patients (first_name, last_name, date_of_birth, gender, address, phone_number, email) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   ("Duplicate", "Patient", "2000-01-01", "Male", "Test Address", "1234567890", "duplicate@example.com"))
    conn.commit()

    with pytest.raises(sqlite3.IntegrityError):  #Expect an IntegrityError
        cursor.execute("INSERT INTO patients (first_name, last_name, date_of_birth, gender, address, phone_number, email) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       ("Duplicate2", "Patient", "2000-01-01", "Male", "Test Address", "1234567890", "duplicate@example.com"))
        conn.commit()

    conn.close()