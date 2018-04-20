from flask import Flask
from flaskext.mysql import MySQL

app = Flask(__name__)
mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'culturp7'
app.config['MYSQL_DATABASE_PASSWORD'] = 'IanTheMan2017!'
app.config['MYSQL_DATABASE_DB'] = 'culturp7_rehearsal'
app.config['MYSQL_DATABASE_HOST'] = '50.116.65.175'
mysql.init_app(app)

@app.route('/')
def hello_world():
    cursor = mysql.get_db().cursor()
    cursor.execute("SELECT * FROM networks WHERE id=251")
    data = cursor.fetchone()
    print(data)
    return "Success!!"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
