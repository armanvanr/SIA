from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

username = os.environ["USER_NAME"]
password = os.environ["PASSWORD"]

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{username}:{password}@localhost:5432/sia"
db = SQLAlchemy(app)


class Mata_Kuliah(db.Model):
    __tablename__ = "mata_kuliah"
    kode_mk = db.Column(db.String, primary_key=True, nullable=False, unique=True)
    nama_mk = db.Column(db.String, nullable=False)
    sks = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Matkul {self.nama_mk}>"

class Mahasiswa(db.Model):
    __tablename__ = "mahasiswa"
    nim = db.Column(db.String, primary_key=True, nullable=False, unique=True)
    nama_mhs = db.Column(db.String, nullable=False)
    gender_mhs = db.Column(db.String, nullable=False)
    telp_mhs = db.Column(db.String, nullable=False, unique=True)
    email_mhs = db.Column(db.String, nullable=False, unique=True)

    def __repr__(self):
        return f"<Matkul {self.nama_mk}>"

@app.get("/courses")
def get_courses():
    res = [
        {"kode": matkul.kode_mk, "mata_kuliah": matkul.nama_mk, "sks": matkul.sks}
        for matkul in Mata_Kuliah.query.all()
    ]
    return jsonify({"result" : res})


@app.get("/courses/<kode_mk>")
def get_course(kode_mk):
    res = [
        {"kode": matkul.kode_mk, "mata_kuliah": matkul.nama_mk, "sks": matkul.sks}
        for matkul in Mata_Kuliah.query.all()
        if matkul.kode_mk == kode_mk
    ]
    return jsonify({"result" : res})

@app.get("/students")
def get_students():
    res = [
        {
            "1nim": mahasiswa.nim,
            "2nama": mahasiswa.nama_mhs,
            "3jenis_kelamin": mahasiswa.gender_mhs,
            "4nomor_telepon": mahasiswa.telp_mhs,
            "5email": mahasiswa.email_mhs
        }
        for mahasiswa in Mahasiswa.query.all()
    ]
    return jsonify({"result" : res})

if __name__ == "__main__":
    app.run(debug=True)