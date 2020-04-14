'''=================================================================================================
                                        IMPORTS AND CONFIG
================================================================================================='''
# Imports
from flask import Flask, jsonify
from flask import render_template, request, flash
from flask_mysqldb import MySQL
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from forms import RegisterForm, AppointmentForm

# import the required libraries for map:
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

# other imports
import time

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
        db_helper('''CREATE TABLE instructions (queueNumber CHAR(8) NOT NULL PRIMARY KEY, vibrate TINYINT NOT NULL, ring TINYINT NOT NULL, command INT DEFAULT 0, waitingTime INT NOT NULL, nsew VARCHAR(5) DEFAULT NULL, appointmentVenue VARCHAR(45) DEFAULT NULL, appointmentTime VARCHAR(4) DEFAULT NULL, lastUpdated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)''')

    # /db/?func=insert
    elif func == "insert":
        db_helper(
            '''INSERT IGNORE INTO users (nric, name, age) VALUES ('S1234567A', 'Tan Chuan Xin', 23)''')
        for i in range(1, 10):
            db_helper(
                '''INSERT IGNORE INTO ble_data (beaconID, rssiValue) VALUES (%s, %s)''', ("beacon"+str(i), None))
        db_helper(
            '''INSERT IGNORE INTO instructions (queueNumber, vibrate, ring, waitingTime) VALUES (%s, %s, %s, %s)''', ("9385", 0, 0, 0))

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

    navigation()

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

        if result['venue'] == 'Pharmacy':
            return render_template('appointment.html', result=result, venue='Pharmacy')
        else:
            return render_template('appointment.html', result=result, venue='Dr. So Clinic')

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
                  (int(value), "9385"))

    if column == 'ring':
        db_helper('''UPDATE instructions SET ring = %s WHERE queueNumber = %s''',
                  (int(value), "9385"))

    if column == "waitingTime":
        db_helper('''UPDATE instructions SET waitingTime = %s WHERE queueNumber = %s''',
                  (int(value), "9385"))

    if column == 'direction':
        db_helper('''UPDATE instructions SET direction = %s WHERE queueNumber = %s''',
                  (value, "9385"))

    if column == "appointmentVenue":
        db_helper('''UPDATE instructions SET appointmentVenue = %s WHERE queueNumber = %s''',
                  (value, "9385"))

    if column == "nsew":
        db_helper('''UPDATE instructions SET nsew = %s WHERE queueNumber = %s''',
                  (value, "9385"))

    response = {
        "Instruction": column,
        "Value": value
    }

    return jsonify(response)




# Finding current location based on rssi values
def currentLocationFinder():
    rssiValues = db_helper(
        '''SELECT beaconID, rssiValue FROM ble_data WHERE rssiValue IS NOT NULL ORDER BY rssiValue DESC LIMIT 2''')

    top2_beacons = [
        rssiValues[0]["beaconID"], rssiValues[1]["beaconID"]
    ]


    # sound the alarm! about to be out of bounds
    if top2_beacons[0] == "beacon1":
        db_helper(
            '''UPDATE instructions SET vibrate = 1 WHERE queueNumber = 9385''')


    if top2_beacons == ["beacon1", "beacon2"] or top2_beacons == ["beacon2", "beacon1"]:
        print("currentloc: at registration")
        currentloc_y = 18
        currentloc_x = 10
        level = 1
    elif top2_beacons == ["beacon2", "beacon3"] or top2_beacons == ["beacon3", "beacon2"] or top2_beacons == ["beacon1", "beacon3"] or top2_beacons == ["beacon3", "beacon1"]:
        currentloc_y = 41
        currentloc_x = 10
        level = 1
    elif top2_beacons == ["beacon3", "beacon4"] or top2_beacons == ["beacon3", "beacon5"]:
        print("currentloc: midpoint of staircase")
        currentloc_y = 27
        currentloc_x = 11
        level = 2
    elif top2_beacons == ["beacon4", "beacon3"] or top2_beacons == ["beacon4", "beacon5"]:
        print("currentloc: outside pharmacy")
        currentloc_y = 33
        currentloc_x = 5
        level = 2
    elif top2_beacons == ["beacon5", "beacon3"] or top2_beacons == ["beacon5", "beacon4"] or top2_beacons == ["beacon5", "beacon6"]:
        print("currentloc: top of staircase")
        currentloc_y = 27
        currentloc_x = 5
        level = 2
    elif top2_beacons == ["beacon6", "beacon7"] or top2_beacons == ["beacon6", "beacon5"] or top2_beacons == ["beacon6", "beacon8"]:
        print("currentloc: middle of top corridor")
        currentloc_y = 16
        currentloc_x = 5
        level = 2
    elif top2_beacons == ["beacon7", "beacon6"] or top2_beacons == ["beacon7", "beacon8"]:
        print("currentloc: seats at top corridor")
        currentloc_y = 7
        currentloc_x = 5
        level = 2
    elif top2_beacons == ["beacon8", "beacon7"] or top2_beacons == ["beacon8", "beacon6"] or top2_beacons == ["beacon8", "beacon9"]:
        print("currentloc: prof teo clinic")
        currentloc_y = 7
        currentloc_x = 10   
        level = 2     
    elif top2_beacons == ["beacon9", "beacon8"]:
        print("currentloc: prof so clinic")
        currentloc_y = 7
        currentloc_x = 22   
        level = 2
    else:
        currentloc_y = None
        currentloc_x = None
        level = None

    return [currentloc_y, currentloc_x, level]


