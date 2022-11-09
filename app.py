from flask import Flask, request, session, redirect, url_for, render_template, flash
import psycopg2
import psycopg2.extras
import re
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from psycopg2 import Error

app = Flask(__name__)
app.secret_key = 'cairocoders-ednalan'
conn = psycopg2.connect(dbname="d73n5mj84ual3h", user="rdafgphauxwref", port="5432",
password="d374484bc9439592ec0c6541dec1601478e6db4007a671b9f0ae6436d115b2a1", 
host="ec2-54-75-26-218.eu-west-1.compute.amazonaws.com")

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/result', methods=['GET', 'POST'])
def solana(conn, cursor, address):
    if 'loggedin' in session:
        url = f'https://solana-gateway.moralis.io/nft/mainnet/' + address + '/metadata'
        headers = {"accept": "application/json",
               "X-API-Key": "u8emWI08OHGRqpKRzmO3Y3gW4OhbTdOdVRuJobooGeSvYRGjep6bmjuIDVu8RqEI"}
        response = requests.get(url, headers=headers)

        cursor.execute(
          "INSERT INTO nft (address, info) values (" + "'" + address + "'" + "," + "'" + response.text + "'" + ")");
        conn.commit()

        return f''' 
                         <h2>info: {response.text} </h2>

                                        '''
    return redirect(url_for('login'))





@app.route('/', methods=['GET', 'POST'])
def home():
    if 'loggedin' in session:
        if request.method == 'POST':

            cursor = conn.cursor()
            address = request.form.get('nftaddress')

            try:
                postgreSQL_select_Query = "SELECT info FROM nft WHERE address=" + "'" + address + "'" + ";"
                cursor.execute(postgreSQL_select_Query)
                mobile_records = cursor.fetchall()

                if mobile_records == []:
                    solana(address)
                else:
                    for row in mobile_records:
                        return f''' 
                                         <h2>info: {row[0]} </h2>

                                                        '''
            except (Exception, Error) as error:
                return solana(conn, cursor, address)
            cursor.close()
            conn.close()
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        _hashed_password = generate_password_hash(password)

        cursor.execute('SELECT * FROM userdb WHERE username = %s', (username,))
        account = cursor.fetchone()
        print(account)

        if account:
            flash('This account is registered')

        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('The beginning must contain only numbers and symbols!')
        elif not username or not password:
            flash('Fill it out completely, please')
        else:
            cursor.execute("INSERT INTO userdb (username, password) VALUES (%s,%s)",
                           (username, _hashed_password))
            conn.commit()
            flash('You have successfully registered!')


    elif request.method == 'POST':
        flash('Fill it out completely, please')
    return render_template('register.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        print(password)

        cursor.execute('SELECT * FROM userdb WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            password_rs = account['password']
            print(password_rs)
            if check_password_hash(password_rs, password):
                session['loggedin'] = True
                session['username'] = account['username']
                return redirect(url_for('home'))
            else:
                flash('Username/Password is incorrect')
        else:
            flash('Username/Password is incorrect')

    return render_template('login.html')



if __name__ == '__main__':
    app.run(debug=True)
