import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
DATABASE = 'health_monitoring.db'


def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = dict_factory  # Use dict_factory here too
        print("Database connection successful!")  # Added
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")  # Added
        return None


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.route('/patients', methods=['GET'])
def get_patients():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500 # Handle DB connection failure

    conn.row_factory = dict_factory
    cursor = conn.execute('SELECT * FROM patients')
    patients = cursor.fetchall()
    conn.close()
    return jsonify(patients)

@app.route('/patients', methods=['POST'])
def create_patient():
    data = request.get_json()

    # Input Validation: Check for required fields and data types
    required_fields = ['first_name', 'last_name']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields: first_name, last_name'}), 400

    # Sanitize Input (important to prevent SQL injection):
    first_name = data.get('first_name').strip()  #remove leading/trailing whitespace
    last_name = data.get('last_name').strip()
    date_of_birth = data.get('date_of_birth')  #Consider date validation
    gender = data.get('gender') # Consider validation to allow only 'Male', 'Female', 'Other'
    address = data.get('address')
    phone_number = data.get('phone_number') # Consider phone number validation using regex
    email = data.get('email') # Consider email validation using regex

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        #Use parameterized query to prevent SQL injection
        cursor.execute("""
            INSERT INTO patients (first_name, last_name, date_of_birth, gender, address, phone_number, email)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (first_name, last_name, date_of_birth, gender, address, phone_number, email))
        conn.commit()
        patient_id = cursor.lastrowid  # Get the ID of the newly created patient
        conn.close()
        return jsonify({'message': 'Patient created', 'patient_id': patient_id}), 201  #Return 201 Created
    except sqlite3.IntegrityError as e: # Handle unique constraint violation (email)
        conn.close()
        return jsonify({'error': 'Email already exists'}), 409
    except sqlite3.Error as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': str(e)}), 500  #General database error

@app.route('/patients/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    data = request.get_json()

    # Input Validation
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Sanitize input (important for security!)
    first_name = data.get('first_name').strip() if data.get('first_name') else None
    last_name = data.get('last_name').strip() if data.get('last_name') else None
    date_of_birth = data.get('date_of_birth')
    gender = data.get('gender') #Validate gender values
    address = data.get('address')
    phone_number = data.get('phone_number')
    email = data.get('email')

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()

        # Construct the UPDATE query dynamically based on the provided data.  Only update fields that are present in the request.
        set_clause = ", ".join([f"{field} = ?" for field in data if field not in ('patient_id')])
        query = f"""
            UPDATE patients
            SET {set_clause}
            WHERE patient_id = ?
        """
        params = list(data.values()) if set_clause else []
        params.append(patient_id)  # Add patient_id as the last parameter


        cursor.execute(query, tuple(params))

        if cursor.rowcount == 0:  #Check if any rows were updated
            return jsonify({'error': 'Patient not found'}), 404

        conn.commit()
        conn.close()
        return jsonify({'message': 'Patient updated'}), 200
    except sqlite3.IntegrityError as e:  #Handle unique constraint violations (email)
        conn.close()
        return jsonify({'error': 'Email already exists'}), 409
    except sqlite3.Error as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Database connection failed'}), 500

        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM patients WHERE patient_id = ?", (patient_id,))
            conn.commit()
            rows_affected = cursor.rowcount

            if rows_affected == 0:
                conn.close()
                return jsonify({'error': 'Patient not found'}), 404

            conn.close()
            return jsonify({'message': 'Patient deleted'}), 200
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)