# Finding destination based on appointment made
def destinationFinder():
    destination = db_helper(
        '''SELECT appointmentVenue FROM instructions WHERE queueNumber = 9385''')

    if destination[0]["appointmentVenue"] == "Prof Teo Clinic":
        # this is actually the coordinate for the couches, not the room
        destination_y = 7
        destination_x = 5
        level = 2
    elif destination[0]["appointmentVenue"] == "Prof So Clinic":
        # this is actually the coordinate for the couches, not the room
        destination_y = 7
        destination_x = 22
        level = 2
    elif destination[0]["appointmentVenue"] == "Pharmacy":
        # this is in the pharmacy 
        destination_y = 33
        destination_x = 5
        level = 2
    elif destination[0]["appointmentVenue"] == "Registration":
        # to registration door
        destination_y = 18
        destination_x = 10
        level = 1
    else:
        destination_y = None
        destination_x = None
        level = None
    
    return [destination_y, destination_x, level]


# Finding the path based on the current location and destination 
def pathfinder(start_y, start_x, start_level, end_y, end_x, end_level):
    # Create a map using a 2D-list.
    # Any value smaller or equal to 0 describes an obstacle.
    # Any number bigger than 0 describes the weight of a field that can be walked on.
    # The bigger the number the higher the cost to walk that field.
    # In this example we like the algorithm to create a path from the upper left to the bottom right.
    # To make it not to easy for the algorithm we added an obstacle in the middle, so it can not use the direct way.
    # We ignore the weight for now, all fields have the same cost of 1.
    # Feel free to create a more complex map or use some sensor data as input for it.
    # Note: you can use negative values to describe different types of obstacles.
    # It does not make a difference for the path finding algorithm but it might be useful for your later map evaluation.

    level1_matrix = [

        [0,0,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,1,1],
        [0,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,0,0,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,0,0,0,1,1],
        [0,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,0,0,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,0,0,0,1,1],
        [0,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,0,0,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,0,0,0,1,1],
        [1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,0,0,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,0,0,0,1,1],

        [1,1,1,1,1,1,   1,1,1,1,1,1,   0,0,0,0,0,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,0,0,0,1,1],
        [0,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,0,0,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,0,0,0,1,1],
        [0,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,1,   1,0,0,0,0,0,   0,0,0,0,1,1],
        [0,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,1,   1,0,0,0,0,0,   0,0,0,0,1,1],
        [0,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,0,0,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1],

        [0,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,0,0,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1],
        [0,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,0,0,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,0,0,0,0,0],
        [0,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,0,0,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   0,0,0,0,1,1],
        [0,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,0,0,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1],
        [0,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,0,0,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1],

        [0,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,0,0,1,1,1],
        [0,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,0,0,1,1,1],
        [0,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,0,0,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,0,0,1,1,1],
        [0,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,0,0,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,0,0,1,1,1],
        [0,0,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,0,   1,1,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,0],

    ]

    level2_matrix = [
        
        [1,1,1,1,1,0,   0,0,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,0],
        [1,1,1,1,1,0,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,0,0,0,   1,1,1,1,1,0,   0,1,1,1,1,1,   1,1,1,0,1,1,   1,1,0,1,1,1,   1,1,1,1,1,0],
        [1,1,1,1,0,0,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,0,0,0,   1,1,1,1,1,0,   0,1,1,1,1,1,   1,0,0,0,0,1,   0,0,0,1,1,1,   1,1,1,1,1,0], 
        [1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,0,0,0,   1,1,1,1,1,0,   0,1,1,1,1,1,   1,1,1,0,1,1,   1,1,0,1,1,1,   1,1,1,1,1,0], 
        [1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,0,0,0,   0,1,1,0,0,0,   0,0,0,1,1,0,   0,0,0,0,1,1,   1,1,0,1,1,1,   1,1,1,1,1,0],

        [1,1,1,1,0,0,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,0],
        [0,0,0,0,0,0,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,0],
        [0,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,0,0,0,   0,0,1,1,0,0,   0,0,1,1,0,0,   0,0,1,1,0,0,   0,0,0,0,0,0,   1,0,0,0,1,1,   1,1,0,1,1,1,   1,1,1,1,1,0],
        [0,1,1,1,1,1,   1,1,0,0,0,0,   0,0,0,0,0,0,   1,1,1,1,1,1,   1,0,1,1,0,1,   1,1,1,1,1,1,   1,1,1,0,0,0,   1,1,1,0,1,1,   1,1,0,1,1,1,   1,1,1,1,1,0],
        [0,0,0,0,0,0,   1,1,0,0,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,0,1,1,0,1,   1,1,1,1,1,1,   1,1,1,0,1,1,   1,1,1,0,1,1,   1,1,0,1,1,1,   1,1,1,1,1,0],

        [0,0,0,0,0,0,   1,1,0,0,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,0,1,1,0,1,   1,1,1,1,1,1,   1,1,1,0,1,1,   1,1,1,0,1,1,   1,1,0,1,1,1,   1,1,1,1,1,0],
        [0,1,1,1,1,1,   1,1,0,0,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,0,1,1,0,1,   1,1,1,1,1,1,   1,1,1,0,1,1,   1,1,1,0,1,1,   1,1,0,1,1,1,   1,1,1,1,1,0],
        [0,1,1,1,1,1,   1,1,0,0,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,0,1,1,0,1,   1,1,1,1,1,1,   1,1,1,0,0,0,   0,0,0,0,1,1,   1,1,0,1,1,1,   1,1,1,1,1,0],
        [0,0,0,0,0,0,   1,1,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,1,   1,1,1,1,1,1,   1,1,1,0,0,0,   0,0,0,0,1,1,   1,1,0,1,1,1,   1,1,1,1,1,0],
        [0,0,0,0,0,0,   1,1,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,1,   1,1,1,1,1,1,   1,1,1,0,1,1,   1,1,1,0,1,1,   1,1,0,1,1,1,   1,1,1,1,1,0],

        [0,1,1,1,1,0,   1,1,0,0,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,0,0,1,   1,1,1,1,1,1,   1,1,1,0,1,1,   1,1,1,0,1,1,   1,1,0,1,1,1,   1,1,1,1,1,0],
        [0,1,1,1,1,1,   1,1,0,0,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,0,0,1,   1,1,1,1,1,1,   1,1,1,0,1,1,   1,1,1,0,1,1,   1,1,0,1,1,1,   1,1,1,1,1,0],
        [0,1,1,1,1,0,   1,1,0,0,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,0,0,1,   1,1,1,1,1,1,   1,1,1,0,1,1,   1,1,1,0,1,1,   1,1,0,1,1,1,   1,1,1,1,1,0],
        [0,0,0,0,0,0,   1,1,0,0,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,0,0,1,   1,1,1,1,1,1,   1,1,1,0,1,1,   1,1,1,0,1,1,   1,1,0,1,1,1,   1,1,1,1,1,0],
        [0,1,1,1,1,0,   1,1,0,0,0,0,   0,0,0,0,0,1,   1,0,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,0,   1,1,0,0,1,1,   1,1,0,1,1,1,   1,1,1,1,1,0],

        [0,1,1,1,1,1,   1,1,0,0,0,0,   0,0,0,0,0,1,   1,0,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,0,   1,1,0,0,1,1,   1,1,0,1,1,1,   1,1,1,1,1,0],
        [0,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   0,1,1,1,1,1,   1,1,1,1,0,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,0],
        [0,1,1,1,1,0,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,0],
        [0,1,1,1,1,0,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   0,1,1,1,1,1,   1,1,1,1,1,1,   1,1,1,1,1,1,   1,1,0,1,1,1,   1,1,1,1,1,0],
        [0,0,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,0,   0,0,0,0,0,0],
    ]

    # we create a new grid from this map representation. This will create Node instances for every element of our map.
    # It will also set the size of the map. We assume that your map is a square, so the size height is defined by the
    # length of the outer list and the width by the length of the first list inside it.
    if start_level == 1:
        grid = Grid(matrix=level1_matrix)
    elif start_level == 2:
        grid = Grid(matrix=level2_matrix)


    # modify the endpoints if it is on another level, to be the intermediate staircase based on the correct level 
    # this ensures we can find a path
    if start_level == 1 and end_level == 2:
        end_y = 41
        end_x = 10
        end_level = 1
    elif start_level == 2 and end_level == 1:
        end_y = 27
        end_x = 11
        end_level = 2



    # we get the start (top-left) and endpoint (bottom-right) from the map:
    # IMPORTANT: THE GRID COORDINATES ARE GIVEN AS COLUMN, ROW

    start = grid.node(start_y, start_x)     # start = grid.node(27, 11)
    end = grid.node(end_y, end_x)           # end = grid.node(3, 7)



    # create a new instance of our finder and let it do its work.
    # The find_path function does not only return you the path from the start to the end point
    # it also returns the number of times the algorithm needed to be called until a way was found.
    finder = AStarFinder()
    path, runs = finder.find_path(start, end, grid)


    # thats it. We found a way. Now we can print the result (or do something else with it).
    # Note that the start and end points are part of the path.

    # You can ignore the +, - and | characters, they just show the border around your map
    # The blank space is a free field, 's' marks the start, 'e' the end and '#' our obstacle in the middle.
    # You see the path from start to end marked by 'x' characters. We allow horizontal movement, so it is not using the upper-right corner. Y
    # ou can access print(path) to get the specific list of coordinates.
    print('operations:', runs, 'path length:', len(path))
    print(grid.grid_str(path=path, start=start, end=end))
    print("\nThe actual path coordinates: ", path)

    return [grid.grid_str(path=path, start=start, end=end),path]


