from flask import Flask, render_template,request,jsonify,redirect,url_for,session
from flask_mail import Mail, Message
import sqlite3 as sql
import json
from datetime import date, time, datetime
import sqlite3 as sql
import re
import os
from datetime import date, time, datetime


app = Flask(__name__)

days =["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

def get_id():
    con = sql.connect("passport.db")
    cur = con.cursor()
    cur.execute("select seq from sqlite_sequence where name = 'passport_details'")
    users = cur.fetchall()
    print("users", users)
    for x in users:
        print("ss",x[0])
        sendid = x[0]
        print("ssend",sendid)
    id = sendid
    con.close()
    return id


def insert_passport_detail(id, name,agent_name, passport_no, email_id, visa_entry_date, visa_expiry_date):
    print("insert",id, name, agent_name, passport_no, visa_entry_date, visa_expiry_date, email_id)
    con = sql.connect("passport.db")
    cur = con.cursor()
    cur.execute("INSERT INTO passport_details (id, name, agent_name, passport_no, visa_entry_date, visa_expiry_date, email_id) VALUES (?,?,?,?,?,?,?)", (id, name, agent_name, passport_no, visa_entry_date, visa_expiry_date, email_id))
    con.commit()
    con.close()

def insert_into_stamping(id, status, today_date, today_day, today_time):
    try:
        con = sql.connect("passport.db")
        cur = con.cursor()
        cur.execute("insert into stamping_detail (id, status, IN_DATE, IN_DAY, IN_TIME) VALUES (?,?,?,?,?)", (id, status, today_date, today_day, today_time))
        con.commit()
    except sql.Error as e:
        print(e)
        return "error"
    finally:
        con.close()
    return "ok"

def insert_sales(id, T_amt, P_amt, balance):
    try:
        con = sql.connect("passport.db")
        cur = con.cursor()
        cur.execute("insert into sales_report (id, total_amt, amt_paid, balance) VALUES (?,?,?,?)", (id, T_amt, P_amt, balance))
        con.commit()
    except sql.Error as e:
        print(e)
        return "error"
    finally:
        con.close()
    return "ok"

def update_sales(id, T_amt, P_amt, balance):
    try:
        con = sql.connect("passport.db")
        cur = con.cursor()
        cur.execute("update sales_report set  total_amt=?, amt_paid=?, balance=? where id = ?", (T_amt, P_amt, balance,id))
        con.commit()
    except sql.Error as e:
        print(e)
        return "error"
    finally:
        con.close()
    return "ok"

def update_rec(id, status, today_date, today_day, today_time, T_amt, P_amt):
    try:
        con = sql.connect("passport.db")
        cur = con.cursor()
        cur.execute("update stamping_detail set status = ?,OUT_DATE = ?,OUT_DAY = ?,OUT_TIME = ? where id = ?", (status, today_date, today_day, today_time,id,))
        con.commit()
    except sql.Error as e:
        print(e)
        return "error"
    finally:
        con.close()
    return "ok"

def sales_report_data():
    try:
        con = sql.connect("passport.db")
        cur = con.cursor()
        cur.execute("select passport_details.id, IFNULL(stamping_detail.status, 0) status, passport_details.passport_no, (CASE WHEN passport_details.name IS '' then passport_details.agent_name else passport_details.name end) name, (CASE WHEN stamping_detail.status is 1 THEN 'In Stamping' when stamping_detail.status is 3 then 'Failed' when stamping_detail.status is 2 then sales_report.balance else 'Not checkin' end) balance,sales_report.total_amt from passport_details left join stamping_detail on passport_details.id = stamping_detail.id left join sales_report on passport_details.id = sales_report.id;")
        users = cur.fetchall()
        jsonarray = []
        for x in users:
            xasd =	{
                "id": x[0],
                "status": x[1],
                "passport_no": x[2],
                "name": x[3],
                "balance":x[4],
                "total_amt":x[5],
            }
            jsonarray.append(xasd)
        con.close()
        return jsonarray
    except sql.Error as e:
        print("error",e)
        return 'error'
    finally:
        con.close()

def check_amt(id):
    try:
        con = sql.connect("passport.db")
        cur = con.cursor()
        cur.execute("SELECT EXISTS(SELECT total_amt FROM sales_report WHERE id=?)", (id,))
        users = cur.fetchall()
        for x in users:
                user = x[0]
        return user
    except sql.Error as e:
        print("error", e)
        return "error"
    finally:
        con.close()


def check_status(id):
    try:
        print("id", id)
        con = sql.connect("passport.db")
        cur = con.cursor()
        cur.execute("select status from stamping_detail where id=? limit 1", (id,))
        users = cur.fetchall()
        if users == []:
            print("none")
            return "none"
        else:
            for x in users:
                user = x[0]
            print("usersss",user)
            return user
    except sql.Error as e:
        print(e)
        return 'error'
    finally:
        con.close()

def get_bill_record(tuple_result):
    try:
        con = sql.connect("passport.db")
        cur = con.cursor()
        query = "select passport_details.id, passport_details.passport_no,sales_report.total_amt, sales_report.balance, sales_report.amt_paid, stamping_detail.status, (CASE WHEN passport_details.name IS '' then passport_details.agent_name else passport_details.name end) name from passport_details left join sales_report on passport_details.id = sales_report.id left join stamping_detail on passport_details.id = stamping_detail.id where passport_details.id in {} and sales_report.amt_paid is not null".format(tuple_result).replace(',)', ')')
        # print("query00", query)
        cur.execute(query)
        # cur.execute("select passport_details.id, passport_details.passport_no, sales_report.balance, sales_report.amt_paid, stamping_detail.status, (CASE WHEN passport_details.name IS '' then passport_details.agent_name else passport_details.name end) name from passport_details left join sales_report on passport_details.id = sales_report.id left join stamping_detail on passport_details.id = stamping_detail.id where passport_details.id in (?) and sales_report.amt_paid is not null", tuple_result)
        data = cur.fetchall()
        if data == []:
            return "none"
        else:
            jsonarray = []
            for x in data:
                xasd =	{
                    "id" : x[0],
                    "passport_no" : x[1],
                    "total_amt": x[2],
                    "balance" : x[3],
                    "amt_paid" : x[4],
                    "status" : x[5],
                    "name" : x[6],
                }
                jsonarray.append(xasd)
            con.close()
            return jsonarray
    except sql.Error as e:
        print("error",e)
        return 'error'
    finally:
        con.close()

def send_mail(tuple_result):
    try:
        con = sql.connect("passport.db")
        cur = con.cursor()
        query = "select distinct passport_details.email_id from passport_details left join sales_report on passport_details.id = sales_report.id where passport_details.id in {} and sales_report.amt_paid is not null".format(tuple_result).replace(',)', ')')
        # print("query00", query)
        cur.execute(query)
        data = cur.fetchall()
        if data == []:
            return "none"
        else:
            jsonarray = []
            for x in data:
                xasd =	{
                    "email_id" : x[0],
                }
                jsonarray.append(xasd)
            con.close()
            return jsonarray
    except sql.Error as e:
        print("error",e)
        return 'error'
    finally:
        con.close()

def getdetails_db(uniqueno, passpno):
    if(passpno == ""):
        con = sql.connect("passport.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM passport_details WHERE id = ?", (uniqueno,))
        users = cur.fetchall()
        jsonarray = []
        for x in users:
            xasd =	{
                "id": x[0],
                "name": x[1],
                "agentname": x[2],
                "passport_no": x[3],
                "visa_entry_date":x[4],
                "visa_expiry_date":x[5],
                "email":x[6]
            }
            jsonarray.append(xasd)
        con.close()
        return jsonarray
    elif(uniqueno == ""):
        con = sql.connect("passport.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM passport_details WHERE passport_no LIKE ? limit 4", ('%'+passpno+'%',))
        users = cur.fetchall()
        jsonarray = []
        for x in users:
            xasd =	{
                "id": x[0],
                "name": x[1],
                "agentname": x[2],
                "passport_no": x[3],
                "visa_entry_date":x[4],
                "visa_expiry_date":x[5],
                "email":x[6]
            }
            jsonarray.append(xasd)
        con.close()
        return jsonarray
    else:
        return "Please Enter correct data"
    


@app.route('/')
def index():
   return render_template('index.html')

@app.route('/category')
def category():
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        return render_template('category.html')

@app.route('/login', methods=['POST','GET'])
def login():
    username = request.form.get("username")
    password = request.form.get("psw")
    print(username)
    print(password)
    if username == "Rikshit" and password == "ric":
        session['logged_in'] = True
        return redirect(url_for('category'))
    else:
        return "not ok"

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return render_template('index.html')

@app.route('/sendpasinfo', methods=['POST','GET'])
def sendpasinfo():
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        unique_id = request.form.get('unique_id')
        agent_name = request.form.get('agentname')
        name = request.form.get('name')
        passport_no = request.form.get('passport_no')
        email_id = request.form.get('email_id')
        visa_entry_date = request.form.get('visa_entry_date')
        visa_exit_date = request.form.get('visa_exit_date')
        print('unique_id', unique_id)
        print("jhf",visa_exit_date)
        print(agent_name + name)
        insert_passport_detail(unique_id, name, agent_name, passport_no, email_id, visa_entry_date, visa_exit_date)
        data = agent_name
        return jsonify(matchData = data)

@app.route('/filldetail', methods= ['POST','GET'])
def filldetail():
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        if request.method == 'POST':
            agentname = request.form.get("agentname")
            passno = request.form.get("passno")
            print(passno)
            m = re.match(r'^[ 0-9]+$', passno)
            print("regex",m)
            if(agentname == "" or m == None):
                error = "Enter below details correctly"
                print(error)
                enable = "true"
                return render_template('category.html', error = error, enable = enable)
            else:
                sendid = get_id()
                print("sendid", sendid)
                return render_template('filldetail.html', passno = int(passno), agentname = agentname, sendid = int(sendid))

@app.route('/individual')
def individual():
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        sendid = get_id()
        return render_template('individual.html', sendid = int(sendid))

@app.route('/view_report', methods= ['POST','GET'])
def view_report():
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        if request.method == 'POST':
            return render_template('category.html')
        else:
            return render_template('view_report.html')

@app.route('/getdetails', methods=['POST', 'GET'])
def getdetails():
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        uniqueno = request.form.get('uniqueno')
        passpno = request.form.get('passpno')
        view_detail = getdetails_db(uniqueno, passpno)
        return jsonify(matchData=view_detail)

@app.route('/send_stamp', methods=['POST','GET'])
def send_stamp():
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        id = request.form.get('id')
        today = date.today()
        today2 = today.weekday()
        today3 = datetime.now()
        today_time = today3.strftime("%X")
        today_day = days[today2]
        today_date = today.strftime('%d/%m/%Y')
        status = 1
        ret_data = insert_into_stamping(id, status, today_date, today_day, today_time)
        if(ret_data == "error"):
            print("123213",id)
            check_st = check_status(id)
            print("check",check_st)
            return jsonify(matchData="error", check_st=check_st)
        else:
            return jsonify(matchData=id)

@app.route('/rec_after_stamp', methods=['POST','GET'])
def rec_after_stamp():
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        radio = request.form.get('radio')
        T_amt = request.form.get('T_amt')
        P_amt = request.form.get('P_amt')
        balance = int(T_amt) - int(P_amt)
        if (radio == "done"):
            status = 2
        elif (radio == "fail"):
            status = 3
        id = request.form.get('rec_id')
        today = date.today()
        today2 = today.weekday()
        today3 = datetime.now()
        today_time = today3.strftime("%X")
        today_day = days[today2]
        today_date = today.strftime('%d/%m/%Y')
        update_rec(id, status, today_date, today_day, today_time, T_amt, P_amt)
        checked = check_amt(id)
        print(checked,"456")
        if(checked == 0):
            insert_sales(id, T_amt, P_amt, balance)
            return render_template('view_report.html', data = "Data inserted successfully")
        else:
            update_sales(id, T_amt, P_amt, balance) 
            return render_template('view_report.html', data = "Data updated successfully")

@app.route('/check_st_psp', methods=['POST','GET'])
def check_st_psp():
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        id = request.form.get('id')
        ck_psp = check_status(id)
        print('ck_psp', ck_psp)
        return jsonify(matchData = ck_psp)

@app.route('/sales_report_pg', methods=['POST','GET'])
def sales_report_pg():
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        sales_data = sales_report_data()
        # print("sales_data", sales_data)
        return render_template('sales_report_pg.html', sales_data = sales_data)

@app.route('/bill_report', methods=['POST','GET'])
def bill_report():
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        result = request.form.getlist('result')
        print("rssult", result)
        tuple_result = tuple(int(i) for i in result)
        bill_data = get_bill_record(tuple_result)
        mail_data = send_mail(tuple_result)
        print("mail_data", mail_data)
        return render_template('bill_page.html', bill_data=bill_data)


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(host='0.0.0.0', port=5000,debug=True)
