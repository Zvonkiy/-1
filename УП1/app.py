import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
from health_monitoring_lib import Patient
import sqlite3
from tkcalendar import DateEntry

def create_db_and_tables(db_name="health_monitoring.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS patients (
        patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        date_of_birth DATE,
        gender TEXT,
        address TEXT,
        phone_number TEXT,
        email TEXT UNIQUE
    )''')

    conn.commit()
    conn.close()


create_db_and_tables()

class App:
    def __init__(self, master):
        self.master = master
        master.title("Health Monitoring System")
        self.create_widgets()
        self.load_patients()

    def load_patients(self):
        self.patients_listbox.delete(0, tk.END)
        conn = sqlite3.connect('health_monitoring.db')
        cursor = conn.cursor()
        cursor.execute("SELECT patient_id, first_name, last_name FROM patients")
        patients = cursor.fetchall()
        for patient_id, first_name, last_name in patients:
            self.patients_listbox.insert(tk.END, f"{patient_id} - {first_name} {last_name}")
        conn.close()

    def create_widgets(self):
        # Этикетки и поля ввода
        ttk.Label(self.master, text="Имя-Отчество:").grid(row=0, column=0, sticky=tk.W)
        self.first_name_entry = ttk.Entry(self.master)
        self.first_name_entry.grid(row=0, column=1)
        ttk.Label(self.master, text="Фамилия:").grid(row=1, column=0, sticky=tk.W)
        self.last_name_entry = ttk.Entry(self.master)
        self.last_name_entry.grid(row=1, column=1)
        ttk.Label(self.master, text="Дата рождения:").grid(row=2, column=0, sticky=tk.W)
        self.date_of_birth_entry = ttk.Entry(self.master)
        self.date_of_birth_entry.grid(row=2, column=1)
        ttk.Label(self.master, text="Пол:").grid(row=3, column=0, sticky=tk.W)
        self.gender_entry = ttk.Entry(self.master)
        self.gender_entry.grid(row=3, column=1)
        ttk.Label(self.master, text="Адрес:").grid(row=4, column=0, sticky=tk.W)
        self.address_entry = ttk.Entry(self.master)
        self.address_entry.grid(row=4, column=1)
        ttk.Label(self.master, text="Номер телефона:").grid(row=5, column=0, sticky=tk.W)
        self.phone_number_entry = ttk.Entry(self.master)
        self.phone_number_entry.grid(row=5, column=1)
        ttk.Label(self.master, text="Почта:").grid(row=6, column=0, sticky=tk.W)
        self.email_entry = ttk.Entry(self.master)
        self.email_entry.grid(row=6, column=1)
        ttk.Button(self.master, text="Добавить пациента", command=self.add_patient).grid(row=7, column=0, columnspan=2)
        ttk.Button(self.master, text="Удалить пациента", command=self.delete_patient).grid(row=8, column=0, columnspan=2)
        ttk.Button(self.master, text="Просмотреть и отредактировать запись", command=self.edit_patient).grid(row=9, column=0, columnspan=2)
        self.patients_listbox = tk.Listbox(self.master)
        self.patients_listbox.grid(row=10, column=0, columnspan=2)
        ttk.Button(self.master, text="Добавить пациента", command=self.add_patient).grid(row=7, column=0, columnspan=2)
        ttk.Button(self.master, text="Удалить пациента", command=self.delete_patient).grid(row=8, column=0,
                                                                                                           columnspan=2)
        ttk.Button(self.master, text="Открыть приложение с данными врачей", command=self.open_doctor_app).grid(row=13,
                                                                                                               column=0,
                                                                                                               columnspan=2)

        self.patients_listbox = tk.Listbox(self.master, selectmode=tk.SINGLE)
        self.patients_listbox.grid(row=10, column=0, columnspan=2, sticky=tk.NSEW)
        self.patients_listbox.bind("<<ListboxSelect>>", self.on_patient_select)

    def add_patient(self):
        try:
            patient = Patient(first_name=self.first_name_entry.get(), last_name=self.last_name_entry.get(),
                              date_of_birth=self.date_of_birth_entry.get(), gender=self.gender_entry.get(),
                              address=self.address_entry.get(),
                              phone_number=self.phone_number_entry.get(), email=self.email_entry.get())
            conn = sqlite3.connect('health_monitoring.db')
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO patients (first_name, last_name, date_of_birth, gender, address, phone_number, email) VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (patient.first_name, patient.last_name, patient.date_of_birth, patient.gender, patient.address, patient.phone_number,
                 patient.email))
            conn.commit()
            messagebox.showinfo("Успех!", "Пациент добавлен!")
            conn.close()
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка!", "Почта уже существует")
        except Exception as e:
            messagebox.showerror("Ошибка!", f"Произошла ошибка: {e}")

    def delete_patient(self):
        if self.patients_listbox.curselection():
            try:
                index = self.patients_listbox.curselection()[0]
                patient_id = int(self.patients_listbox.get(index).split(" - ")[0])
                conn = sqlite3.connect('health_monitoring.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM patients WHERE patient_id = ?", (patient_id,))
                conn.commit()
                messagebox.showinfo("Успех!", "Пациент удален!")
                self.load_patients()
                conn.close()
            except Exception as e:
                messagebox.showerror("Ошибка!", f"Произошла ошибка: {e}")
        else:
            messagebox.showwarning("Предупреждение!", "Выберите пациента для удаления")

    def edit_patient(self):
        if self.patients_listbox.curselection():
            try:
                index = self.patients_listbox.curselection()[0]
                patient_id = int(self.patients_listbox.get(index).split(" - ")[0])
                conn = sqlite3.connect('health_monitoring.db')
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,))
                patient_data = cursor.fetchone()
                conn.close()

                try:
                    new_patient_data = self.get_patient_data_from_dialog(patient_data)
                    if new_patient_data:
                        conn = sqlite3.connect('health_monitoring.db')
                        cursor = conn.cursor()
                        # Проверка на уникальность email (простая проверка, можно улучшить)
                        cursor.execute("SELECT COUNT(*) FROM patients WHERE email = ? AND patient_id != ?",
                                       (new_patient_data[7], patient_id))
                        if cursor.fetchone()[0] > 0:
                            messagebox.showerror("Ошибка!", "Email уже существует")
                        else:
                            cursor.execute(
                                '''UPDATE patients SET first_name = ?, last_name = ?, date_of_birth = ?, gender = ?, address = ?, phone_number = ?, email = ? WHERE patient_id = ?''',
                                new_patient_data)
                            conn.commit()
                            messagebox.showinfo("Успех!", "Пациент изменен!")
                            self.load_patients()
                        conn.close()
                except Exception as e:
                    messagebox.showerror("Ошибка в диалоге!", f"Ошибка: {e}")

            except sqlite3.Error as e:
                messagebox.showerror("Ошибка с базой данных!", f"Ошибка: {e}")
            except Exception as e:
                messagebox.showerror("Ошибка!", f"Произошла непредвиденная ошибка: {e}")
        else:
            messagebox.showwarning("Предупреждение!", "Выберите пациента для редактирования")

    def get_patient_data_from_dialog(self, initial_data):
        root = tk.Toplevel(self.master)
        root.title("Редактирование пациента")

        labels = ["Имя-Отчество:", "Фамилия:", "Дата рождения:", "Пол:", "Адрес:", "Номер телефона:",
                  "Почта:"]
        entries = []
        for i, label_text in enumerate(labels):
            ttk.Label(root, text=label_text).grid(row=i, column=0, sticky=tk.W)
            entry = ttk.Entry(root)
            entry.insert(0, initial_data[i + 1] if initial_data else "")
            entry.grid(row=i, column=1)
            entries.append(entry)

        # Кнопки "OK" и "Cancel"
        ok_button = ttk.Button(root, text="OK", command=lambda: self.save_patient_data(root, initial_data, entries))
        cancel_button = ttk.Button(root, text="Cancel", command=root.destroy)
        ok_button.grid(row=len(labels), column=0)
        cancel_button.grid(row=len(labels), column=1)

        root.wait_window()

    def on_ok(self, root, entries, data):
        try:
            data = [entry.get() for entry in entries]
            if not all(data[0:2] + [data[-1]]):
                messagebox.showerror("Ошибка", "Поля Имя, Фамилия и Email обязательны.")
                return

            root.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка обработки данных: {e}")

    def save_patient_data(self, root, initial_data, entries):
        try:
            patient_data = (initial_data[0],) + tuple(entry.get() for entry in entries)
            if len(patient_data) != 8:  # проверка на количество полей
                raise ValueError("Не все поля заполнены")

            patient = Patient(*patient_data[1:])  # соз
            # даем объект patient для валидации
            if patient.is_valid():
                conn = sqlite3.connect('health_monitoring.db')
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM patients WHERE email = ? AND patient_id != ?",
                               (patient_data[7], patient_data[0]))
                if cursor.fetchone()[0] > 0:
                    messagebox.showerror("Ошибка!", "Email уже существует")
                else:
                    cursor.execute(
                        '''UPDATE patients SET first_name = ?, last_name = ?, date_of_birth = ?, gender = ?, address = ?, phone_number = ?, email = ? WHERE patient_id = ?''',
                        patient_data)
                    conn.commit()
                    messagebox.showinfo("Успех!", "Пациент изменен!")
                    self.load_patients()
                conn.close()
            else:
                messagebox.showerror("Ошибка!", "Некорректные данные")
            root.destroy()
        except ValueError as e:
            messagebox.showerror("Ошибка!", f"Ошибка: {e}")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка с базой данных!", f"Ошибка: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка!", f"Произошла непредвиденная ошибка: {e}")

    def save_patient_data(self, root, initial_data, entries):
        try:
            # Собирать данные пациента из полей ввода
            patient_data = (initial_data[0],) + tuple(entry.get() for entry in entries)  # Добавляем patient_id к данным
            if len(patient_data) != 8:  # Проверка на количество полей
                raise ValueError("Не все поля заполнены")

            patient = Patient(*patient_data[1:])  # Создаем объект patient для валидации
            if patient.is_valid():
                conn = sqlite3.connect('health_monitoring.db')
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM patients WHERE email = ? AND patient_id != ?",
                               (patient_data[7], patient_data[0]))  # Проверка уникальности email
                if cursor.fetchone()[0] > 0:
                    messagebox.showerror("Ошибка!", "Email уже существует")
                else:
                    # Здесь используем параметр patient_data + передаем patient_id в конце
                    cursor.execute(
                        '''UPDATE patients SET first_name = ?, last_name = ?, date_of_birth = ?, gender = ?, address = ?, phone_number = ?, email = ? WHERE patient_id = ?''',
                        (patient_data[1], patient_data[2], patient_data[3], patient_data[4], patient_data[5],
                         patient_data[6], patient_data[7], patient_data[0]))
                    conn.commit()
                    messagebox.showinfo("Успех!", "Пациент изменен!")
                    self.load_patients()  # Перезагрузка списка пациентов
                conn.close()
            else:
                messagebox.showerror("Ошибка!", "Некорректные данные")
            root.destroy()
        except ValueError as e:
            messagebox.showerror("Ошибка!", f"Ошибка: {e}")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка с базой данных!", f"Ошибка: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка!", f"Произошла непредвиденная ошибка: {e}")

    def open_doctor_app(self):
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pp-doctor.py")

        try:
            python_executable = sys.executable

            subprocess.Popen([python_executable, script_path])
        except FileNotFoundError:
            messagebox.showerror("Ошибка", f"Файл не найден: '{script_path}'")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при запуске приложения: {e}")

    def on_patient_select(self, event):
        widget = event.widget
        selection = widget.curselection()
        if selection:
            index = selection[0]
            value = widget.get(index)
            patient_id = int(value.split(" - ")[0])
            self.show_health_data(patient_id)

    def show_health_data(self, patient_id):
        health_data_window = tk.Toplevel(self.master)
        health_data_window.title(f"Данные о здоровье пациента {patient_id}")

        health_data_listbox = tk.Listbox(health_data_window, width=50)
        health_data_listbox.pack(fill=tk.BOTH, expand=True)

        conn = None
        try:
            conn = sqlite3.connect('health_monitoring.db')
            cursor = conn.cursor()
            cursor.execute("SELECT measurement_date, weight, body_temperature, blood_pressure, heart_rate, notes FROM health_data WHERE patient_id = ?",
                           (patient_id,))
            health_data = cursor.fetchall()
            for row in health_data:
                health_data_listbox.insert(tk.END, " - ".join(map(str, row)))
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка БД", f"Ошибка загрузки данных о здоровье: {e}")
        finally:
            if conn:
                conn.close()

    def on_patient_select(self, event):
        widget = event.widget
        selection = widget.curselection()
        if selection:
            index = selection[0]
            value = widget.get(index)
            self.patient_id = int(value.split(" - ")[0])  # Store patient_id
            self.show_health_data(self.patient_id)

    def show_health_data(self, patient_id):
        health_data_window = tk.Toplevel(self.master)
        health_data_window.title(f"Данные о здоровье пациента {patient_id}")

        # Health data listbox
        self.health_data_listbox = tk.Listbox(health_data_window, width=50)
        self.health_data_listbox.pack(fill=tk.BOTH, expand=True)
        self.load_health_data(patient_id)

        #Buttons for managing health data
        ttk.Button(health_data_window, text="Добавить запись", command=lambda: self.add_health_record(patient_id)).pack()
        ttk.Button(health_data_window, text="Редактировать запись", command=lambda: self.edit_health_record(patient_id)).pack()
        ttk.Button(health_data_window, text="Удалить запись", command=lambda: self.delete_health_record(patient_id)).pack()



    def load_health_data(self, patient_id):
        self.health_data_listbox.delete(0, tk.END)
        conn = None
        try:
            conn = sqlite3.connect('health_monitoring.db')
            cursor = conn.cursor()
            cursor.execute("SELECT data_id, measurement_date, heart_rate, blood_pressure, body_temperature, weight, notes FROM health_data WHERE patient_id = ?", (patient_id,))
            health_data = cursor.fetchall()
            for row in health_data:
                self.health_data_listbox.insert(tk.END, row) #Simplified display for now
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка БД", f"Ошибка загрузки данных о здоровье: {e}")
        finally:
            if conn:
                conn.close()


    def add_health_record(self, patient_id):
        self.show_health_record_dialog(patient_id, "Добавить запись")

    def edit_health_record(self, patient_id):
        selection = self.health_data_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите запись для редактирования.")
            return

        record_id = self.health_data_listbox.get(selection[0])[0]  # Get record ID

        conn = None
        try:
            conn = sqlite3.connect('health_monitoring.db')
            cursor = conn.cursor()
            cursor.execute("SELECT measurement_date, heart_rate, blood_pressure, body_temperature, weight, notes FROM health_data WHERE data_id = ?", (record_id,))
            record = cursor.fetchone()
            conn.close()

            if record:
                # Create a dialog for editing
                edit_window = tk.Toplevel(self.master)
                edit_window.title("Редактирование записи")

                # Input fields pre-filled with existing data
                measurement_date_entry = DateEntry(edit_window, width=17, background='darkblue', foreground='white',
                                       borderwidth=2)  # tkcalendar DateEntry
                measurement_date_entry.insert(0, record[0])
                measurement_date_entry.grid(row=0, column=1)

                heart_rate_entry = ttk.Entry(edit_window)
                heart_rate_entry.insert(0, record[1])
                heart_rate_entry.grid(row=1, column=1)

                blood_pressure_entry = ttk.Entry(edit_window)
                blood_pressure_entry.insert(0, record[2])
                blood_pressure_entry.grid(row=2, column=1)

                body_temperature_entry = ttk.Entry(edit_window)
                body_temperature_entry.insert(0, record[3])
                body_temperature_entry.grid(row=3, column=1)

                weight_entry = ttk.Entry(edit_window)
                weight_entry.insert(0, record[4])
                weight_entry.grid(row=4, column=1)

                notes_entry = ttk.Entry(edit_window)
                notes_entry.insert(0, record[5])
                notes_entry.grid(row=5, column=1)

                ttk.Label(edit_window, text="Дата (YYYY-MM-DD):").grid(row=0, column=0)
                ttk.Label(edit_window, text="ЧСС:").grid(row=1, column=0)
                ttk.Label(edit_window, text="Давление:").grid(row=2, column=0)
                ttk.Label(edit_window, text="Температура:").grid(row=3, column=0)
                ttk.Label(edit_window, text="Вес:").grid(row=4, column=0)
                ttk.Label(edit_window, text="Примечания:").grid(row=5, column=0)

                # Save button
                ttk.Button(edit_window, text="Сохранить",
                           command=lambda: self.save_health_record(patient_id, measurement_date_entry.get(),
                                                                  heart_rate_entry.get(),
                                                                   blood_pressure_entry.get(),
                                                                  body_temperature_entry.get(), weight_entry.get(), notes_entry.get(), record_id, edit_window)).grid(
                    row=6, column=0, columnspan=2)

            else:
                messagebox.showerror("Ошибка", "Запись не найдена.")

        except IndexError:
            messagebox.showerror("Ошибка", "Ошибка выбора записи.")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка БД", f"Ошибка загрузки данных записи: {e}")
        finally:
            if conn:
                conn.close()



    def delete_health_record(self, patient_id):
        selection = self.health_data_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления.")
            return

        record_id = self.health_data_listbox.get(selection[0])[0]
        if messagebox.askyesno("Подтверждение", f"Удалить запись с ID {record_id}?"):
            conn = None
            try:
                conn = sqlite3.connect('health_monitoring.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM health_data WHERE data_id = ?", (record_id,))
                conn.commit()
                messagebox.showinfo("Успех", "Запись удалена.")
                self.load_health_data(patient_id)
            except sqlite3.Error as e:
                messagebox.showerror("Ошибка БД", f"Ошибка удаления записи: {e}")
            finally:
                if conn:
                    conn.close()


    def show_health_record_dialog(self, patient_id, title, record_id=None):
        dialog = tk.Toplevel(self.master)
        dialog.title(title)

        #Input fields
        measurement_date_entry = DateEntry(dialog, width=17, background='darkblue', foreground='white', borderwidth=2)
        heart_rate_entry = ttk.Entry(dialog)
        blood_pressure_entry = ttk.Entry(dialog)
        body_temperature_entry = ttk.Entry(dialog)
        weight_entry = ttk.Entry(dialog)
        notes_entry = ttk.Entry(dialog)

        measurement_date_entry.grid(row=0, column=1)
        heart_rate_entry.grid(row=1, column=1)
        blood_pressure_entry.grid(row=2, column=1)
        body_temperature_entry.grid(row=3, column=1)
        weight_entry.grid(row=4, column=1)
        notes_entry.grid(row=5, column=1)

        ttk.Label(dialog, text="Дата (YYYY-MM-DD):").grid(row=0, column=0)
        ttk.Label(dialog, text="ЧСС:").grid(row=1, column=0)
        ttk.Label(dialog, text="Давление:").grid(row=2, column=0)
        ttk.Label(dialog, text="Температура:").grid(row=3, column=0)
        ttk.Label(dialog, text="Вес:").grid(row=4, column=0)
        ttk.Label(dialog, text="Примечания:").grid(row=5, column=0)


        if record_id:
            conn = sqlite3.connect('health_monitoring.db')
            cursor = conn.cursor()
            cursor.execute("SELECT date_id, measurement_date, heart_rate, blood_pressure, body_temperature, weight, notes FROM health_data WHERE data_id = ?", (record_id,))
            record = cursor.fetchone()
            conn.close()
            if record:
                measurement_date_entry.insert(0, record[0])
                heart_rate_entry.insert(0, record[1])
                blood_pressure_entry.insert(0, record[2])
                body_temperature_entry.insert(0, record[3])
                weight_entry.insert(0, record[4])
                notes_entry.insert(0, record[5])

        ttk.Button(dialog, text="Сохранить", command=lambda: self.save_health_record(patient_id, measurement_date_entry.get(), heart_rate_entry.get(), blood_pressure_entry.get(), body_temperature_entry.get(), weight_entry.get(),  notes_entry.get(), record_id, dialog)).grid(row=6, column=0, columnspan=2)

    def save_health_record(self, patient_id, measurement_date, heart_rate, blood_pressure, body_temperature,  weight, notes, record_id=None, dialog=None):
        conn = None
        try:
            conn = sqlite3.connect('health_monitoring.db')
            cursor = conn.cursor()
            if record_id:
                cursor.execute("UPDATE health_data SET measurement_date = ?, blood_pressure = ?, body_temperature = ?, heart_rate = ?, weight = ?, notes = ? WHERE data_id = ?",
                               (measurement_date, heart_rate, blood_pressure, body_temperature,  weight, notes, record_id))
            else:
                cursor.execute("INSERT INTO health_data (patient_id, measurement_date, heart_rate, blood_pressure, body_temperature, weight, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
                               (patient_id, measurement_date, heart_rate, blood_pressure, body_temperature,  weight, notes))
            conn.commit()
            messagebox.showinfo("Успех", "Запись сохранена!")
            self.load_health_data(self.patient_id)
            if dialog:
                dialog.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка БД", f"Ошибка сохранения записи: {e}")
        finally:
            if conn:
                conn.close()

def load_patients(self):
    self.patients_listbox.delete(0, tk.END)
    conn = sqlite3.connect('health_monitoring.db')
    cursor = conn.cursor()
    cursor.execute("SELECT patient_id, first_name, last_name FROM patients")
    patients = cursor.fetchall()
    for patient_id, first_name, last_name in patients:
        self.patients_listbox.insert(tk.END, f"{patient_id} - {first_name} {last_name}")
    conn.close()


root = tk.Tk()
app = App(root)
root.mainloop()