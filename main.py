import mysql.connector
from flask import Flask, render_template, request, url_for, session,redirect
import random as rd
import pyqrcode
from PIL import Image
from pyzbar.pyzbar import decode
import smtplib
import config
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = ''

# db = mysql.connector.connect(host="localhost",
#                              user="root",
#                              password="",
#                              database="")

client = MongoClient(
    "")
db = client.ticketGenerator
collection1 = db['']


def sendmail(receiver, message):
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(config.EMAIL_ADDRESS, config.PASSWORD)
    server.sendmail(config.EMAIL_ADDRESS, receiver, message)
    server.quit()


@app.route('/')
def welcome():
    return render_template('index.html')


@app.route('/registrationform', methods=['GET', 'POST'])
def addparticipant():
    return render_template('addParticipant.html')


@app.route('/addparticipant', methods=['POST'])
def participantdatasubmit():
    participantDetails = request.form
    session['name'] = participantDetails['name']
    session['email'] = participantDetails['email']
    session['grade'] = participantDetails['grade']
    session['contact'] = participantDetails['contact']
    session['school'] = participantDetails['school']
    session['TFA'] = rd.randint(100000, 999999)
    subject = 'TICKET GENERATOR VERIFICATION TEST'
    msg = f"""
    Greetings,

        Test Mail
        Your verification code is {session['TFA']}

    Regards,
    Team CodeTech
    Birla Vidya Niketan
    """
    message = 'Subject: {}\n\n{}'.format(subject, msg)
    print(f"Sending verification mail to {session['name']} ")
    sendmail(participantDetails['email'], message)
    return render_template('verification.html')


@app.route('/addparticipant/confirmation', methods=['POST'])
def verifycommit():
    verifdata = request.form
    if int(session['TFA']) == int(verifdata['verification_code']):
        num = rd.randint(100000, 999999)
        qrembed = f"CODEx2021_{num}"

        code = pyqrcode.create(qrembed)
        code.png(f"QRCodes/CODEx2021_{session['name']}.png", scale=8)

        # with open(f"/Users/pancham/PycharmProjects/flasktestapp/QRCodes/CODEx2021_{session['name']}.png", 'rb') as file:
        #     binaryData = file.read()
        # cur = db.cursor()
        # cur.execute(
        #     "INSERT INTO participantData(name,email,class,contact,school,CODExID,qrcode) VALUES(%s,%s,%s,%s,"
        #     "%s,%s,%s)",
        #     (session['name'], session['email'], session['grade'], session['contact'], session['school'], qrembed,
        #      binaryData))
        # db.commit()
        # cur.close()

        collection1.insert(
            {
                '_id': qrembed,
                'name': session['name'].titlecase(),
                'email': session['email'],
                'contact': session['contact'],
                'school': session['school'].titlecase(),
            }
        )

        return 'You have successfully registered!'
    else:
        return "Invalid verification code, please register again."

@app.route('/scanparticipant', methods=['GET', 'POST'])
def scanparticipant():
    if request.method == 'POST':
        scanData = request.form
        filename = scanData['QRCODE']
        decoder = decode(Image.open(f'QRCodes/{filename}'))
        targetParticipant = decoder[0].data.decode('ascii ')
        # cur = db.cursor()
        # cur.execute('SELECT * FROM participantData WHERE CODExID like' + f"'%{targetParticipant}%';")
        # data = cur.fetchall()
        results = collection1.find({
            '_id':targetParticipant
        })
        if results:
            for result in results:
                id = result['_id']
                name = result['name']
                email = result['email']
                contact = result['contact']
                school = result['school']
            return render_template('scan-results.html', name=name, id=id, email=email, contact=contact, school=school)
    return render_template('scanParticipant.html')


@app.route('/participants')
def participants():
    # cur = db.cursor()
    # cur.execute('SELECT * FROM participantData;')
    #
    # userdetails = cur.fetchall()
    results = collection1.find()
    userdetails = []
    if results:
        for result in results:
            userdetails.append(result)

    if len(userdetails) > 0:
        return render_template('users.html', userdetails=userdetails)


@app.route('/search', methods=['GET', 'POST'])
def searchbyname():
    if request.method == 'POST':
        search = request.form
        namefilter = search['search']
        # cur = db.cursor()
        # cur.execute('SELECT * FROM participantData WHERE name like' + f"'%{namefilter}%';")
        # searchdata = cur.fetchall()

        results = collection1.find({
            'name':namefilter
        })
        if results:
            searchdata = []
            for result in results:
              searchdata.append(result)
            return render_template('search results.html', searchdata=searchdata)
    return render_template('searchbyname.html')


@app.errorhandler(404)
def error404(error):
    return "<h1>ERROR 404</h1>", 404


@app.errorhandler(500)
def error404(error):
    return "<h1>ERROR 500</h1>", 500


if __name__ == "__main__":
    app.run(debug=True)
