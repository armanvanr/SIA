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
        return f"<Matkul {self.nama_mk}>"


# ROUTES
# retrieve details of all courses
@app.get("/courses")
def get_courses():
    res = [
        {"kode": matkul.kode_mk, "mata_kuliah": matkul.nama_mk, "sks": matkul.sks}
        for matkul in Mata_Kuliah.query.all()
    ]
    return jsonify(res)


# retrieve a specific course details
@app.get("/course/<code>")
def get_course(code):
    course = Mata_Kuliah.query.filter_by(kode_mk=code).first()
    if not course:
        return {"message": "Course not found"}, 404
    res = {"kode": course.kode_mk, "mata_kuliah": course.nama_mk, "sks": course.sks}
    return jsonify(res)


# add a new course
@app.post("/course")
def add_course():
    data = request.get_json()
    if any([not "kode" in data, not "nama" in data, not "sks" in data]):
        return {"error": "Bad Request: Missing field(s)"}, 400

    course = Mata_Kuliah.query.filter_by(kode_mk=data["kode"]).first()
    if course:
        return {"error": "Course already exists"}, 400

    new_course = Mata_Kuliah(
        kode_mk=data["kode"], nama_mk=data["nama"], sks=data["sks"]
    )
    db.session.add(new_course)
    db.session.commit()
    return {"message": "Course added"}, 201


# update a course
@app.put("/course")
def update_course():
    data = request.get_json()
    course = Mata_Kuliah.query.get(data["kode"])
    if not course:
        return {"message": "Course not found"}, 404
    course.kode_mk = data.get("kode", course.kode_mk)
    course.nama_mk = data.get("nama", course.nama_mk)
    course.sks = data.get("sks", course.sks)
    db.session.commit()
    return {"message": "Course updated"}


# delete a course
@app.delete("/course/<code>")
def delete_course(code):
    course = Mata_Kuliah.query.filter_by(kode_mk=code).first()
    if not course:
        return {"message": "Course not found"}, 404
    db.session.delete(course)
    db.session.commit()
    return {"message": "Course deleted"}


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


if __name__ == "__main__":
    app.run(debug=True)
