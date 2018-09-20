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
from flask import make_response
import os.path
import StringIO
import csv

DATABASE = '/site/mantener/db/mantener'

app = Flask(__name__,template_folder='/site/mantener/html/')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "/site/mantener/db/mantener")

sampleCSV = [
[1, "PIZA3LH", "Durvesh Bhole", "S2", "09/02/2018", "Weekend", "RT123454", "Weekend", "Primary"],
[2, "PIZA3LK", "Prashant Keshvani", "S2", "09/04/2018", "Weekday", "RT12344,RT23232", "Weekend", "Primary"],
[3, "PIZA3LK", "Durvesh Bhole", "S2", "09/06/2018", "Weekend", "RT123454", "Weekend", "Secondary"],
[4, "PIZA3LJ", "Sushrut Pajai", "S1", "09/02/2018", "Weekday", "RT123454", "Weekend", "Primary"],
[5, "PIZA3LK", "Prashant Keshvani", "S1", "09/04/2018", "Weekend", "RT12344,RT23232", "Weekend", "Primary"],
[6, "PIZA3LJ", "Sushrut Pajai", "S1", "09/14/2018", "Weekday", "RT123454", "Weekday", "Secondary"],
[7, "PIZA3LK", "Prashant Keshvani", "S1", "09/06/2018", "Weekend", "RT12344,RT23232", "Weekend", "Primary"],
[8, "PIZA3LJ", "Sushrut Pajai", "S1", "09/03/2018", "Weekday", "RT123454", "Weekday", "Secondary"],
[9, "PIZA3LH", "Durvesh Bhole", "S2", "09/03/2018", "Weekend", "RT123454", "Weekend", "Primary"],
[10, "PIZA3LJ", "Sushrut Pajai", "S2", "09/03/2018", "Weekend", "RT12344,RT23232", "Weekend", "Primary"],
[11, "PIZA3LH", "Durvesh Bhole", "S1", "09/04/2018", "Weekend", "RT123454", "Weekend", "Primary"],
[12, "PIZA3LJ", "Sushrut Pajai", "S2", "09/05/2018", "Weekday", "RT12344,RT23232", "Weekend", "Primary"],
[13, "PIZA3LJ", "Sushrut Pajai", "S1", "09/05/2018", "Weekday", "RT123454", "Weekend", "Primary"],
[14, "PIZA3LK", "Prashant Keshvani", "S2", "09/05/2018", "Weekday", "RT12344,RT23232", "Weekend", "Secondary"],
[15, "PIZA3LK", "Prashant Keshvani", "S1", "09/05/2018", "Weekend", "RT12344,RT23232", 10, "Primary"]
]

def is_json(request):
    if not request.json:
        print 'Not a JSON'
        abort(400)
        return False
    return True

#DB Connection
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


#Data handling API's
@app.route("/api/v1/getData")
def getData():
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
            level = dataDict['level']
            cursor = g.db.execute("insert into work_log (user_id,name,shift,date,day,tickets,timespent,level) values(?,?,?,?,?,?,?,?)",(uid,nm,shift,date,day,tickets,timespent,level))
            g.db.commit()
        except ValueError, e:
    	    print 'Failed Pushing Data to Database'
            return False

    return {'status':'1'}


@app.route('/api/v1/onCall',methods = ['GET'])
def onCall():
    try:
        level = request.args.get('level')
    except Error as e:
        print "No parameter supplied",e

    cursor = g.db.execute('select u.user_id, u.full_name, u.email, u.contact, o.level, o.team from users u join on_call_now o using(user_id) where level = ?',(level,))
    items = []
    headers = ['user_id','full_name','email','contact','level','team']
    onCall = cursor.fetchall()
    for row in onCall:
        items.append({'user_id':row[0],'full_name':row[1],'email':row[2],'contact':row[3],'level':row[4],'team':row[5]})

    return json.dumps(items)

#file download
@app.route('/download')
def post():
    try:
        queryParameter = request.args.get('date')
    except Error as e:
        print "No Parameter supplied",e

    daterange = queryParameter.split(' - ', 1)
    print daterange
    cursor = g.db.execute('SELECT * FROM work_log where date > ? and date < ?', (daterange[0],daterange[1],))
    dbResult = cursor.fetchall()
    print dbResult
    csv_headers = ["Id", "uid","Name","Shift","Date","Day","RT","ts","level"]
    dbResult.insert(0,csv_headers)
    si = StringIO.StringIO()
    cw = csv.writer(si)
    cw.writerows(dbResult)
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output

#Sample API
@app.route('/foo', methods=['POST']) 
def foo():
    if not request.json:
        abort(400)
    print request.json
    return json.dumps(request.json)

#views routes
@app.route('/update')
def index():
    return render_template('store_data.html') 

@app.route('/home')
def view():
    return render_template('index.html')

@app.route('/generate_reports')
def generateReports():
    return render_template('reports.html')

if __name__ == '__main__':
   print "Opened database successfully";
   app.run(
       host="0.0.0.0",
       port=int("3000")
   )
