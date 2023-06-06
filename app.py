from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

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
db = SQLAlchemy(app)


# SCHEMAS
# create table Mata_Kuliah
class Mata_Kuliah(db.Model):
    __tablename__ = "mata_kuliah"
    kode_mk = db.Column(db.String, primary_key=True, nullable=False, unique=True)
    nama_mk = db.Column(db.String, nullable=False)
    sks = db.Column(db.Integer, nullable=False)
    # list_kelas = db.relationship("kelas")

    def __repr__(self):
        return f"Matkul <{self.nama_mk}>"


# create table Mahasiswa
class Mahasiswa(db.Model):
    __tablename__ = "mahasiswa"
    nim = db.Column(db.String, primary_key=True, nullable=False, unique=True)
    nama_mhs = db.Column(db.String, nullable=False)
    gender_mhs = db.Column(db.String, nullable=False)
    telp_mhs = db.Column(db.String, nullable=False, unique=True)
    email_mhs = db.Column(db.String, nullable=False, unique=True)

    def __repr__(self):
        return f"<Matkul {self.nama_mhs}>"


# create table Dosen
class Dosen(db.Model):
    __tablename__ = "dosen"
    nip = db.Column(db.String, primary_key=True, nullable=False, unique=True)
    nama_dosen = db.Column(db.String, nullable=False)
    gender_dosen = db.Column(db.String, nullable=False)
    telp_dosen = db.Column(db.String, nullable=False, unique=True)
    email_dosen = db.Column(db.String, nullable=False, unique=True)
    # list_kelas = db.relationship("kelas")

    def __repr__(self):
        return f"<Matkul {self.nama_dosen}>"


# create table Kelas
class Kelas(db.Model):
    __tablename__ = "kelas"
    kode_kelas = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    nama_kelas = db.Column(db.String, nullable=False)
    nip = db.Column(db.String, db.ForeignKey("dosen.nip"), nullable=False)
    kode_mk = db.Column(db.String, db.ForeignKey("mata_kuliah.kode_mk"), nullable=False)
    hari = db.Column(db.String, nullable=False)
    jam = db.Column(db.Time, nullable=False)

    def __repr__(self):
        return f"<Kelas {self.kode_kelas}>"

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

# retrieve a specific course details or delete a course
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

# add a new course or delete an existing course
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
# retrieve details of all students
@app.get("/students")
def get_students():
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

# Dosen/Lecturers
# retrieve all lecturers
@app.get("/lecturers")
def get_lecturers():
    res = [
        {
            "nip": dosen.nip,
            "nama": dosen.nama_dosen,
            "jenis_kelamin": dosen.gender_dosen,
            "nomor_telepon": dosen.telp_dosen,
            "email": dosen.email_dosen,
        }
        for dosen in Dosen.query.all()
    ]
    return jsonify(res)

# Kelas/Schedules
# retrieve all available schedules
@app.get("/schedules")
def get_schedules():
    res = [
        {
            "kode_kelas": kelas.kode_kelas,
            "ruang": kelas.nama_kelas,
            "dosen": kelas.nip,
            "mata_kuliah": kelas.kode_mk,
            "hari": kelas.hari,
            "waktu": kelas.jam.strftime('%H:%M:%S')
        }
        for kelas in Kelas.query.all()
    ]
    return jsonify(res)

if __name__ == "__main__":
    app.run(debug=True)
