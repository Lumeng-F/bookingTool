import pytz
from flask import redirect, render_template, request, url_for, abort, flash
from flask_login import login_user, current_user, logout_user, login_required
from pbook import app, db, bcrypt
from pbook.models import Customers, Stores, Setting
from pbook.scripts.cus import *
from pbook.scripts.sche import *
from pbook.scripts.other import *
from pbook.scripts.forms import *


# Global variables and func to init default settings
defGList = ['G1', 'G2', 'G3', 'G4']
defDList = ['D1', 'D2', 'D3', 'D4']
colCount = len(defGList)
defTOne = {'30': [200, 120, 100], '60': [300, 180, 120], '70': [
    400, 220, 180], '90': [500, 300, 200], '120': [800, 500, 300]}
defTTwo = {'30': [300, 180, 120], '60': [500, 300, 120], '70': [
    600, 400, 200], '90': [800, 500, 300], '120': [1000, 500, 500]}


@app.route("/")
def homepage():
    return redirect(url_for('schedulepage'))


@app.route("/register", methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('schedulepage'))
    form = RegisterForm()
    if form.validate_on_submit():
        hashedPswd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Stores(storeName=form.storeName.data, password=hashedPswd)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('schedulepage'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Stores.query.filter_by(storeName=form.storeName.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('schedulepage'))

    return render_template('login.html', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

# The main page of the application
@app.route("/schedule", methods=['POST', 'GET'])
@login_required
def schedulepage():
    global allAppInfo
    storeAppInfo = [appinfo for appinfo in allAppInfo if appinfo[9] == current_user.id]
    phoneList = []
    currTime = datetime.now(pytz.timezone('US/Eastern')).strftime("%Y-%m-%d %H:%M")
    # I don't know WTF I'm doing, but seems like I need to query everytime I do this
    results = db.engine.execute('SELECT * FROM setting WHERE storeID = %s', current_user.id).fetchone()

    if results is not None:
        # Variables for displays, apparently I cannot set this to a global variable
        girlList = setGD(results)[0]
        deviceList = setGD(results)[1]
        colCount = colClassName(len(girlList))
        phoneResult = db.engine.execute('SELECT phone FROM customers WHERE storeID = %s', current_user.id).fetchall()
        phoneList = [int(phone[0]) for phone in phoneResult]
    else:
        girlList = defGList
        deviceList = defDList
        colCount = colClassName(4)

    if request.method == "POST":
        sTime = request.form.get("sTime")
        gName = request.form.get("gName")
        dura = request.form.get("dura")
        cName = request.form.get("cName")
        cNum = request.form.get("cNum")
        device = request.form.get("device")
        tier = request.form.get("tier")

        # Since I built other func around the old approach, the new formatted list will have to be what it is now
        # Take 10 params for display/sorting/calculate pays/customer info
        sTime = datetime.strptime(sTime, '%Y-%m-%dT%H:%M')
        eTime = sTime + timedelta(minutes=int(dura))
        newAppoint = [gName, sTime, eTime, "apbtn default", cName, cNum, device, dura, tier, current_user.id]

        # Check if the new appointment is overlapping with current ones
        tempAppInfo = [appInfo for appInfo in storeAppInfo if appInfo[0] == newAppoint[0]]
        tempAppInfo = [appInfo for appInfo in tempAppInfo if appInfo[3] == 'apbtn default']
        if len(tempAppInfo) == 0:
            # The solution seems less optimal, but need to add this to add the 1st appointment of the day
            allAppInfo.append(newAppoint)
        else:
            for appoints in tempAppInfo:
                errorMsg = checkOverlapping([appoints[1], appoints[2]], [newAppoint[1], newAppoint[2]])
                if errorMsg is None:
                    allAppInfo.append(newAppoint)
                    break
                else:
                    flash(errorMsg)
                    break

        allAppInfo = sortAppointInfo(allAppInfo)
        # Map girlList to an empty Dict to display which appointment is which girl
        for (key, girl) in zip(girlListDic.keys(), girlList):
            storeAppInfo = [appinfo for appinfo in allAppInfo if appinfo[9] == current_user.id]
            girlListDic[key] = getLists(storeAppInfo, girl)

    for (key, girl) in zip(girlListDic.keys(), girlList):
        storeAppInfo = [appinfo for appinfo in allAppInfo if appinfo[9] == current_user.id]
        girlListDic[key] = getLists(storeAppInfo, girl)
    return render_template('schedule.html', colCount=colCount,
                           currTime=currTime, girlList=girlList, deviceList=deviceList,
                           girlListDic=girlListDic, allAppInfo=allAppInfo, phoneList=phoneList)

# Show the pay and work for each one
@app.route("/dayend", methods=['POST', 'GET'])
def dayendpage():
    global girlPayDic
    global currTier

    # I don't know WTF I'm doing, but seems like I need to query everytime I do this
    results = db.engine.execute('SELECT * FROM setting WHERE storeID = %s', current_user.id).fetchone()
    if results is not None:
        girlList = [results[1], results[2], results[3], results[4]]
        t1Price = setPTier(results)[0]
        t2Price = setPTier(results)[1]
        girlPayDic = {girl: {} for girl in girlList}
    else:
        girlList = defGList
        t1Price = defTOne
        t2Price = defTTwo

    storeAppInfo = [appinfo for appinfo in allAppInfo if appinfo[9] == current_user.id]
    for (key, girl) in zip(girlPayDic.keys(), girlList):
        girlPayDic[key] = getGirlPay(storeAppInfo, girl, t1Price)

    # func to change price tier
    if request.method == "POST":
        if currTier == 1:
            for (key, girl) in zip(girlPayDic.keys(), girlList):
                girlPayDic[key] = getGirlPay(storeAppInfo, girl, t1Price)
            currTier = 2
            # IDK why I decided to add this
            dayCharged = dayEndPay(girlPayDic)[0]
            dayEarned = dayEndPay(girlPayDic)[1]

            return render_template('dayend.html', girlList=girlList, girlPayDic=girlPayDic,
                                   dayCharged=dayCharged, dayEarned=dayEarned)
        if currTier == 2:
            for (key, girl) in zip(girlPayDic.keys(), girlList):
                girlPayDic[key] = getGirlPay(storeAppInfo, girl, t2Price)
            currTier = 1
            # IDK why I decided to add this
            dayCharged = sum(
                [girlPayDic[key]['Comp Total'] + girlPayDic[key]['Girl Total'] for key in girlPayDic.keys()])
            dayEarned = sum([girlPayDic[key]['Comp Total'] for key in girlPayDic.keys()])
            return render_template('dayend.html', girlList=girlList, girlPayDic=girlPayDic,
                                   dayCharged=dayCharged, dayEarned=dayEarned)

    # IDK why I decided to add this
    dayCharged = dayEndPay(girlPayDic)[0]
    dayEarned = dayEndPay(girlPayDic)[1]
    return render_template('dayend.html', girlList=girlList, girlPayDic=girlPayDic,
                           dayCharged=dayCharged, dayEarned=dayEarned)


@app.route("/customer")
def customerpage():
    return render_template('customer.html')


# The whole setting thing will be better if it's implemented like the customer page,
# But the customer sorting/editing is copied, so I don't know how implement here.
@app.route("/setting", methods=['POST', 'GET'])
@login_required
def setting():
    results = db.engine.execute('SELECT * FROM setting WHERE storeID = %s', current_user.id).fetchone()
    if results is not None:
        # Variables for displays, apparently I cannot set this to a global variable
        girlList = setGD(results)[0]
        deviceList = setGD(results)[1]
        t1Price = setPTier(results)[0]
        t2Price = setPTier(results)[1]
    else:
        girlList = defGList
        deviceList = defDList
        t1Price = defTOne
        t2Price = defTTwo
    form = SettingForm()
    # Fetch user info and save to db
    if request.method == "POST":
        newSetting = Setting(g1=form.g1.data, g2=form.g2.data,
                             g3=form.g3.data, g4=form.g4.data,
                             d1=form.d1.data, d2=form.d2.data,
                             d3=form.d3.data, d4=form.d4.data,

                             t130=form.t130.data, t130Comp=form.t130Comp.data,
                             t160=form.t160.data, t160Comp=form.t160Comp.data,
                             t170=form.t170.data, t170Comp=form.t170Comp.data,
                             t190=form.t190.data, t190Comp=form.t190Comp.data,
                             t1120=form.t1120.data, t1120Comp=form.t1120Comp.data,

                             t230=form.t230.data, t230Comp=form.t230Comp.data,
                             t260=form.t260.data, t260Comp=form.t260Comp.data,
                             t270=form.t270.data, t270Comp=form.t270Comp.data,
                             t290=form.t290.data, t290Comp=form.t290Comp.data,
                             t2120=form.t1120.data, t2120Comp=form.t2120Comp.data,
                             storeID=current_user.id
                             )
        Setting.query.filter_by(storeID=current_user.id).delete()
        db.session.add(newSetting)
        db.session.commit()

        return render_template('setting.html', form=form, girlList=girlList, deviceList=deviceList,
                               t1Price=t1Price, t2Price=t2Price)
    return render_template('setting.html', form=form, girlList=girlList, deviceList=deviceList,
                           t1Price=t1Price, t2Price=t2Price)


""" Backend stuff"""

# Change appointment status on click
@app.route("/backend", methods=['POST', 'GET'])
def statuschange():
    global allAppInfo
    if request.method == "POST":
        appToCheck = request.form.get("appToCheck")
        for appoints in allAppInfo:
            if appToCheck == str(appoints):
                onStatusChange(appoints)
                return redirect(url_for('schedulepage'))

    return redirect(url_for('schedulepage'))

# Update customer info after day end
@app.route("/backend2", methods=['POST', 'GET'])
def saveCusInfo():
    global allAppInfo
    currTime = datetime.now()

    results = db.engine.execute('SELECT * FROM setting WHERE storeID = %s', current_user.id).fetchone()
    if results is not None:
        t1Price = setPTier(results)[0]
        t2Price = setPTier(results)[1]
    else:
        t1Price = defTOne
        t2Price = defTTwo
    paidDf = paidCus(allAppInfo, t1Price, t2Price)
    canedDf = cancelledCus(allAppInfo)
    updateDb(paidDf, canedDf, current_user.id)

    # Save appointments that have not been cancelled and not yet happened, clear else.
    allAppInfo = [appInfo for appInfo in allAppInfo if appInfo[3] == 'apbtn default' and appInfo[1] > currTime]
    for key in girlListDic:
        girlListDic[key].clear()
    return redirect(url_for('dayendpage'))

# This and 'update' are copied, used to show customer info in the customer page
@app.route('/api/data')
def data():
    # query = Customers.query # Return all data
    query = db.session.query(Customers).filter(Customers.storeID == current_user.id)
    # search filter
    search = request.args.get('search')
    if search:
        query = query.filter(db.or_(
            Customers.name.like(f'%{search}%'),
            Customers.phone.like(f'%{search}%'),
            Customers.description.like(f'%{search}%')
        ))
    total = query.count()
    # sorting
    sort = request.args.get('sort')
    if sort:
        order = []
        for s in sort.split(','):
            direction = s[0]
            name = s[1:]
            # Columns available for sorting
            if name not in ['timeVisted', 'timeCancelled', 'avgSpent', 'totalSpent']:
                name = 'name'
            col = getattr(Customers, name)
            if direction == '-':
                col = col.desc()
            order.append(col)
        if order:
            query = query.order_by(*order)
    # pagination
    start = request.args.get('start', type=int, default=-1)
    length = request.args.get('length', type=int, default=-1)
    if start != -1 and length != -1:
        query = query.offset(start).limit(length)
    # response
    return {
        'data': [user.to_dict() for user in query],
        'total': total,
    }


@app.route('/api/data', methods=['POST'])
def update():
    # fetch a tuple of user inputs
    data = request.get_json()
    if 'id' not in data:
        abort(400)
    user = Customers.query.get(data['id'])
    # match it to db with input field
    for field in ['name', 'description']:
        if field in data:
            # set data
            setattr(user, field, data[field])
    db.session.commit()
    return '', 204

