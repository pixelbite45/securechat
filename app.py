from flask import Flask, render_template, redirect, request, session, url_for, jsonify
from flask_socketio import SocketIO, emit, join_room
from flask_session import Session
from meeting_id_creation import *
from functools import wraps
from meeting_db import *
from chat_db import ChatDB






#decalre decorator for login require
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

app=Flask(__name__)
app.secret_key='hagkfgkew$#%^%$hag'




app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# and


socketio = SocketIO(app, async_mode='threading')

@socketio.on('user_unblocked')
def handle_unblock(data):
    room = data['meeting_id']
    user_id = data['user_id']
    emit('status', {'msg': f"{user_id} has been unblocked."}, room=room)

@socketio.on('join')
def handle_join(data):
    room = data['meetingId']
    username = session.get('username', 'Guest')
    
    # Check if user is blocked
    blocked_users = UserMeetingDB.get_blocked_users(room)
    if username in blocked_users:
        emit('redirect', {'url': url_for('access_denied')}, room=request.sid)
        return  # Exit without joining
    
    join_room(room)
    emit('status', {'msg': f"{username} joined the meeting."}, room=room)

@socketio.on('send_message')
def handle_message(data):
    room = data['meetingId']
    username = session.get('username', 'Guest')
    msg = data['msg']

    # Check if user is blocked
    blocked_users = UserMeetingDB.get_blocked_users(room)
    if username in blocked_users:
        # Notify the blocked user
        emit('private_message', {
            'msg': 'You are blocked and cannot send messages'
        }, room=request.sid)
        return  # Exit without processing the message

    # Save to DB
    ChatDB.save_message(room, username, msg)

    # Broadcast to room
    emit('receive_message', {'msg': f"{username}: {msg}"}, room=room)


@app.route('/')
def welcome():
    return render_template('welcome.html')


