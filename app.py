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
    return jsonify({"result": res})


# retrieve a specific course details
@app.get("/courses/<code>")
def get_course(code):
    matkul = Mata_Kuliah.query.filter_by(kode_mk=code).first_or_404()
    res = {"kode": matkul.kode_mk, "mata_kuliah": matkul.nama_mk, "sks": matkul.sks}
    return jsonify({"result": res})


# add a new course
@app.post("/courses")
def add_course():
    kode = request.json["kode"]
    nama = request.json["nama"]
    sks = request.json["sks"]
    m = Mata_Kuliah(kode_mk=kode, nama_mk=nama, sks=sks)
    db.session.add(m)
    db.session.commit()
    return jsonify({"message": "Course added"}), 201


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
    return jsonify({"result": res})


if __name__ == "__main__":
    app.run(debug=True)
