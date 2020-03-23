from flask import Flask, jsonify
from flask_mysqldb import MySQL

from flask import render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

from forms import RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'naviband'

app.config['MYSQL_USER'] = 'sql12329145'
app.config['MYSQL_PASSWORD'] = 'm88dXRMc7r'
app.config['MYSQL_HOST'] = 'sql12.freemysqlhosting.net'
app.config['MYSQL_DB'] = 'sql12329145'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


### To be used to reset the entire database to its default state 
@app.route("/reset")
def resetDB():
    cur = mysql.connection.cursor()
    
    cur.execute('''
        DROP TABLE users, ble_data
    ''')

    ## UNIQUE on NRIC later
    cur.execute('''
        CREATE TABLE users (nric CHAR(9) NOT NULL, name VARCHAR(45) NOT NULL, age TINYINT NOT NULL)
    ''')

    cur.execute('''
        CREATE TABLE ble_data (data TINYINT NOT NULL, datetime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)
    ''')

    cur.execute('''
        INSERT INTO users VALUES ('S1234567A', 'Tan Chuan Xin', 23)
    ''')

    cur.execute('''
        SELECT * FROM users
    ''')
    results = cur.fetchall()
    print(results)


    mysql.connection.commit()
    return "DB has been reset"



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

        cur = mysql.connection.cursor()
        cur.execute('''
            INSERT INTO users VALUES (%s, %s, %s) 
        ''', (result['nric'], result['name'], result['age'], )
        )

        cur.execute('''
            SELECT * FROM users WHERE nric=%s 
        ''', (result['nric'], )
        )
        user = cur.fetchall()
        print(user)

        mysql.connection.commit()

        result = result.copy()
        result.poplist('register')

        return render_template('ticket.html', result=result)
    return render_template('register.html', form=form)

### Arduino connected
@app.route('/getdata', methods=['GET'])
def getdata():
    response = {
        "response": "Hello ESP8266, from Flask. Here is your data",
        "data": 123
    }
    return jsonify(response)

### Arduino connected
@app.route('/senddata', methods=['GET'])
def senddata():
    data = request.args['data']

    cur = mysql.connection.cursor()
    cur.execute('''
        INSERT INTO ble_data (data) VALUES (%s) 
    ''', (int(data), )
    )
    
    mysql.connection.commit()

    response = {
        "response": "Goodbye ESP8266, from Flask. Data was received"
    }

    return jsonify(response)




### Display commands
@app.route('/commands')
def commands():
    return "Commands"

### Display map
@app.route('/map')
def map():
    return "Map"








if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=80)