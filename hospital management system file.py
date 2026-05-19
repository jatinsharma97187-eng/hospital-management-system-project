import sqlite3
import os


def init_db():
    connect = sqlite3.connect("hospital.db")
    cur = connect.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialty TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            available TEXT DEFAULT 'Yes'
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            disease TEXT,
            doctor_id INTEGER,
            phone TEXT,
            admitted TEXT DEFAULT 'Yes',
            FOREIGN KEY (doctor_id) REFERENCES doctors(id)
        )
    """)
    connect.commit()
    connect.close()

# Helper
def get_connect():
    return sqlite3.connect("hospital.db")

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input("\nPress Enter to continue...")


# DOCTOR FUNCTIONS

def adddoc():
    print("\nAdd Doctor ─>>")
    n = int(input("How many doctors to add? "))
    connect = get_connect()

    for i in range(n):
        name = input("Name : ").strip()
        specialty = input("Specialty : ").strip()
        phone = input("Phone : ").strip()
        email = input("Email : ").strip()

        if not name or not specialty:
            print("Name and specialty are required.")
            pause()
            return

        connect.execute(
            "INSERT INTO doctors (name, specialty, phone, email) VALUES (?,?,?,?)",
            (name, specialty, phone, email)
        )
    connect.commit()
    connect.close()
    print(f"\n✔ Dr. {name} added successfully.")
    pause()


def viewdoc():
    print("\n── All Doctors ──")
    connect = get_connect()
    rows = connect.execute("SELECT * FROM doctors").fetchall()
    connect.close()

    if not rows:
        print("No doctors found.")

    else:
        print(f"\n{'ID':<5} {'Name':<25} {'Specialty':<20} {'Phone':<15} {'Email':<25} {'Available'}")
        print("-" * 100)
        for r in rows:
            print(f"{r[0]:<5} {r[1]:<25} {r[2]:<20} {r[3]:<15} {r[4]:<25} {r[5]}")

    pause()


def updatedoc():
    viewdoc()
    try:
        did = int(input("\nEnter Doctor ID to update: "))
    except ValueError:
        print("Invalid ID.")
        pause()
        return
    connect = get_connect()
    doc = connect.execute("SELECT * FROM doctors WHERE id=?", (did,)).fetchone()

    if not doc:
        print("Doctor not found.")
        connect.close()
        pause()
        return
    print(f"\nUpdating Dr. {doc[1]} (press Enter to keep current value)")
    name = input(f"Name [{doc[1]}] : ").strip() or doc[1]
    specialty = input(f"Specialty [{doc[2]}] : ").strip() or doc[2]
    phone = input(f"Phone [{doc[3]}] : ").strip() or doc[3]
    email = input(f"Email [{doc[4]}] : ").strip() or doc[4]
    available = input(f"Available [{doc[5]}] : ").strip() or doc[5]
    connect.execute(
        "UPDATE doctors SET name=?, specialty=?, phone=?, email=?, available=? WHERE id=?",
        (name, specialty, phone, email, available, did)
    )

    connect.commit()
    connect.close()
    print("✔ Doctor record updated.")
    pause()


def deletedoc():
    viewdoc()
    try:
        did = int(input("\nEnter Doctor ID to delete: "))

    except ValueError:
        print("Invalid ID.")
        pause()
        return

    connect = get_connect()
    doc = connect.execute("SELECT name FROM doctors WHERE id=?", (did,)).fetchone()

    if not doc:
        print("Doctor not found.")
        connect.close()
        pause()
        return

    confirm = input(f"Delete Dr. {doc[0]}? (yes/no): ").strip().lower()

    if confirm == 'yes':
        connect.execute("DELETE FROM doctors WHERE id=?", (did,))
        connect.commit()
        print("✔ Doctor deleted.")

    else:
        print("Cancelled.")

    connect.close()
    pause()


def searchdoc():
    term = input("\nSearch doctor by name or specialty: ").strip()
    connect = get_connect()
    rows = connect.execute(
        "SELECT * FROM doctors WHERE name LIKE ? OR specialty LIKE ?",
        (f"%{term}%", f"%{term}%")
    ).fetchall()
    connect.close()
    if not rows:
        print("No results found.")
    else:
        print(f"\n{'ID':<5} {'Name':<25} {'Specialty':<20} {'Phone':<15} {'Email':<25} {'Available'}")
        print("-" * 100)
        for r in rows:
            print(f"{r[0]:<5} {r[1]:<25} {r[2]:<20} {r[3]:<15} {r[4]:<25} {r[5]}")

    pause()


# PATIENT FUNCTIONS

def addpatient():
    print("\nAdd Patient->>")
    n = int(input("How many patients to add? "))
    connect = get_connect()

    for i in range(n):
        name = input("Name : ").strip()
        age = input("Age : ").strip()
        gender = input("Gender : ").strip()
        disease = input("Disease : ").strip()
        phone = input("Phone : ").strip()
        docs = connect.execute(
            "SELECT id, name, specialty FROM doctors WHERE available='Yes'"
        ).fetchall()
        if docs:
            print("\nAvailable Doctors:")
            for d in docs:
                print(f" [{d[0]}] Dr. {d[1]} — {d[2]}")

            try:
                doctor_id = int(
                    input("Assign Doctor ID (0 for none): ").strip()
                )

            except ValueError:
                doctor_id = None

        else:
            print("No doctors available currently.")
            doctor_id = None

        if not name:
            print("Patient name is required.")
            pause()
            return
        connect.execute(
            """
            INSERT INTO patients
            (name, age, gender, disease, doctor_id, phone)
            VALUES (?,?,?,?,?,?)
            """,
            (
                name,
                age or None,
                gender,
                disease,
                doctor_id or None,
                phone
            )
        )

    connect.commit()
    connect.close()
    print(f"\n✔ {n} patient(s) admitted successfully.")
    pause()


def viewpatients():
    print("\n── All Patients ──")
    connect = get_connect()

    rows = connect.execute("""
        SELECT p.id, p.name, p.age, p.gender, p.disease,
               COALESCE('Dr. ' || d.name, 'Unassigned') as doctor,
               p.phone, p.admitted
        FROM patients p
        LEFT JOIN doctors d ON p.doctor_id = d.id
    """).fetchall()
    connect.close()

    if not rows:
        print("No patients found.")

    else:
        print(f"\n{'ID':<5} {'Name':<20} {'Age':<5} {'Gender':<8} {'Disease':<18} {'Doctor':<22} {'Phone':<15} {'Admitted'}")
        print("-" * 110)

        for r in rows:
            print(f"{r[0]:<5} {r[1]:<20} {str(r[2]):<5} {r[3]:<8} {r[4]:<18} {r[5]:<22} {r[6]:<15} {r[7]}")
    pause()


def updatepatient():
    viewpatients()
    try:
        pid = int(input("\nEnter Patient ID to update: "))
    except ValueError:
        print("Invalid ID.")
        pause()
        return
    connect = get_connect()
    pat = connect.execute("SELECT * FROM patients WHERE id=?", (pid,)).fetchone()
    if not pat:
        print("Patient not found.")
        connect.close()
        pause()
        return
    print(f"\nUpdating {pat[1]} (press Enter to keep current value)")
    name = input(f"Name [{pat[1]}] : ").strip() or pat[1]
    age = input(f"Age [{pat[2]}] : ").strip() or pat[2]
    gender = input(f"Gender [{pat[3]}] : ").strip() or pat[3]
    disease = input(f"Disease [{pat[4]}] : ").strip() or pat[4]
    phone = input(f"Phone [{pat[6]}] : ").strip() or pat[6]
    admitted = input(f"Admitted [{pat[7]}] : ").strip() or pat[7]
    connect.execute(
        "UPDATE patients SET name=?, age=?, gender=?, disease=?, phone=?, admitted=? WHERE id=?",
        (name, age, gender, disease, phone, admitted, pid)
    )
    connect.commit()
    connect.close()
    print("✔ Patient record updated.")
    pause()


def deletepatient():
    viewpatients()
    try:
        pid = int(input("\nEnter Patient ID to delete: "))

    except ValueError:
        print("Invalid ID.")
        pause()
        return

    connect = get_connect()
    pat = connect.execute("SELECT name FROM patients WHERE id=?", (pid,)).fetchone()
    if not pat:
        print("Patient not found.")
        connect.close()
        pause()
        return
    confirm = input(f"Delete record of {pat[0]}? (yes/no): ").strip().lower()

    if confirm == 'yes':
        connect.execute("DELETE FROM patients WHERE id=?", (pid,))
        connect.commit()
        print("✔ Patient record deleted.")
    else:
        print("Cancelled.")
    connect.close()
    pause()


def searchpatient():
    term = input("\nSearch patient by name or disease: ").strip()
    connect = get_connect()
    rows = connect.execute("""
        SELECT p.id, p.name, p.age, p.gender, p.disease,
               COALESCE('Dr. ' || d.name, 'Unassigned') as doctor,
               p.phone, p.admitted
        FROM patients p
        LEFT JOIN doctors d ON p.doctor_id = d.id
        WHERE p.name LIKE ? OR p.disease LIKE ?
    """, (f"%{term}%", f"%{term}%")).fetchall()

    connect.close()

    if not rows:
        print("No results found.")

    else:
        print(f"\n{'ID':<5} {'Name':<20} {'Age':<5} {'Gender':<8} {'Disease':<18} {'Doctor':<22} {'Phone':<15} {'Admitted'}")
        print("-" * 110)
        for r in rows:
            print(f"{r[0]:<5} {r[1]:<20} {str(r[2]):<5} {r[3]:<8} {r[4]:<18} {r[5]:<22} {r[6]:<15} {r[7]}")

    pause()


# MENUS

def doctor_menu():

    while True:

        clear()

        print("╔══════════════════════════════╗")
        print("║       DOCTOR MANAGEMENT      ║")
        print("╠══════════════════════════════╣")
        print("║  1. Add Doctor               ║")
        print("║  2. View All Doctors         ║")
        print("║  3. Update Doctor            ║")
        print("║  4. Delete Doctor            ║")
        print("║  5. Search Doctor            ║")
        print("║  0. Back                     ║")
        print("╚══════════════════════════════╝")

        choice = input("Enter choice: ").strip()

        if choice == '1':
            adddoc()

        elif choice == '2':
            viewdoc()

        elif choice == '3':
            updatedoc()

        elif choice == '4':
            deletedoc()

        elif choice == '5':
            searchdoc()

        elif choice == '0':
            break

        else:
            print("Invalid option.")
            pause()


def patient_menu():

    while True:

        clear()

        print("╔══════════════════════════════╗")
        print("║      PATIENT MANAGEMENT      ║")
        print("╠══════════════════════════════╣")
        print("║  1. Add Patient              ║")
        print("║  2. View All Patients        ║")
        print("║  3. Update Patient           ║")
        print("║  4. Delete Patient           ║")
        print("║  5. Search Patient           ║")
        print("║  0. Back                     ║")
        print("╚══════════════════════════════╝")

        choice = input("Enter choice: ").strip()

        if choice == '1':
            addpatient()

        elif choice == '2':
            viewpatients()

        elif choice == '3':
            updatepatient()

        elif choice == '4':
            deletepatient()

        elif choice == '5':
            searchpatient()

        elif choice == '0':
            break

        else:
            print("Invalid option.")
            pause()


def main_menu():
    init_db()
    while True:

        clear()

        print("╔══════════════════════════════════╗")
        print("║    HOSPITAL MANAGEMENT SYSTEM    ║")
        print("╠══════════════════════════════════╣")
        print("║  1. Doctor Management            ║")
        print("║  2. Patient Management           ║")
        print("║  0. Exit                         ║")
        print("╚══════════════════════════════════╝")

        choice = input("Enter choice: ").strip()

        if choice == '1':
            doctor_menu()

        elif choice == '2':
            patient_menu()

        elif choice == '0':
            print("\nGoodbye!")
            break

        else:
            print("Invalid option.")
            pause()


if __name__ == "__main__":

    main_menu()