# Give the direction of the next step to take
def nextStepDirectionFinder(current_location, destination):
    if current_location == [18,10,1] and destination == [7,5,2]:
        # going prof teo clinic. go to stairs by walking straight (out of registration can see stairs)
        db_helper(
            '''UPDATE instructions SET command = 12''')

    elif current_location == [41,10,1] and destination == [7,5,2]:
        # going prof teo clinic. climb up stairs
        db_helper(
            '''UPDATE instructions SET command = 16''')            

    elif current_location == [27,11,2] and destination == [7,5,2]:
        # going prof teo clinic. climb up the stairs
        db_helper(
            '''UPDATE instructions SET command = 16''')

    elif current_location == [27,5,2] and destination == [7,5,2]:
        # going prof teo clinic. turn left. go straight
        db_helper(
            '''UPDATE instructions SET command = 11''') 
        
        time.sleep(3)

        db_helper(
            '''UPDATE instructions SET command = 12''') 

    elif current_location == [16,5,2] and destination == [7,5,2]:
        # going prof teo clinic. go straight
        db_helper(
            '''UPDATE instructions SET command = 12''') 
        
    elif current_location == [7,5,2] and destination == [7,5,2]:
        # going prof teo clinic. reached. set wait time
        db_helper(
            '''UPDATE instructions SET command = 19''') 

        time.sleep(10)
        db_helper(
            '''UPDATE instructions SET command = 22''')             
        time.sleep(5)
        db_helper(
            '''UPDATE instructions SET command = 23''')                
        time.sleep(5)
        db_helper(
            '''UPDATE instructions SET command = 25''')          
        time.sleep(5)
        db_helper(
            '''UPDATE instructions SET command = 24''')                      

    elif current_location == [7,5,2] and destination == [7,22,2]:
        # going prof so clinic. turn right. go straight
        db_helper(
            '''UPDATE instructions SET command = 13''') 

        time.sleep(3)

        db_helper(
            '''UPDATE instructions SET command = 12''')      

    elif current_location == [7,10,2] and destination == [7,22,2]:
        # going prof so clinic. go straight
        db_helper(
            '''UPDATE instructions SET command = 12''')                 

    elif current_location == [7,22,2] and destination == [7,22,2]:
        # going prof so clinic. reached. Set wait time
        db_helper(
            '''UPDATE instructions SET command = 20''') 

        time.sleep(10)
        db_helper(
            '''UPDATE instructions SET command = 22''')             
        time.sleep(5)
        db_helper(
            '''UPDATE instructions SET command = 23''')                
        time.sleep(5)
        db_helper(
            '''UPDATE instructions SET command = 25''')          
        time.sleep(5)
        db_helper(
            '''UPDATE instructions SET command = 24''')  

    elif current_location == [7,22,2] and destination == [33,5,2]:
        # going pharmacy. turn left. go straight
        db_helper(
            '''UPDATE instructions SET command = 11''') 

        time.sleep(3)

        db_helper(
            '''UPDATE instructions SET command = 12''')      

    elif current_location == [7,10,2] and destination == [33,5,2]:
        # going pharmacy. go straight
        db_helper(
            '''UPDATE instructions SET command = 12''')        

    elif current_location == [7,5,2] and destination == [33,5,2]:
        # going pharmacy. turn right. go straight
        db_helper(
            '''UPDATE instructions SET command = 13''') 

        time.sleep(3)

        db_helper(
            '''UPDATE instructions SET command = 12''')           

    elif current_location == [16,5,2] and destination == [33,5,2]:
        # going pharmacy. go straight
        db_helper(
            '''UPDATE instructions SET command = 12''')                    

    elif current_location == [27,5,2] and destination == [33,5,2]:
        # going pharmacy. go straight
        db_helper(
            '''UPDATE instructions SET command = 12''')              

    elif current_location == [33,5,2] and destination == [33,5,2]:
        # going pharmacy. reached. set 5 minute wait time
        db_helper(
            '''UPDATE instructions SET command = 21''')    

        time.sleep(10)
        db_helper(
            '''UPDATE instructions SET command = 22''')             
        time.sleep(5)
        db_helper(
            '''UPDATE instructions SET command = 23''')                
        time.sleep(5)
        db_helper(
            '''UPDATE instructions SET command = 25''')          
        time.sleep(5)
        db_helper(
            '''UPDATE instructions SET command = 24''')                             
    
    elif current_location == [33,5,2] and destination == [18,10,1]:
        # going registration. turn left. go straight
        db_helper(
            '''UPDATE instructions SET command = 11''')    

        time.sleep(3)

        db_helper(
            '''UPDATE instructions SET command = 12''')             

    elif current_location == [27,5,2] and destination == [18,10,1]:
        # going registration. turn left. go down
        db_helper(
            '''UPDATE instructions SET command = 11''')    

        time.sleep(3)

        db_helper(
            '''UPDATE instructions SET command = 15''')     

    elif current_location == [27,11,2] and destination == [18,10,1]:
        # going registration. climb down. go straight
        db_helper(
            '''UPDATE instructions SET command = 15''')    

        time.sleep(3)

        db_helper(
            '''UPDATE instructions SET command = 12''')         

    elif current_location == [41,10,1] and destination == [18,10,1]:
        # going registration. go straight
        db_helper(
            '''UPDATE instructions SET command = 12''')        

    elif current_location == [18,10,1] and destination == [18,10,1]:
        # going registration. reached
        db_helper(
            '''UPDATE instructions SET command = 18''')                               

@app.route('/navigation')
def navigation(): 
    current_location = currentLocationFinder()      
    print("current location: ", current_location)
    destination = destinationFinder()
    print("destination: ", destination)
    [grid,path] = pathfinder(current_location[0], current_location[1], current_location[2], destination[0], destination[1], destination[2])
    nextStepDirectionFinder(current_location, destination)

    # need three more characters than the number of rows for delimiters and newline character 
    if current_location[2] == 1:
        no_column = 45  
    elif current_location[2] == 2:
        no_column = 63


    grid = [grid[i:i+no_column] for i in range(0, len(grid), no_column)]


    return render_template("navigation.html", data=grid[1:-1])







'''=================================================================================================
                                        RUN APP
================================================================================================='''
# initialize the application on localhost, based on the IPv4 address
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

# if __name__ == "__main__":
#     app.run(debug=True)
