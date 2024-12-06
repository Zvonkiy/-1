class Patient:
    def __init__(self, patient_id=None, first_name="", last_name="", date_of_birth="", gender="", address="", phone_number="",
                 email=""):
        self.patient_id = patient_id
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.address = address
        self.phone_number = phone_number
        self.email = email

    def __repr__(self):
        return f"<Patient {self.first_name} {self.last_name}>"

    def is_valid(self):
        """Проверяет валидность данных пациента."""
        if not self.first_name or not self.last_name:
            return False  # Имя и фамилия обязательны
        if self.email and "@" not in self.email:  # простейшая проверка email
            return False
        # Добавьте  здесь  другие  проверки  валидности  данных  (например,  формат  даты  рождения)
        return True


class Doctor:
  def __init__(self, patient_id=None, first_name="", last_name="", speciality="", contact_info=""):
    self.doctor_id = patient_id
    self.first_name = first_name
    self.last_name = last_name
    self.speciality = speciality
    self.contact_info = contact_info

  def __repr__(self):
    return f"<Doctor {self.first_name} {self.last_name}>"


class health_data:
  def __init__(self, data_id=None, patient_id=None, doctor_id=None, measurement_date="", heart_rate="",
               blood_pressure="", body_temperature="", weight="",notes=""):
    self.data_id = data_id
    self.patient_id = patient_id
    self.doctor_id = doctor_id
    self.measurement_date = measurement_date
    self.heart_rate = heart_rate
    self.blood_pressure = blood_pressure
    self.body_temperature = body_temperature
    self.weight = weight
    self.notes = notes

  def __repr__(self):
    return f"<health_data {self.data_id}>"

class appointments:
  def __init__(self, appointment_id=None, patient_id=None, doctor_id=None, appointment_date="", notes=""):
    self.appointment_id = appointment_id
    self.patient_id = patient_id
    self.doctor_id = doctor_id
    self.appointment_date = appointment_date
    self.notes = notes

  def __repr__(self):
    return f"<appointments {self.appointment_id}>"

