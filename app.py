from flask import Flask, request
from flask import render_template
from flask import jsonify, make_response
import datetime
import psycopg2
import urllib.parse as urlparse
import os

url = urlparse.urlparse(os.environ['DATABASE_URL'])
dbname = url.path[1:]
user = url.username
password = url.password
host = url.hostname
port = url.port

conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
            )

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/monitoring', methods = ['GET' , 'POST'])
def datamanager():
    if request.method == 'POST' :
        data = request.get_json(force=True)
        uploadtime = data.get("uploadtime")
        user =  data.get("users")
        os = data.get('kernel')
        mem = data.get('mem free')
        swap = data.get('swap so')
        cpu = data.get('cpu sy')
        disk = data.get('hdused ')
        cur = conn.cursor()
        cur.execute("""INSERT INTO monitoring VALUES('"""+ uploadtime + """ ' , '""" + user + """ ' , '""" + os + """ ' , ' """
                     + mem + """  ' , ' """ + swap + """ ' , ' """ + cpu + """ ' , ' """ + disk + """ ')""")
        cur.execute(""" COMMIT """)

        return "1"

    cur = conn.cursor()
    cur.execute("""SELECT * FROM monitoring ORDER BY uploadtime DESC""")
    rows = cur.fetchall()
    return render_template('monitoring.html', rows = rows)

@app.route('/requests-download', methods = ['GET','POST'])
def requests_download():
    if request.method == 'POST':
        cur = conn.cursor()
        url = request.form['magnetlink']
        cur.execute(""" INSERT INTO magnetlinks (url) VALUES ('""" +  url  + """ ')""")
        cur.execute(""" COMMIT """)
        return render_template("successful.html")

    return render_template("requestDownload.html")

@app.route('/get-requests', methods = ['GET'])
def datamanagerm():
    cur = conn.cursor()
    cur.execute("""SELECT url FROM magnetlinks """)
    rows = cur.fetchall()
    urls = {}
    x = 0
    for row in rows:
        urls['url'+ str(x)] = row[0]
        x += 1

    cur.execute("""DELETE FROM magnetlinks""")
    cur.execute(""" COMMIT """)
    return jsonify(urls)

@app.route('/status', methods = ['GET', 'POST'])
def status():
    if request.method == 'POST':
        data = request.get_json(force=True)
        cur = conn.cursor()
        cur.execute("""DELETE FROM downloads""")
        cur.execute(""" COMMIT """)
        x = 0
        for dic in data:
            dic = data [x]
            name = dic.get('name')
            progress = dic.get('progress')
            ETA = dic.get('ETA')
            status = dic.get('status-1')
            speed = dic.get('speeddown')
            uploadtime = dic.get('uploadtime')
            cur.execute("""INSERT INTO downloads (name, progress, eta, status, speed, uploadtime) VALUES ('""" + name + """ ' , ' """
                        + progress + """ ' , ' """ + ETA + """ ' , ' """
                        + status + """ ' , ' """+ speed + """' , '""" + uploadtime + """ ' ) """ )
            cur.execute("""COMMIT""")

            x += 1
        return "Status upload Successful"

    cur = conn.cursor()
    cur.execute("""SELECT id, name, progress, eta, status, speed FROM downloads""")
    rows = cur.fetchall()
    cur.execute("""SELECT uploadtime FROM downloads GROUP BY uploadtime""")
    time = cur.fetchone()[0]
    return render_template('status.html', rows = rows, time = time)





if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, port = 5001)
