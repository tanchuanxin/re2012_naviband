'''=================================================================================================
                                        IMPORTS AND CONFIG
================================================================================================='''
### Imports
from flask import Flask, jsonify
from flask import render_template, request
from flask_mysqldb import MySQL
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from forms import RegisterForm

app = Flask(__name__)

### Database configuration
app.config['SECRET_KEY'] = 'naviband'
app.config['MYSQL_USER'] = 'sql12329145'
app.config['MYSQL_PASSWORD'] = 'm88dXRMc7r'
app.config['MYSQL_HOST'] = 'sql12.freemysqlhosting.net'
app.config['MYSQL_DB'] = 'sql12329145'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)







'''=================================================================================================
                                            DATABASE CODE
================================================================================================='''
### database commit helper. just pass in the query like this:    '''SQL query'''
def db_helper(sql_query, values=None):
    cur = mysql.connection.cursor()
    cur.execute(sql_query, values)
    mysql.connection.commit()
    return cur.fetchall()

### To be used to reset the entire database to its default state 
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
        db_helper('''CREATE TABLE instructions (queueNumber CHAR(8) NOT NULL PRIMARY KEY, vibrate TINYINT NOT NULL, direction VARCHAR(10) DEFAULT NULL, appointmentTime DATETIME DEFAULT NULL, appointmentVenue VARCHAR(45) DEFAULT NULL, lastUpdated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)''')

    # /db/?func=insert
    elif func == "insert":
        db_helper('''INSERT IGNORE INTO users (nric, name, age) VALUES ('S1234567A', 'Tan Chuan Xin', 23)''')
        for i in range(1, 13):
            db_helper('''INSERT IGNORE INTO ble_data (beaconID, rssiValue) VALUES (%s, %s)''', ("beacon"+str(i), 0) )
        db_helper('''INSERT IGNORE INTO instructions (queueNumber, vibrate) VALUES (%s, %s)''', ("A123456F", 0))

    # /db/?func=reset
    elif func == "reset": 
        database("drop")
        database("create")
        database("insert")

    return ("Database has been " + func)






'''=================================================================================================
                                        ARDUINO FUNCTIONS
================================================================================================='''
# used by arduino to send ble data to server
# /sendData?beaconID=beacon01&rssiValue=123
@app.route('/sendData', methods=['GET'])
def senddata():
    beaconID = request.args['beaconID']     # of format: beacon01.....beacon12 etc
    rssiValue = request.args['rssiValue']   # of format: integer

    db_helper('''UPDATE ble_data SET rssiValue = %s WHERE beaconID = %s''', (int(rssiValue), beaconID) )

    response = {
        "response": "Goodbye ESP8266, from Flask. Data was received"
    }

    return jsonify(response)

### used by arduino to retrieve instructions from server
@app.route('/getInstructions', methods=['GET'])
def getdata():
    data = db_helper('''SELECT * FROM instructions WHERE queueNumber = "A123456F"''')

    return jsonify(data)







'''=================================================================================================
                                        FRONTEND LOGIC AND VIEW
================================================================================================='''
### Index page
@app.route("/")
def index():
    naviband_users = [{'name': 'ChuanXin', 'comment': 'Awesome'}, {'name': 'AikHui', 'comment': 'Really Awesome'}]
    return render_template('naviband.html', author="Chuan Xin", goodday=True, naviband_users=naviband_users)

### New polyclinic user signup
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.is_submitted():
        result = request.form
        print(result)

        db_helper('''INSERT IGNORE INTO users (nric, name, age) VALUES (%s, %s, %s)''', (result['nric'], result['name'], result['age']))

        user = db_helper('''SELECT * FROM users WHERE nric=%s''', (result['nric']))
        print(user)


        result = result.copy()
        result.poplist('register')

        return render_template('ticket.html', result=result)
    return render_template('register.html', form=form)



'''=================================================================================================
                                        BACKEND SERVER LOGIC 
================================================================================================='''













'''=================================================================================================
                                        RUN APP
================================================================================================='''
# initialize the application on localhost, based on the IPv4 address
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)



