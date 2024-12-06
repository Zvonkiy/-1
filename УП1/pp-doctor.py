import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

def create_doctor_db_and_tables(db_name="health_monitoring.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS doctors (
            doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            speciality TEXT,
            contact_info TEXT,
        )''')
        conn.commit()
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred creating doctors table: {e}")
    finally:
        conn.close()

create_doctor_db_and_tables()

class Doctor:
    def __init__(self, first_name, last_name, speciality, contact_info):
        self.first_name = first_name
        self.last_name = last_name
        self.speciality = speciality
        self.contact_info = contact_info

class DoctorApp:
    def __init__(self, master):
        self.master = master
        master.title("Doctor Management System")
        self.create_widgets()
        self.load_doctors()

    def load_doctors(self):
        self.doctors_listbox.delete(0, tk.END)
        conn = None
        try:
            conn = sqlite3.connect('health_monitoring.db')
            cursor = conn.cursor()
            cursor.execute("SELECT doctor_id, first_name, last_name FROM doctors")
            doctors = cursor.fetchall()
            for doctor_id, first_name, last_name in doctors:
                self.doctors_listbox.insert(tk.END, f"{doctor_id} - {first_name} {last_name}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading doctors: {e}")
        finally:
            if conn:
                conn.close()

    def create_widgets(self):
        # Labels and Entry fields
        ttk.Label(self.master, text="Имя:").grid(row=0, column=0, sticky=tk.W)
        self.first_name_entry = ttk.Entry(self.master)
        self.first_name_entry.grid(row=0, column=1)
        ttk.Label(self.master, text="Фамилия:").grid(row=1, column=0, sticky=tk.W)
        self.last_name_entry = ttk.Entry(self.master)
        self.last_name_entry.grid(row=1, column=1)
        ttk.Label(self.master, text="Специальность:").grid(row=2, column=0, sticky=tk.W)
        self.speciality_entry = ttk.Entry(self.master)
        self.speciality_entry.grid(row=2, column=1)
        ttk.Label(self.master, text="Контактная информация:").grid(row=3, column=0, sticky=tk.W)
        self.contact_info_entry = ttk.Entry(self.master)
        self.contact_info_entry.grid(row=3, column=1)


        # Buttons
        ttk.Button(self.master, text="Добавить врача", command=self.add_doctor).grid(row=5, column=0, columnspan=2)
        ttk.Button(self.master, text="Удалить врача", command=self.delete_doctor).grid(row=6, column=0, columnspan=2)
        ttk.Button(self.master, text="Просмотреть и отредактировать запись", command=self.edit_doctor).grid(row=7, column=0,
                                                                                            columnspan=2)
        self.doctors_listbox = tk.Listbox(self.master)
        self.doctors_listbox.grid(row=8, column=0, columnspan=2)

    def add_doctor(self):
        conn = None
        try:
            first_name = self.first_name_entry.get()
            last_name = self.last_name_entry.get()
            speciality = self.speciality_entry.get()
            contact_info = self.contact_info_entry.get()

            if not all([first_name, last_name]):  # Basic input validation
                messagebox.showerror("Ошибка", "Имя и фамилия  обязательны.")
                return

            doctor = Doctor(first_name, last_name, speciality, contact_info)
            conn = sqlite3.connect('health_monitoring.db')
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO doctors (first_name, last_name, speciality, contact_info) VALUES (?, ?, ?, ?)",
                (doctor.first_name, doctor.last_name, doctor.speciality, doctor.contact_info))
            conn.commit()
            messagebox.showinfo("Успех", "Врач добавлен!")
            self.load_doctors()
            self.clear_entries()
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Email уже существует!")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка БД", f"Ошибка добавления врача: {e}")
        finally:
            if conn:
                conn.close()

    def delete_doctor(self):
        try:
            selection = self.doctors_listbox.curselection()
            if not selection:
                messagebox.showwarning("Предупреждение", "Выберите врача для удаления.")
                return

            index = selection[0]
            doctor_info = self.doctors_listbox.get(index)
            doctor_id = int(doctor_info.split(" - ")[0])

            if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить врача {doctor_info}?"):
                conn = sqlite3.connect('health_monitoring.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM doctors WHERE doctor_id = ?", (doctor_id,))
                conn.commit()
                messagebox.showinfo("Успех", "Врач удален.")
                self.load_doctors()  # Refresh the listbox
        except IndexError:
            messagebox.showerror("Ошибка", "Ошибка выбора врача.")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка БД", f"Ошибка удаления врача: {e}")
        finally:
            if conn:
                conn.close()


    def edit_doctor(self):
        try:
            selection = self.doctors_listbox.curselection()
            if not selection:
                messagebox.showwarning("Предупреждение", "Выберите врача для редактирования.")
                return

            index = selection[0]
            doctor_info = self.doctors_listbox.get(index)
            doctor_id = int(doctor_info.split(" - ")[0])

            conn = sqlite3.connect('health_monitoring.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM doctors WHERE doctor_id = ?", (doctor_id,))
            doctor_data = cursor.fetchone()
            conn.close()

            if doctor_data:
                edit_window = tk.Toplevel(self.master)
                edit_window.title("Редактирование врача")


                ttk.Label(edit_window, text="Имя:").grid(row=0, column=0, sticky=tk.W)
                first_name_entry = ttk.Entry(edit_window)
                first_name_entry.insert(0, doctor_data[1])
                first_name_entry.grid(row=0, column=1)

                ttk.Label(edit_window, text="Фамилия:").grid(row=1, column=0, sticky=tk.W)
                last_name_entry = ttk.Entry(edit_window)
                last_name_entry.insert(0, doctor_data[2])
                last_name_entry.grid(row=1, column=1)

                ttk.Label(edit_window, text="Специальность:").grid(row=2, column=0, sticky=tk.W)
                speciality_entry = ttk.Entry(edit_window)
                speciality_entry.insert(0, doctor_data[3])
                speciality_entry.grid(row=2, column=1)

                ttk.Label(edit_window, text="Контактная информация:").grid(row=3, column=0, sticky=tk.W)
                contact_info_entry = ttk.Entry(edit_window)
                contact_info_entry.insert(0, doctor_data[4])
                contact_info_entry.grid(row=3, column=1)

                ttk.Button(edit_window, text="Сохранить", command=lambda: self.save_doctor_changes(doctor_id, first_name_entry.get(), last_name_entry.get(), speciality_entry.get(), contact_info_entry.get(), edit_window)).grid(row=5, column=0, columnspan=2)

            else:
                messagebox.showerror("Ошибка", "Врач не найден.")

        except IndexError:
            messagebox.showerror("Ошибка", "Ошибка выбора врача.")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка БД", f"Ошибка загрузки данных врача: {e}")



    def save_doctor_changes(self, doctor_id, first_name, last_name, speciality, contact_info, edit_window):
        conn = None
        try:
            if not all([first_name, last_name]):
                messagebox.showerror("Ошибка", "Имя и фамилия обязательны.")
                return

            conn = sqlite3.connect('health_monitoring.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE doctors SET first_name = ?, last_name = ?, speciality = ?, contact_info = ? WHERE doctor_id = ?",
                           (first_name, last_name, speciality, contact_info, doctor_id))
            conn.commit()
            messagebox.showinfo("Успех", "Данные врача обновлены!")
            self.load_doctors()
            edit_window.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Email уже существует!")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка БД", f"Ошибка обновления данных врача: {e}")
        finally:
            if conn:
                conn.close()

    def clear_entries(self):
        self.first_name_entry.delete(0, tk.END)
        self.last_name_entry.delete(0, tk.END)
        self.speciality_entry.delete(0, tk.END)
        self.contact_info_entry.delete(0, tk.END)

root = tk.Tk()
app = DoctorApp(root)
root.mainloop()