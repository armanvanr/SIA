from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from flask_migrate import Migrate

# FLASK AND POSTGRESQL CONFIGURATIONS
# load environment variables (username and password of postgreSQL account)
load_dotenv()
username = os.environ["USER_NAME"]
password = os.environ["PASSWORD"]

# configuration Flask and connect to postgreSQL
app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"postgresql://{username}:{password}@localhost:5432/sia"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
db = SQLAlchemy(app)

migrate = Migrate(app, db)


# SCHEMAS
# table Mata_Kuliah
class Mata_Kuliah(db.Model):
    __tablename__ = "mata_kuliah"
    kode_mk = db.Column(db.String, primary_key=True, nullable=False, unique=True)
    nama_mk = db.Column(db.String, nullable=False)
    sks = db.Column(db.Integer, nullable=False)
    list_kelas = db.relationship("Kelas", backref="mata_kuliah", lazy="dynamic")

    def __repr__(self):
        return f"Matkul <{self.nama_mk}>"


# table Mahasiswa
class Mahasiswa(db.Model):
    __tablename__ = "mahasiswa"
    nim = db.Column(db.String, primary_key=True, nullable=False, unique=True)
    nama_mhs = db.Column(db.String, nullable=False)
    gender_mhs = db.Column(db.String, nullable=False)
    telp_mhs = db.Column(db.String, nullable=False, unique=True)
    email_mhs = db.Column(db.String, nullable=False, unique=True)

    def __repr__(self):
        return f"<Matkul {self.nama_mhs}>"


# table Dosen
class Dosen(db.Model):
    __tablename__ = "dosen"
    nip = db.Column(db.String, primary_key=True, nullable=False, unique=True)
    nama_dosen = db.Column(db.String, nullable=False)
    gender_dosen = db.Column(db.String, nullable=False)
    telp_dosen = db.Column(db.String, nullable=False, unique=True)
    email_dosen = db.Column(db.String, nullable=False, unique=True)
    list_kelas = db.relationship("Kelas", backref="dosen", lazy="dynamic")

    def __repr__(self):
        return f"<Matkul {self.nama_dosen}>"


# table Kelas
class Kelas(db.Model):
    __tablename__ = "kelas"
    kode_kelas = db.Column(
        db.Integer, primary_key=True, nullable=False, autoincrement=True
    )
    nama_kelas = db.Column(db.String, nullable=False)
    nip = db.Column(db.String, db.ForeignKey("dosen.nip"), nullable=False)
    kode_mk = db.Column(db.String, db.ForeignKey("mata_kuliah.kode_mk"), nullable=False)
    hari = db.Column(db.String, nullable=False)
    jam = db.Column(db.Time, nullable=False)

    def __repr__(self):
        return f"<Kelas {self.kode_kelas}>"


# table Kelas Ampu
class Kelas_Ampu(db.Model):
    __tablename__ = "kelas_ampu"
    kode_kelas = db.Column(
        db.Integer, db.ForeignKey("kelas.kode_kelas"), primary_key=True, nullable=False
    )
    nim = db.Column(
        db.String, db.ForeignKey("mahasiswa.nim"), primary_key=True, nullable=False
    )

    def __repr__(self):
        return f"<Kelas Ampu {self.kode_kelas}>"


# AUTH
def login():
    id = request.authorization.get("username")
    mahasiswa = Mahasiswa.query.get(id)
    dosen = Dosen.query.get(id)
    if mahasiswa:
        return "mahasiswa"
    elif dosen:
        return "dosen"


# ROUTES
# Mata_Kuliah/Courses
# retrieve details of all courses
@app.get("/courses")
def get_courses():
    res = [
        {"kode": matkul.kode_mk, "mata_kuliah": matkul.nama_mk, "sks": matkul.sks}
        for matkul in Mata_Kuliah.query.all()
    ]
    return jsonify(res)


