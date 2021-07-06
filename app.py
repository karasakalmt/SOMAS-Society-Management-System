from werkzeug.utils import redirect, secure_filename
from forms import *
from flask import Flask, request, render_template, session, url_for, abort
from dboperate import db_cursor, getSocAdmAdv, isExistsComposite, isExistsDB, parseEvents, societyAuth, somasdb, passwordCheck, getSocietyInfo, getEvents, getImage, attendeeParse
from authorizations import accessLevel
from datetime import timedelta
from helper import *
from slugify import slugify
import os
import fnmatch

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(days=5)
app.config['SECRET_KEY'] = "Sup3rS3cre7c5rF7ok3N"
app.config['EVENT_POSTER_DEST'] = 'static/posters'
app.config['IMAGES_DEST'] = 'static/images'


allLevels = ["ADMIN", "ADVISOR", "USER", "SOC"]

@app.route("/")
def home():
    if not 'auth' in session:
        return redirect(url_for('login',next=request.url))
    event_list = getEvents(session["user"], 2, app.root_path)
    return render_template("events.html", events=event_list)

@app.route("/register", methods=['GET', 'POST'])
def register():
    register_form = UserRegisterForm()
    if register_form.is_submitted():
        name = register_form.name.data
        email = register_form.email.data
        password = str(register_form.password.data)
        department = register_form.department.data
        year = register_form.year.data
        stuID = register_form.stuID.data
        if(isExistsDB(email, 'email', 'User') or isExistsDB(email, 'email', 'Advisor') or isExistsDB(email, 'email', 'Administrator')):
            return render_template("register.html", register_form = register_form,error=1)
        else:

            db_cursor.execute(f'''INSERT INTO User VALUES("{email}","{name}",md5("{password}"),{department});''')
            if(year and stuID):
                db_cursor.execute(f'''INSERT INTO Student VALUES("{email}", '{year}', {stuID})''')
            somasdb.commit()
            session["user"] = email
            session["auth"] = "USER"
        register_form.email.data=None
        
        if request.method == 'POST':
            return redirect(url_for('home', next=request.url), code=302)
    
    return render_template("register.html",register_form = register_form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    login_form = UserLoginForm()
    if login_form.is_submitted():
        email = login_form.email.data
        password = login_form.password.data
        user = isExistsDB(email, 'email', 'User')
        adv = isExistsDB(email, 'email', 'Advisor')
        soc = isExistsDB(email, 'email', 'Society')
        adm = isExistsDB(email, 'email', 'Administrator')
        if not (user or adv or adm or soc):
            return render_template("login.html",login_form = login_form,error=1)
        else:
            session["user"] = email
            if(user and passwordCheck(email, 'User', password)):
                session["auth"] = "USER"
            elif(adv and passwordCheck(email, 'Advisor', password)):
                session["auth"] = "ADVISOR"
            elif(soc and passwordCheck(email,'Society', password)):
                session["auth"] = "SOC"
                db_cursor.execute(f'''SELECT slug FROM Society where email="{email}";''')
                info = db_cursor.fetchall()[0]
                session["slug"] = info
            elif(adm and passwordCheck(email,'Administrator', password)):
                session["auth"] = "ADMIN"
            else:
                session.pop('user', None)
                session.pop('auth', None)
                return render_template("login.html",login_form = login_form,error=1)

            return redirect(url_for('home', next=request.url))

    return render_template("login.html",login_form = login_form)

@app.route('/logout')
@accessLevel(allLevels)
def logout():
    session.pop('user', None)
    session.pop('auth', None)
    return redirect(url_for('login', next=request.url), code=302)

@app.route('/change-password', methods=['GET', 'POST'])
@accessLevel(allLevels)
def change_pw():
    form = ChangePassword()
    if form.is_submitted():
        password = form.password.data
        table = authToTable(session)
        db_cursor.execute(f'''UPDATE {table} SET password = md5('{password}') WHERE email = '{session["user"]}';''')
        somasdb.commit()
    return render_template("pass_change.html", form=form)

@app.route('/create-society-acc', methods=['GET', 'POST'])
@accessLevel(["ADMIN"])
def create_soc():
    form = CreateSocietyForm()
    if form.is_submitted():
        email = form.email.data
        name = form.name.data
        logo = form.logo.data
        slug = slugify(name)
        password = form.password.data
        budget = form.budget.data
        description = form.description.data
        advisor = form.advisor_email.data
        db_cursor.execute(f'''INSERT INTO Society VALUES("{email}","{name}","{slug}",md5("{password}"),{budget},"{description}", "{session["user"]}", "{advisor}");''')
        db_cursor.execute(f'''INSERT INTO Advised VALUES("{advisor}", "{email}");''')
        somasdb.commit()
        if logo:
            extension = logo.filename.split(".")
            filename = secure_filename(slug+'.'+extension[1])
            logo.save(os.path.join(
                app.root_path, 'static', 'logos', filename
            ))
    return render_template("create_society.html", form=form)

@app.route('/create-advisor-acc', methods=['GET', 'POST'])
@accessLevel(["ADMIN"])
def create_adv():
    form = CreateAdvisor()
    if form.is_submitted():
        email = form.email.data
        name = form.name.data
        password = form.password.data
        department = form.department.data
        if(isExistsDB(email, 'email', 'Advisor')):
            return render_template("create_advisor.html", form=form,error=1)

        else:
            db_cursor.execute(f'''INSERT INTO Advisor VALUES("{email}","{name}",md5("{password}"),"{department}");''')

        somasdb.commit()
    return render_template("create_advisor.html", form=form)

@app.route("/societies")
@accessLevel(allLevels)
def list_societies():
    if not 'auth' in session:
        return redirect(url_for('login',next=request.url))
    db_cursor.execute(f'''SELECT slug FROM Society;''')
    slugs = db_cursor.fetchall()
    soc_list =[]
    for slug in slugs:
        soc_list.append(getSocietyInfo(app.root_path , slug[0]))
    return render_template('societies.html', societies = soc_list)

@app.route('/<society>', methods=['GET','POST'])
@accessLevel(allLevels)
def show_society_details(society):
    if(isExistsDB(society,'slug','Society')):
        userFlag=0 # if 1 user not member if 2 user member if 0 not user 
        authFlag=False
        socFlag=False
        payments=[]
        total_attendance =[]
        member_list=[]
        society_info = getSocietyInfo(app.root_path, society)

        if request.method == 'POST' and society_info["email"] == session["user"]:
            photo=request.files["photo"]
            count = 0
            while 1:
                if getImage(app.root_path, f"{society}-{count}", 'gallery') == "":
                    break
                count+=1
            ext = photo.filename.split('.')[1]
            fileName = secure_filename(f"{society}-{count}.{ext}")
            photo.save(os.path.join(app.root_path, 'static', 'gallery', fileName))

        if session["auth"] == "USER":
            userFlag = 1
            db_cursor.execute(f'''SELECT user_email FROM SocietyMembers WHERE user_email='{session["user"]}' AND soc_email = '{society_info["email"]}';''')
            user = db_cursor.fetchall()
            if user != []:
                userFlag = 2
                
        if request.method == 'POST' and session["auth"] == "USER":
            req = request.form["choise"]
            if userFlag == 1 and req=="member":
                db_cursor.execute(f'''INSERT INTO SocietyMembers VALUES('{session["user"]}', '{society_info["email"]}')''')
                userFlag = 2
            elif userFlag == 2 and req=="end":
                db_cursor.execute(f'''DELETE FROM SocietyMembers WHERE user_email = '{session["user"]}' AND soc_email='{society_info["email"]}';''')
                userFlag = 1
            somasdb.commit()

        
        gallery = []
        count = 0
        image = ""
        while 1:
            image = litowin(getImage(app.root_path, f"{society}-{count}", 'gallery'))
            if image == "":
                break
            gallery.append(image)
            count+=1
        db_cursor.execute(f'''SELECT event_name, e_date, name, e.description, e.slug, soc_email, s.slug FROM Event e LEFT JOIN Society s on s.email=e.soc_email WHERE e.status=2 AND s.slug = '{society}' ORDER BY e_date DESC;''')
        upcoming_events = db_cursor.fetchall()
        upcoming_events = parseEvents(upcoming_events, app.root_path)

        if session["user"] == society_info["email"]:
            socFlag=True

        if session["user"] == society_info["email"] or session["auth"] == "ADMIN" or session["user"] == society_info["admin-mail"]:
            authFlag = True
            db_cursor.execute(f'''SELECT u.name, u.student_id, u.email, a.e_name 
                                        FROM (SELECT u.name, u.email, s.student_id FROM User u LEFT JOIN Student s USING(email)) u
                                        RIGHT JOIN Attendee a ON u.email=a.user_email
                                        WHERE a.soc_email='{society_info["email"]}'
                                        ORDER BY a.e_name;''')
            total_attendance = db_cursor.fetchall()
            total_attendance = attendeeParse(total_attendance)
            db_cursor.execute(f'''SELECT e_name, bill_detail, cost FROM Payment WHERE soc_email ='{society_info["email"]}';''')
            total_cost = db_cursor.fetchall()
            if total_cost!=[]:
                for cost in total_cost:
                    payments.append({
                            'event': cost[0],
                            'bill_detail': cost[1],
                            'cost': cost[2]
                        })
            db_cursor.execute(f'''SELECT user_email FROM SocietyMembers WHERE soc_email='{society_info["email"]}';''')
            getmembers = db_cursor.fetchall()
            for member in getmembers:
                member_list.append(member[0])
        return render_template("society.html", society_info=society_info, upcomings=upcoming_events, socFlag=socFlag, gallery=gallery, userFlag=userFlag, authFlag=authFlag, attendance=total_attendance, costs=payments, members=member_list)
    return abort(404)

@app.route('/<society>/create-event', methods=['GET', 'POST'])
@accessLevel(["SOC"])
def create_event(society):
    if(isExistsDB(society,'slug', 'Society')):
        if(societyAuth(session["user"], society)):
            form = EventCreationForm()
            if form.is_submitted():
                name = form.event_name.data
                date = form.event_date.data
                description = form.description.data
                poster = form.poster.data
                guest = form.guest_name.data
                slug = slugify(name)
                info = getSocAdmAdv(society)

                if not isExistsComposite(name, session["user"], "event_name", "soc_email", "Event"):
                    db_cursor.execute(f'''INSERT INTO Event VALUES("{name}", STR_TO_DATE('{date}', '%Y-%m-%d %h:%i:%s') ,"{slug}",0,"{description}", "{session["user"]}","{info["advisor-mail"]}", "{info["admin-mail"]}");''')
                    somasdb.commit()
                    if poster:
                        extension = poster.filename.split(".")
                        filename = secure_filename(society+'-'+slug+'.'+extension[1])
                        poster.save(os.path.join(
                            app.root_path, 'static', 'posters', filename
                        ))
                    if guest:
                        guest = guest.split(',')
                        for g in guest:
                            db_cursor.execute(f'''INSERT INTO Event_Guest VALUES("{session["user"]}","{name}","{g.strip()}");''')
                        somasdb.commit()
                else:
                    return render_template("create_event.html", form = form,error=1)


            return render_template("create_event.html", form = form)
        return abort(403)
    return abort(404)

@app.route('/events-apply', methods=['GET', 'POST'])
@accessLevel(["ADVISOR", "ADMIN"])
def society_acceptence_activities():
    if request.method == "POST":
        req = request.form
        req = req["status"].split(' ')
        status = 0
        if req[2] == 'Accept':
            if(session["auth"]=="ADMIN"):
                status = 2
            if(session["auth"]=="ADVISOR"):
                status = 1
            db_cursor.execute(f'''UPDATE Event SET status={status} WHERE slug='{req[1]}' AND soc_email='{req[0]}';''')
            somasdb.commit()
        else:
            e_name = req[1].replace('-', ' ')
            db_cursor.execute(f'''SELECT guest FROM Event_Guest WHERE soc_email='{req[0]}' AND e_name='{e_name}';''')
            guests = db_cursor.fetchall()
            if guests != []:
                guests_delete = "("
                for guest in guests:
                    guests_delete += "'"+guest[0]+"',"
                guests_delete = guests_delete[:-1]+')'
                db_cursor.execute(f'''DELETE FROM Event_Guest WHERE soc_email='{req[0]}' AND e_name='{e_name}' AND guest IN {guests_delete};''')
                somasdb.commit()
            db_cursor.execute(f'''SELECT s.slug FROM Society s RIGHT JOIN Event e ON s.email='{req[0]}'  WHERE e.slug='{req[1]}';''')
            soc_slug=db_cursor.fetchall()
            soc_slug = soc_slug[0][0]
            poster = getImage(app.root_path,f"{soc_slug}-{req[1]}",'posters')
            if poster != "":
                os.remove(poster)
            db_cursor.execute(f'''DELETE FROM Event WHERE soc_email='{req[0]}' AND event_name='{e_name}';''')
            somasdb.commit()
    if(session["auth"]=="ADVISOR"):
        event_list = getEvents(session["user"],0,app.root_path)
        return render_template("advisor_adm_accept.html", events = event_list)
    elif(session["auth"]=="ADMIN"):
        event_list = getEvents(session["user"],1,app.root_path)
        return render_template("advisor_adm_accept.html", events=event_list)
    return abort(403)

@app.route('/<society>/<event>', methods=['GET', 'POST'])
@accessLevel(allLevels)
def show_event(society, event): #if admin or related advisor show attendance and budget add edit for society
    db_cursor.execute(f'''SELECT e.status, event_name, soc_email FROM Event e LEFT JOIN Society s on s.email=e.soc_email WHERE e.slug='{event}' AND s.slug='{society}';''')
    eventFetched = db_cursor.fetchall()
    eventFetched = eventFetched[0]
    userFlag = 0 # if 1 not attendee and user else if 2 attendee and user
    attendance =[]
    if session["auth"] == "USER":
        userFlag = 1
        db_cursor.execute(f'''SELECT user_email FROM Attendee WHERE user_email='{session["user"]}' AND soc_email = '{eventFetched[2]}' AND e_name='{eventFetched[1]}';''')
        user = db_cursor.fetchall()
        if user != []:
            userFlag = 2

    if request.method == "POST" and session["user"] == eventFetched[2]:
        req = request.form
        db_cursor.execute(f'''SELECT budget FROM Society WHERE email='{eventFetched[2]}';''')
        budget = db_cursor.fetchall()[0][0]
        if 'paid' in req:
            if req['paid'] != '' and req['cost'] != '' and int(req['cost'])>0:
                budget -= int(req['cost'])
                if budget > 0:
                    db_cursor.execute(f'''INSERT INTO Payment VALUES('{eventFetched[1]}', '{eventFetched[2]}', '{req['paid']}', {req['cost']});''')
                    db_cursor.execute(f'''UPDATE Society SET budget = {budget} WHERE email='{eventFetched[2]}';''')
                    somasdb.commit()
            else:
                pass #give error
        elif 'delete' in req:
            db_cursor.execute(f'''SELECT cost FROM Payment WHERE bill_detail ='{req["delete"]}' AND e_name = '{eventFetched[1]}' AND soc_email = '{eventFetched[2]}';''')
            cost = db_cursor.fetchall()[0][0]
            budget += cost
            db_cursor.execute(f'''DELETE FROM Payment WHERE soc_email = '{eventFetched[2]}' AND e_name='{eventFetched[1]}';''')
            db_cursor.execute(f'''UPDATE Society SET budget = {budget} WHERE email='{eventFetched[2]}';''')
            somasdb.commit()

    if request.method == "POST" and session["auth"] == "USER":
        if userFlag == 1:
            db_cursor.execute(f'''INSERT INTO Attendee VALUES('{eventFetched[2]}','{eventFetched[1]}','{session["user"]}');''')
            userFlag = 2
            pass
        elif userFlag == 2:
            db_cursor.execute(f'''DELETE FROM Attendee WHERE user_email='{session["user"]}' AND soc_email = '{eventFetched[2]}' AND e_name='{eventFetched[1]}';''')
            userFlag = 1
            pass
        somasdb.commit()
    socFlag = False
    details = []
    if eventFetched != []:
        if(eventFetched[0]<2 and session["auth"] not in ["ADMIN", "ADVISOR"]):
            return abort(403)
        else: # can be optimized
            db_cursor.execute(f'''SELECT event_name, e_date, name, e.description, e.slug, soc_email, s.slug FROM Event e LEFT JOIN Society s on s.email=e.soc_email WHERE e.slug = '{event}' AND s.slug = '{society}' ORDER BY e_date DESC;''')
            event_info = db_cursor.fetchall()
            event_info = parseEvents(event_info, app.root_path)[0]
            if session["auth"] == "ADVISOR" or session["auth"] == "ADMIN" or (session["auth"] == "SOC" and session["user"] == event_info["soc_email"]):
                adv_auth = getSocAdmAdv(society)
                if adv_auth["advisor-mail"] == session["user"] or session["auth"] == "ADMIN" or (session["auth"] == "SOC" and session["user"] == event_info["soc_email"]):
                    db_cursor.execute(f'''SELECT bill_detail, cost FROM Payment WHERE e_name = '{event_info["event_name"]}' AND soc_email = '{event_info["soc_email"]}';''')
                    bills = db_cursor.fetchall()
                    for bill in bills:
                        details.append({'bill_detail':bill[0], 'cost': bill[1]})
                    db_cursor.execute(f'''SELECT u.name, u.student_id, u.email 
                                        FROM (SELECT u.name, u.email, s.student_id FROM User u LEFT JOIN Student s USING(email)) u
                                        RIGHT JOIN Attendee a ON u.email=a.user_email
                                        WHERE a.soc_email='{event_info["soc_email"]}' AND a.e_name = '{event_info["event_name"]}';''')
                    attendance = db_cursor.fetchall()
                    attendance = attendeeParse(attendance)

            if session["auth"] == "SOC" and session["user"] == event_info["soc_email"]:
                socFlag = True
            
            if eventFetched[0]==3:
                socFlag = False
                userFlag = 3 #not able to attend
            
        return render_template("event.html", event=event_info, details=details, socFlag=socFlag, userFlag=userFlag, attendees = attendance)
    else:
        return abort(404)


if __name__ == "__main__":
    app.run(debug=True, port=5001)