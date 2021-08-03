from flask import*
app=Flask(__name__)

@app.route('/')
def index():
    return "Hello"

@app.route('/index/<string:name>')
def index1(name):
    return "Your name is: %s"%name;

@app.route('/admin')
def admin():
    return 'admin here'

@app.route('/librarian')
def librarian():
    return 'librarian here'

@app.route('/student')
def student():
    return 'student here'

@app.route('/user/<name>')
def user(name):
    if name=='admin':
        return redirect(url_for('admin'))
    if name=='librarian':
        return redirect(url_for('librarian'))
    if name=='student':
        return redirect(url_for('student'))


if __name__=='__main__':
    app.run(debug=True)
    