# get course and delete course
@app.route("/course/<code>", methods=["GET", "DELETE"])
def get_delete_course(code):
    course = Mata_Kuliah.query.filter_by(kode_mk=code).first()

    # check if a specific course exists
    if not course:
        return {"message": "Course not found"}, 404

    # retrieve that specific course
    if request.method == "GET":
        res = {"kode": course.kode_mk, "mata_kuliah": course.nama_mk, "sks": course.sks}
        return jsonify(res)

    # delete that specific course
    elif request.method == "DELETE":
        db.session.delete(course)
        db.session.commit()
        return {"message": "Course deleted"}


# add course and update course
@app.route("/course", methods=["POST", "PUT"])
def add_update_course():
    data = request.get_json()

    # add a new course
    if request.method == "POST":
        # check the field data
        if any([not "kode" in data, not "nama" in data, not "sks" in data]):
            return {"error": "Bad Request: Missing field(s)"}, 400

        # check if a course already exists
        course = Mata_Kuliah.query.filter_by(kode_mk=data["kode"]).first()
        if course:
            return {"error": "Course already exists"}, 400

        # create a new instance of Mata Kuliah
        new_course = Mata_Kuliah(
            kode_mk=data["kode"], nama_mk=data["nama"], sks=data["sks"]
        )
        db.session.add(new_course)
        db.session.commit()
        return {"message": "Course added"}, 201

    # update an existing course
    elif request.method == "PUT":
        course = Mata_Kuliah.query.get(data["kode"])

        # check if a course exists
        if not course:
            return {"message": "Course not found"}, 404

        # override the existing data with the new ones, with current data as default values
        course.kode_mk = data.get("kode", course.kode_mk)
        course.nama_mk = data.get("nama", course.nama_mk)
        course.sks = data.get("sks", course.sks)
        db.session.commit()
        return {"message": "Course updated"}


# Mahasiswa/Students
# get all students
@app.get("/students")
def get_students():
    if login() == "mahasiswa":
        res = [
            {
                "nim": mahasiswa.nim,
                "nama": mahasiswa.nama_mhs,
                "jenis_kelamin": mahasiswa.gender_mhs,
                "nomor_telepon": mahasiswa.telp_mhs,
                "email": mahasiswa.email_mhs,
            }
            for mahasiswa in Mahasiswa.query.all()
        ]
        return jsonify(res)
    return {"message": "Unauthorized access"}, 401


# get student and delete student
@app.route("/student/<code>", methods=["GET", "DELETE"])
def get_delete_student(code):
    if login() == "mahasiswa":
        student = Mahasiswa.query.filter_by(nim=code).first()

        # check if a specific student exists
        if not student:
            return {"message": "Student not found"}, 404

        # retrieve that specific student
        if request.method == "GET":
            res = {
                "nim": student.nim,
                "nama": student.nama_mhs,
                "jenis_kelamin": student.gender_mhs,
                "nomor_telepon": student.telp_mhs,
                "email": student.email_mhs,
            }
            return jsonify(res)

        # delete that specific student
        elif request.method == "DELETE":
            db.session.delete(student)
            db.session.commit()
            return {"message": "Student deleted"}
    return {"message": "Unauthorized access"}, 401


# add student and update student
@app.route("/student", methods=["POST", "PUT"])
def add_update_student():
    if login() == "mahasiswa":
        data = request.get_json()

        # add a new student
        if request.method == "POST":
            # check if any data field is empty
            if any(
                [
                    not "nim" in data,
                    not "nama" in data,
                    not "jenis_kelamin" in data,
                    not "nomor_telepon" in data,
                    not "email" in data,
                ]
            ):
                return {"error": "Bad Request: Missing field(s)"}, 400

            # check if a student already exists
            res1 = Mahasiswa.query.filter_by(nim=data["nim"]).first()
            if res1:
                return {"error": f"Student with nim {res1.nim} already exists"}, 400

            # check unique phone number
            res2 = Mahasiswa.query.filter_by(telp_mhs=data["nomor_telepon"]).first()
            if res2:
                return {"error": f"Student with telp {res2.telp_mhs} already exists"}, 400

            # check unique email
            res3 = Mahasiswa.query.filter_by(email_mhs=data["email"]).first()
            if res3:
                return {"error": f"Student with email {res3.email_mhs} already exists"}, 400

            # check gender
            if data["jenis_kelamin"] not in ("L", "P"):
                return {"error": "Invalid gender type"}, 400

            # create a new instance of Mata Kuliah
            new_student = Mahasiswa(
                nim=data["nim"],
                nama_mhs=data["nama"],
                gender_mhs=data["jenis_kelamin"],
                telp_mhs=data["nomor_telepon"],
                email_mhs=data["email"],
            )
            db.session.add(new_student)
            db.session.commit()
            return {"message": "Student data added"}, 201

        # update an existing student
        elif request.method == "PUT":
            student = Mahasiswa.query.get(data["nim"])

            # check if a student exists
            if not student:
                return {"message": "Student data not found"}, 404

            # override the existing data with the new ones, with current data as default values
            student.nim = data.get("nim", student.nim)
            student.nama_mhs = data.get("nama", student.nama_mhs)
            student.gender_mhs = data.get("jenis_kelamin", student.gender_mhs)
            student.email_mhs = data.get("email", student.email_mhs)
            student.telp_mhs = data.get("nomor_telepon", student.telp_mhs)
            db.session.commit()
            return {"message": "Student data updated"}
    return {"message": "Unauthorized access"}, 401


