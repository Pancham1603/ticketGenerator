import mysql.connector
from flask import Flask, render_template, request
import random as rd
import pyqrcode
from PIL import Image
from pyzbar.pyzbar import decode

app = Flask(__name__)

db = mysql.connector.connect(host="localhost",
                             user="root",
                             password="***REMOVED***",
                             database="***REMOVED***")

@app.route('/')
def welcome():
    return render_template('index.html')

@app.route('/addparticipant', methods=['GET', 'POST'])
def addparticipant():
    if request.method == 'POST':
        participantDetails = request.form
        name = participantDetails['name']
        email = participantDetails['email']
        grade = participantDetails['grade']
        contact = participantDetails['contact']
        school = participantDetails['school']

        num = rd.randint(100000, 999999)
        qrembed = f"CODEx2021_{num}"

        code = pyqrcode.create(qrembed)
        code.png(f"/Users/pancham/PycharmProjects/flasktestapp/QRCodes/CODEx2021_{name}.png", scale=8)

        with open(f"/Users/pancham/PycharmProjects/flasktestapp/QRCodes/CODEx2021_{name}.png", 'rb') as file:
            binaryData = file.read()

        cur = db.cursor()
        cur.execute("INSERT INTO participantData(name,email,class,contact,school,CODExID,qrcode) VALUES(%s,%s,%s,%s,"
                    "%s,%s,%s)",
                    (name, email, grade, contact, school, qrembed, binaryData))
        db.commit()
        cur.close()
        return 'success'
    return render_template('addParticipant.html')


@app.route('/scanparticipant', methods=['GET', 'POST'])
def scanparticipant():
    if request.method == 'POST':
        scanData = request.form
        filename = scanData['QRCODE']
        decoder = decode(Image.open(f'/Users/pancham/PycharmProjects/flasktestapp/QRCodes/{filename}'))
        targetParticipant = decoder[0].data.decode('ascii ')
        cur = db.cursor()
        cur.execute('SELECT * FROM participantData WHERE CODExID like' + f"'%{targetParticipant}%';")
        data = cur.fetchall()
        for row in data:
            participantName = row[0]
            participantEmail = row[1]
            participantClass = row[2]
            participantContact = row[3]
            participantSchool = row[4]

        return f"Name: {participantName}   |   Email: {participantEmail}   |   Class: {participantClass}   |   Contact: {participantContact}   |   School: {participantSchool} "
    return render_template('scanParticipant.html')


@app.route('/participants')
def participants():
    cur = db.cursor()
    cur.execute('SELECT * FROM participantData;')

    userdetails = cur.fetchall()
    return render_template('users.html', userdetails=userdetails)


@app.route('/search', methods=['GET', 'POST'])
def searchbyname():
    if request.method == 'POST':
        search = request.form
        namefilter = search['search']
        cur = db.cursor()
        cur.execute('SELECT * FROM participantData WHERE name like' + f"'%{namefilter}%';")
        searchdata = cur.fetchall()
        return render_template('search results.html', searchdata=searchdata)
    return render_template('searchbyname.html')

@app.errorhandler(404)
def error404(error):
    return "<h1>ERROR 404</h1>",404

@app.errorhandler(500)
def error404(error):
    return "<h1>ERROR 500</h1>",500


if __name__ == "__main__":
    app.run(debug=True)