@app.route('/login_page', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if UserDB.user_exists(username):
            if password != UserDB.get_password(username):
                message = "Invalid password"
                return render_template('login_page.html', message=message)
            # Successful login
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            # Username not found, redirect to signup with message
            return redirect(url_for('signup', message="Username not found. Please sign up."))
    return render_template('login_page.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    message = None
    if request.method == 'GET':
        message = request.args.get('message')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password1']
        email=request.form['email']
        name=request.form['name']
        
        if UserDB.user_exists(username):
            message = "username already exists"
            return redirect(url_for('signup', message=message))
        else:
            UserDB.add_user(user_id=username,name=name,email=email,password=password)
            session['username'] = username
        return redirect(url_for('dashboard'))

    return render_template('signup_page.html', message=message)

    



@app.route('/dashboard')
@login_required
def dashboard():
    
    
    meetings = UserMeetingDB.get_meetings_for_user(session['username'])
    titles = [[meeting_id, MeetingDB.get_meeting_title(meeting_id)] for meeting_id in meetings]
    return render_template('dashboard.html', username=session['username'], titles=titles)






#------------------ work with multiple rooms creation --------------------#



@app.route('/meeting_create')
@login_required
def meeting_create():
    host = session['username']

    # Always create new meeting
    meetingId = meeting_id_create()
    passkey = meeting_pass_key()

    users = UserMeetingDB.get_users_for_meeting(meetingId)
    MeetingDB.add_meeting(meetingId, passkey, host=host, co_host=None)
    UserMeetingDB.add_user_to_meeting(host, meetingId, 1, 0, None, None, None)

    return redirect(url_for('meeting', meetingId=meetingId))



@app.route('/create-meeting')
def create():
    
    return render_template('create_meeting.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    session.pop('current_meeting_id', None)  # Clear cached meeting
    return redirect(url_for('login'))



@app.route('/join_meeting', methods=['GET', 'POST'])
@login_required
def join_meeting():
    sessionId=None
    if request.method == 'POST':
        username = session['username']
        sessionId = request.form['session_id']
        passkey = request.form['passkey']

        if MeetingDB.get_passkey(sessionId) == passkey:
            if session['username'] not in UserMeetingDB.get_users_for_meeting(sessionId):
                UserMeetingDB.add_user_to_meeting(username, sessionId, 1, 0, None, None, None)
                
            
            return redirect(f'/meeting/{sessionId}')
        else:
            return render_template('join_room.html', success=False, message="Invalid passkey or session ID.")
    
    # GET request: prefill the meeting ID if passed
    meeting = request.args.get('meeting')
    if meeting and MeetingDB.get_host(meeting) == session['username']:
        return redirect(f'/meeting/{meeting}')
    return render_template('join_room.html', meeting=meeting)



# ----------------------- linked with home ----------------
@app.route('/meeting/<meetingId>', methods=['POST', 'GET'])     
@login_required
def meeting(meetingId):
    logged_in_user = session.get('username')

    # Load data
    real_passkey = MeetingDB.get_passkey(meetingId)
    real_host = MeetingDB.get_host(meetingId)

    # Host can set meeting title
    if request.method == 'POST' and real_host == logged_in_user:
        new_title = request.form.get('meeting_name')
        if new_title:
            MeetingDB.update_meeting_title(meeting_id=meetingId, new_title=new_title)

    # Always fetch updated title
    meeting_name = MeetingDB.get_meeting_title(meetingId)

    # Security check
    if logged_in_user != real_host:
        user_in_meeting = logged_in_user in UserMeetingDB.get_users_for_meeting(meetingId)
        if not user_in_meeting:
            return redirect(url_for('join_meeting', message="Access Denied."))

    # Get chat history
    chat_history = ChatDB.get_messages(meetingId)

    # NEW: Fetch active and blocked users
    all_users = UserMeetingDB.get_users_for_meeting(meetingId)
    blocked_users = UserMeetingDB.get_blocked_users(meetingId)
    active_users = [user for user in all_users if user not in blocked_users]

    return render_template("meeting.html", 
                           meetingId=meetingId,
                           passkey=real_passkey,
                           host=real_host,
                           chat_history=chat_history,
                           meeting_name=meeting_name,
                           active_users=active_users,
                           blocked_users=blocked_users)








@app.route('/meeting/<meetingId>/users')
@login_required
def get_meeting_users(meetingId):
    if session['username'] not in UserMeetingDB.get_users_for_meeting(meetingId):
        return {"error": "Unauthorized"}, 403

    all_users = UserMeetingDB.get_users_for_meeting(meetingId)
    blocked_users = UserMeetingDB.get_blocked_users(meetingId)

    user_statuses = []
    for user in all_users:
        user_statuses.append({
            "username": user,
            "isBlocked": user in blocked_users
        })

    return {"users": user_statuses}




@app.route('/meeting/<meetingId>/blocked_users')
@login_required
def get_blocked_users(meetingId):
    if session['username'] not in UserMeetingDB.get_users_for_meeting(meetingId):
        return {"error": "Unauthorized"}, 403

    blocked_users = UserMeetingDB.get_blocked_users(meetingId)  # You implement this in DB
    return {"users": blocked_users}








@app.route('/update_user_status', methods=['POST'])
@login_required
def update_user_status():
    user_id = request.form.get('user_id')
    meeting_id = request.form.get('meeting_id')
    action = request.form.get('action')
    
    # Host-only restriction
    host = MeetingDB.get_host(meeting_id)
    if session['username'] != host:
        return "Unauthorized", 403

    # Determine action
    if action == "block":
        isBlocked = 1
        difi_sharekey = "blocked_key"  # Optional: Use something meaningful or null
    elif action == "unblock":
        isBlocked = 0
        difi_sharekey = None
    else:
        return "Invalid action", 400
    
    if action == "block":
        socketio.emit('user_blocked', {
            'user_id': user_id,
            'meeting_id': meeting_id
        }, room=meeting_id)
        isBlocked = 1
        difi_sharekey = "blocked_key"
    elif action == "unblock":
        socketio.emit('user_unblocked', {
            'user_id': user_id,
            'meeting_id': meeting_id
        }, room=meeting_id)
        isBlocked = 0
        difi_sharekey = None


    # Update status in DB
    UserMeetingDB.update_user_block_status(user_id=user_id, meeting_id=meeting_id, isBlocked=isBlocked, difi_sharekey=difi_sharekey)

    return redirect(request.referrer or url_for('dashboard'))



@app.route('/access_denied')
@login_required
def access_denied():
    return render_template('access_denied.html')






@app.route('/meeting/<meetingId>/check_status')
@login_required
def check_status(meetingId):
    username = session['username']
    blocked_users = UserMeetingDB.get_blocked_users(meetingId)
    
    if session['username'] not in UserMeetingDB.get_users_for_meeting(meetingId):
        session.pop('current_meeting_id', None)
        return jsonify({"error": "Unauthorized"}), 403
    
    if username in blocked_users:
        session.pop('current_meeting_id', None)  # Add this
        return jsonify({"status": "blocked"})
    return jsonify({"status": "active"})


@app.after_request
def add_header(response):
    if request.path.startswith('/meeting/'):
        response.headers['Cache-Control'] = 'no-store, max-age=0'
    return response











    

if __name__ == '__main__':
    app.run(debug=True)