# Dosen/Lecturers
# retrieve all lecturers
@app.get("/lecturers")
def get_lecturers():
    if login() == "dosen":
        res = [
            {
                "nip": dosen.nip,
                "nama": dosen.nama_dosen,
                "jenis_kelamin": dosen.gender_dosen,
                "nomor_telepon": dosen.telp_dosen,
                "email": dosen.email_dosen,
                # "list_kelas": (dosen.list_kelas)
            }
            for dosen in Dosen.query.all()
        ]
        return jsonify(res)
    return {"message": "Unauthorized access"}, 401


# Kelas/Schedules
# retrieve all available schedules
@app.get("/schedules")
def get_schedules():
    res = [
        {
            "kode_kelas": kelas.kode_kelas,
            "ruang": kelas.nama_kelas,
            "dosen": kelas.dosen.nama_dosen,
            "mata_kuliah": kelas.mata_kuliah.nama_mk,
            "hari": kelas.hari,
            "jam": kelas.jam.strftime("%H:%M:%S"),
        }
        for kelas in Kelas.query.all()
    ]
    return jsonify(res)


# create a new schedule or update an existing schedule
@app.route("/schedule", methods=["POST", "PUT"])
def create_delete_schedule():
    data = request.get_json()

    # create a new schedule
    if request.method == "POST":
        if any(
            [
                not "ruang" in data,
                not "dosen" in data,
                not "mata_kuliah" in data,
                not "hari" in data,
                not "jam" in data,
            ]
        ):
            return {"error": "Bad Request: Missing field(s)"}, 400

        # check if time and place occupied
        exist_schedule = Kelas.query.filter_by(
            hari=data["hari"], jam=data["jam"], nama_kelas=data["ruang"]
        ).first()
        if exist_schedule:
            return {"error": "Bad Request: Time and place already occupied"}, 400

        new_schedule = Kelas(
            nama_kelas=data["ruang"],
            nip=data["dosen"],
            kode_mk=data["mata_kuliah"],
            hari=data["hari"],
            jam=data["jam"],
        )
        db.session.add(new_schedule)
        db.session.commit()
        return {"message": "Schedule created"}, 201

    # update an existing schedule
    elif request.method == "PUT":
        schedule = Kelas.query.get(data["kode_kelas"])

        # check if a schedule exists
        if not schedule:
            return {"message": "Schedule not found"}, 404

        # check if time and place occupied
        exist_schedule = Kelas.query.filter_by(
            hari=data["hari"], jam=data["jam"], nama_kelas=data["ruang"]
        ).first()
        if exist_schedule:
            return {"error": "Bad Request: Time and place already occupied"}, 400

        # override the existing data with the new ones, with current data as default values
        schedule.nip = data.get("dosen", schedule.nip)
        schedule.kode_mk = data.get("mata_kuliah", schedule.kode_mk)
        schedule.hari = data.get("hari", schedule.hari)
        schedule.jam = data.get("jam", schedule.jam)
        db.session.commit()
        return {"message": "Schedule updated"}


if __name__ == "__main__":
    app.run(debug=True)
