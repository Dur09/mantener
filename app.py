############# Author #################
# A Python-Flask based web app to log
# pager-duty shifts for MCA team
# version: 0.1 Beta
######################################

import sqlite3
from sqlite3 import Error
import json
from flask import Flask, abort,request
from flask import render_template
from flask import g
import os.path

DATABASE = '/site/mantener/db/mantener'

app = Flask(__name__,template_folder='/site/mantener/html/')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "/site/mantener/db/mantener")

def is_json(request):
    if not request.json:
        print 'Not a JSON'
        abort(400)
        return False
    return True

def connect_db():
    return sqlite3.connect(DATABASE)

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    print "Tearing Down"
    if hasattr(g, 'db'):
        g.db.close()

@app.route("/getData")
def geData():
    cursor = g.db.execute("SELECT * FROM work_log")
    empData = cursor.fetchall()
    output = json.dumps(empData)
    print output
    return output

@app.route("/api/v1/getUsers",methods = ['GET'])
def getUsers():
    if request.method == 'GET':
        try:
            print "Fetching users from db"
            cursor = g.db.execute('select * from users')
            users = cursor.fetchall()
            convert_json = {x[0]:x[1] for x in users}
            users_list = json.dumps(convert_json)
            return users_list
        except Error as e:
            print "Failed to fetch user list from table"
            print(e)
        return None
    else:
        return False

@app.route('/api/v1/storeData',methods = ['POST'])
def storeData():
    if request.method == 'POST':
        print request
        is_json(request)
        incomingData = request.data
        print incomingData
        dataDict = json.loads(incomingData)
        print dataDict
        try:
            uid = dataDict['user_id']
            nm = dataDict['name']
            shift = dataDict['shift']
            date = dataDict['date']
            day = dataDict['day']
            tickets = dataDict['tickets']
            timespent = dataDict['timespent']
            cursor = g.db.execute("insert into work_log (user_id,name,shift,date,day,tickets,timespent) values(?,?,?,?,?,?,?)",(uid,nm,shift,date,day,tickets,timespent))
            g.db.commit()
        except ValueError, e:
    	    print 'Failed Pushing Data to Database'
            return False

    return json.dumps("Data Pushed Successfully.")

@app.route('/foo', methods=['POST']) 
def foo():
    if not request.json:
        abort(400)
    print request.json
    return json.dumps(request.json)

@app.route('/')
def index():
    return render_template('store_data.html') 

# Coming Soon...
@app.route('/view')
def view():
    return render_template('viewLog.html')

if __name__ == '__main__':
   print "Opened database successfully";
   app.run(
       host="0.0.0.0",
       port=int("3000")
   )
