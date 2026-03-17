from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, emit
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dein_geheimes_passwort'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///einkaufsliste.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
socketio = SocketIO(app)  # Initialisierung von Flask-SocketIO

# Datenbankmodelle
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_authorized = db.Column(db.Boolean, default=False)

class Einkauf(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rollenüberprüfung-Dekorator
def role_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authorized:
            abort(403)  # Zugriff verweigern mit Fehler 403
        return func(*args, **kwargs)
    return decorated_function

# Routen
@app.route('/')
@login_required
@role_required  # Nur autorisierte Benutzer können diese Route aufrufen
def home():
    einkaufsliste = Einkauf.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', einkaufsliste=einkaufsliste)

@app.route('/add', methods=['POST'])
@login_required
def add_item():
    item = request.form.get('item')
    new_item = Einkauf(item=item, user_id=current_user.id)
    db.session.add(new_item)
    db.session.commit()
    
    # Diese Zeile sollte entfernt werden
    # socketio.emit('item_added', {'item': item, 'user': current_user.username})
    
    return redirect(url_for('home'))

@app.route('/delete/<int:item_id>')
@login_required
def delete_item(item_id):
    item = Einkauf.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    
    # Nachricht an alle verbundenen Clients senden
    socketio.emit('item_deleted', {'item_id': item_id})
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('home'))
        flash('Fehler beim Login. Bitte überprüfe deine Anmeldedaten.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Benutzername ist bereits vergeben.')
            return redirect(url_for('register'))

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Erfolgreich registriert! Du kannst dich jetzt einloggen.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/authorize/<int:user_id>', methods=['GET'])
@login_required
def authorize_user(user_id):
    if current_user.is_authorized:  # Überprüfen, ob der aktuelle Benutzer autorisiert ist
        user = User.query.get(user_id)
        if user:
            user.is_authorized = True
            db.session.commit()
            flash(f'User {user.username} ist jetzt autorisiert.')
    return redirect(url_for('home'))  # Oder wo immer du umleiten möchtest

@socketio.on('add_item')
@login_required
def handle_add_item(data):
    item = data['item']
    new_item = Einkauf(item=item, user_id=current_user.id)
    db.session.add(new_item)
    db.session.commit()

    # Senden Sie die neuen Elemente an alle verbundenen Clients
    socketio.emit('item_added', {'item': item, 'user': current_user.username, 'id': new_item.id})

@app.route('/user_management', methods=['GET'])
@login_required
def user_management():
    if not current_user.is_admin:  # Überprüfen, ob der aktuelle Benutzer ein Admin ist
        abort(403)
        
    users = User.query.all()
    return render_template('user_management.html', users=users)

@app.route('/authorize_user/<int:user_id>')
@login_required
def authorize_user(user_id):
    if not current_user.is_admin:
        abort(403)

    user = User.query.get_or_404(user_id)
    user.is_authorized = True
    db.session.commit()
    flash(f'Benutzer {user.username} wurde autorisiert.')
    return redirect(url_for('user_management'))

# WebSocket-Events
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Erstellt die Datenbank und Tabellen
    socketio.run(app, debug=True)  # Starte die Anwendung mit SocketIO
