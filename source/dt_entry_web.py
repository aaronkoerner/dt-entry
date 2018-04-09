from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import pyodbc
import datetime

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

server = 'iv-ft-db01'
database = 'Metrics'
username = 'pyweblogger'
password = 'pyweblogger#1'
cn_str = 'DRIVER={ODBC Driver 13 for SQL Server};'
cn_str += 'SERVER='+server
cn_str += ';PORT=1443;'
cn_str += 'DATABASE='+database
cn_str += ';UID=' + username
cn_str += ';PWD='+ password
 
class ReusableForm(Form):
    id = TextField('ID:', validators=[])
    name = TextField('Name:', validators=[validators.required()])
    equip = TextField('Equip:', validators=[validators.required()])
    reason1 = TextField('Reason 1:', validators=[validators.required()])
    reason2 = TextField('Reason 2:', validators=[validators.required()])
    downtime = TextField('Downtime:', validators=[validators.required(),validators.NumberRange(min=0,max=None, message=None)])
 
@app.route("/", methods=['GET', 'POST'])
def default_entry():
    form = ReusableForm(request.form)
    values = {}
    
    id = request.args.get('id', default=-1, type=int)
    if id >= 0:
        cn = pyodbc.connect(cn_str)
        cursor = cn.cursor()
        tsql = 'SELECT top 1 id, operator, equip, reason1, reason2, downtime_minutes, timestamp from dbo.ak_DTLog where id='+id.__str__()+';'
        cursor.execute(tsql)
        result = cursor.fetchall()
        
        cursor.close()
        cn.close()
        if len(result)>0:
            values["id"] = result[0].id
            values["name"] = result[0].operator
            values["equip"] = result[0].equip
            values["reason1"] = result[0].reason1
            values["reason2"] = result[0].reason2
            values["downtime"] = result[0].downtime_minutes
    
    print form.errors
    if request.method == 'POST':
        name=request.form['name']
        equip=request.form['equip']
        reason1=request.form['reason1']
        reason2=request.form['reason2']
        downtime=request.form['downtime']
        print name, " ", equip, " ", reason1, " ", reason2, " ", downtime
 
        if form.validate():
            cn = pyodbc.connect(cn_str)
            cursor = cn.cursor()
            if id >= 0:
                tsql = 'UPDATE dbo.ak_DTLog SET operator = ?, equip = ?, reason1 = ?, reason2 = ?, downtime_minutes = ?, timestamp = ? WHERE id = ?;'
                cursor.execute(tsql,name,equip,reason1,reason2,downtime,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id)
            else:
                tsql = 'INSERT INTO dbo.ak_DTLog (operator, equip, reason1, reason2, downtime_minutes, timestamp) VALUES (?,?,?,?,?,?);'
                cursor.execute(tsql,name,equip,reason1,reason2,downtime,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            cursor.commit()
            cursor.close()
            cn.close()
            
            values["name"] = name
            values["equip"] = equip
            values["reason1"] = reason1
            values["reason2"] = reason2
            values["downtime"] = downtime
            values["id"] = -1
            # Save the comment here.
            flash('Thanks for submitting downtime, ' + name)
        else:
            flash('Error: All the form fields are required. ')
 
    return render_template('default_entry.html', form=form, result=values)


@app.route("/view", methods=['GET'])
def view():
    cn = pyodbc.connect(cn_str)
    cursor = cn.cursor()
    tsql = 'SELECT top 10 id, operator, equip, reason1, reason2, downtime_minutes, timestamp from dbo.ak_DTLog order by timestamp desc;'
    cursor.execute(tsql)
    result = cursor.fetchall()
    
    cursor.close()
    cn.close()
 
    return render_template('view.html', result=result)
    #return render_template('view.html', operator=result[0].operator, equip=result[0].equip, reason1=result[0].reason1, reason2=result[0].reason2, downtime_minutes=result[0].downtime_minutes,timestamp=result[0].timestamp)
 
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
