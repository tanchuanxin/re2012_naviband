'''=================================================================================================
                                        IMPORTS AND CONFIG
================================================================================================='''
# Imports
from flask import Flask, jsonify
from flask import render_template, request, flash
from flask_mysqldb import MySQL
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from forms import RegisterForm, AppointmentForm

app = Flask(__name__)

# Database configuration
app.config['SECRET_KEY'] = 'naviband'
app.config['MYSQL_USER'] = 'x9ROzKhVaW'
app.config['MYSQL_PASSWORD'] = '9aO1rg6Nn3'
app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_DB'] = 'x9ROzKhVaW'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


'''=================================================================================================
                                            DATABASE CODE
================================================================================================='''
# database commit helper. just pass in the query like this:    '''SQL query'''


def db_helper(sql_query, values=None):
    cur = mysql.connection.cursor()
    cur.execute(sql_query, values)
    mysql.connection.commit()
    value = cur.fetchall()
    cur.close()

    return value

# To be used to reset the entire database to its default state
@app.route("/db")
def database(input=None):
    # mode selection. Available modes are drop, create, insert, reset
    if input == None:
        func = request.args['func']
    else:
        func = input

    # /db/?func=drop
    if func == "drop":
        db_helper('''DROP TABLE users, ble_data, instructions''')

    # /db/?func=create
    elif func == "create":
        db_helper('''CREATE TABLE users (nric CHAR(9) NOT NULL PRIMARY KEY, name VARCHAR(45) NOT NULL, age TINYINT NOT NULL, lastUpdated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)''')
        db_helper('''CREATE TABLE ble_data (beaconID VARCHAR(45) NOT NULL PRIMARY KEY, rssiValue INT NULL, lastUpdated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)''')
        db_helper('''CREATE TABLE instructions (queueNumber CHAR(8) NOT NULL PRIMARY KEY, vibrate TINYINT NOT NULL, ring TINYINT NOT NULL, direction VARCHAR(10) DEFAULT NULL, waitingTime INT NOT NULL, nsew VARCHAR(5) DEFAULT NULL, appointmentVenue VARCHAR(45) DEFAULT NULL, appointmentTime VARCHAR(4) DEFAULT NULL, lastUpdated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)''')

    # /db/?func=insert
    elif func == "insert":
        db_helper(
            '''INSERT IGNORE INTO users (nric, name, age) VALUES ('S1234567A', 'Tan Chuan Xin', 23)''')
        for i in range(1, 13):
            db_helper(
                '''INSERT IGNORE INTO ble_data (beaconID, rssiValue) VALUES (%s, %s)''', ("beacon"+str(i), 0))
        db_helper(
            '''INSERT IGNORE INTO instructions (queueNumber, vibrate, ring, waitingTime) VALUES (%s, %s, %s, %s)''', ("A123456F", 0, 0, 0))

    # /db/?func=reset
    elif func == "reset":
        database("drop")
        database("create")
        database("insert")

    return "Database has been " + func


'''=================================================================================================
                                        ARDUINO FUNCTIONS
================================================================================================='''
# used by arduino to send ble data to server
# /sendData?beaconID=beacon01&rssiValue=123
@app.route('/sendData', methods=['GET'])
def senddata():
    # of format: beacon01.....beacon12 etc
    beaconID = request.args['beaconID']
    rssiValue = request.args['rssiValue']   # of format: integer

    db_helper('''UPDATE ble_data SET rssiValue = %s WHERE beaconID = %s''',
              (int(rssiValue), beaconID))

    response = {
        "response": "Goodbye ESP32, from Flask. BLE data was received"
    }

    return jsonify(response)

# used by arduino to retrieve instructions from server
@app.route('/getInstructions', methods=['GET'])
def getInstructions():
    data = db_helper(
        '''SELECT * FROM instructions WHERE queueNumber = "9385"''')

    data = data[0]
    return jsonify(data)


'''=================================================================================================
                                        FRONTEND LOGIC AND VIEW
================================================================================================='''
# Home page
@app.route('/')
def home():
    return render_template('home.html')

# New polyclinic user signup
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.is_submitted():
        result = request.form
        print(result)

        db_helper('''INSERT IGNORE INTO users (nric, name, age) VALUES (%s, %s, %s)''',
                  (result['nric'], result['name'], result['age'],))

        print("nric=%s", result["nric"])
        user = db_helper(
            '''SELECT * FROM users WHERE nric=%s''', (result['nric'],))
        print(user)

        result = result.copy()
        result.poplist('register')

        return render_template('ticket.html', result=result)
    return render_template('register.html', form=form)

# Ticket for registered user
@app.route('/ticket', methods=['GET', 'POST'])
def ticket():
    return render_template('ticket.html')

# Control panel to trigger arduino
@app.route('/doctorsconsole', methods=['GET', 'POST'])
def doctorsconsole():
    form = AppointmentForm()
    if form.is_submitted():
        result = request.form
        print(result)

        db_helper('''UPDATE instructions SET appointmentVenue = %s, waitingTime = %s, appointmentTime = %s WHERE queueNumber = %s''',
                  (result['venue'], '30', result['time'], result['ticket']))

        instructions = db_helper(
            '''SELECT * FROM instructions WHERE queueNumber=%s''', (result['ticket'],))
        print(instructions)

        result = result.copy()
        result.poplist('book')

        return render_template('appointment.html', result=result)
    return render_template('doctorsconsole.html', form=form)

# Ticket for registered user
@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    return render_template('appointment.html')

# Control panel to trigger arduino
@app.route('/commands', methods=['GET', 'POST'])
def commands():
    return render_template('commands.html')


'''=================================================================================================
                                        BACKEND SERVER LOGIC
================================================================================================='''
# Setting the instruction table
@app.route('/instructions')
def instructions():
    column = request.args['column']
    value = request.args['value']

    if column == 'vibrate':
        db_helper('''UPDATE instructions SET vibrate = %s WHERE queueNumber = %s''',
                  (int(value), "A123456F"))

    if column == 'ring':
        db_helper('''UPDATE instructions SET ring = %s WHERE queueNumber = %s''',
                  (int(value), "A123456F"))

    if column == "waitingTime":
        db_helper('''UPDATE instructions SET waitingTime = %s WHERE queueNumber = %s''',
                  (int(value), "A123456F"))

    if column == 'direction':
        db_helper('''UPDATE instructions SET direction = %s WHERE queueNumber = %s''',
                  (value, "A123456F"))

    if column == "appointmentVenue":
        db_helper('''UPDATE instructions SET appointmentVenue = %s WHERE queueNumber = %s''',
                  (value, "A123456F"))

    if column == "nsew":
        db_helper('''UPDATE instructions SET nsew = %s WHERE queueNumber = %s''',
                  (value, "A123456F"))

    response = {
        "Instruction": column,
        "Value": value
    }

    return jsonify(response)


'''=================================================================================================
                                        RUN APP
================================================================================================='''
# initialize the application on localhost, based on the IPv4 address
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=443)

# if __name__ == "__main__":
#     app.run(debug=True)
