import pandas as pd
from pbook import conn, db
from sqlalchemy.sql import text


def paidCus(allAppointInfo, t1Price, t2Price):
    # Clean the data so it only contains info needed
    sortedDf = pd.DataFrame(
        allAppointInfo,
        columns=['gName', 'sTime', 'eTime', 'status', 'cName', 'cNum', 'device', 'dura', 'tier', 'storeID'])
    sortedDf = sortedDf.drop(
        ['gName', 'sTime', 'eTime', 'device'], axis=1)

    # Remove customers without phone
    cus = sortedDf.loc[sortedDf['cNum'] != '']
    # Return customers that have paid with tier1 price
    t1Cus = cus.loc[cus['status'] == 'apbtn done']
    t1Cus = t1Cus.loc[t1Cus['tier'] == str(1)]
    # Return customers that have paid with tier2 price
    t2Cus = cus.loc[cus['status'] == 'apbtn done']
    t2Cus = t2Cus.loc[t2Cus['tier'] == str(2)]
    # I don't know WTF I'm doing, this thing doesn't scale if there are more tier list,
    # But this is the best I can do.
    # Create new column for customers spent today based on price tier
    tempSpentList = []
    for dura in t1Cus['dura']:
        for key in t1Price.keys():
            if str(dura) == key:
                tempSpentList.append(t1Price[key][0])

    t1Cus['spent'] = tempSpentList

    tempSpentList = []
    for dura in t2Cus['dura']:
        for key in t2Price.keys():
            if str(dura) == key:
                tempSpentList.append(t2Price[key][0])

    t2Cus['spent'] = tempSpentList

    paidCusDf = pd.concat([t1Cus, t2Cus], ignore_index=True)
    paidCusDf.drop(['status', 'dura', 'tier'], axis=1, inplace=True)
    return paidCusDf


def cancelledCus(allAppointInfo):
    # Clean the data so it only contains info needed
    sortedDf = pd.DataFrame(
        allAppointInfo,
        columns=['gName', 'sTime', 'eTime', 'status', 'cName', 'cNum', 'device', 'dura', 'tier', 'storeID'])

    sortedDf = sortedDf.loc[sortedDf['status'] == 'apbtn cancel'].reset_index()

    sortedDf = sortedDf.drop(
        ['gName', 'sTime', 'eTime', 'device', 'dura', 'tier', 'status', 'index'], axis=1)
    return sortedDf


def updateDb(paidDf, canedDf, currStoreID):
    for i in range(0, len(paidDf)):
        s = text("SELECT * FROM customers WHERE phone= :phone AND storeID= :id")
        result = conn.execute(s, phone=paidDf['cNum'][i], id=currStoreID).fetchone()
        print(result)
        # if the customer already in db
        if result is not None:
            stat = text(
                "UPDATE customers SET totalSpent=(totalSpent+:spent),timeVisted=(timeVisted+1) WHERE phone=:phone AND storeID=:storeID")
            conn.execute(stat, spent=int(paidDf['spent'][i]), phone=paidDf['cNum'][i], storeID=currStoreID)
            stat2 = text(
                "UPDATE customers SET avgSpent=(totalSpent/timeVisted) WHERE phone=:phone AND storeID=:storeID",
                {'phone': paidDf['cNum'][i], 'storeID': currStoreID})
            conn.execute(stat2, phone=paidDf['cNum'][i], storeID=currStoreID)
            db.session.commit()
        # if the customer is not in db and phone number is valid
        else:
            stat = text(
                "INSERT INTO customers(name,phone,totalSpent,timeVisted,timeCancelled,avgSpent,storeID) VALUES(:name,:phone, :spent,1,0,:spent,:storeID)")
            conn.execute(stat, name=paidDf['cName'][i], phone=paidDf['cNum'][i], spent=int(paidDf['spent'][i]),
                         storeID=currStoreID)


    for i in range(0, len(canedDf)):
        s = text("SELECT * FROM customers WHERE phone= :phone AND storeID= :id")
        result = conn.execute(s, phone=canedDf['cNum'][i], id=currStoreID).fetchone()

        if result is not None:
            stat = text(
                "UPDATE customers SET timeCancelled=(timeCancelled+1) WHERE phone=:phone AND storeID=:storeID")
            conn.execute(stat, phone=canedDf['cNum'][i], storeID=currStoreID)
        else:
            stat = text(
                "INSERT INTO customers(name,phone,totalSpent,timeVisted,timeCancelled,avgSpent,storeID) VALUES(:name, "
                ":phone,0,0,1,0,:storeID)")
            conn.execute(stat, name=canedDf['cName'][i], phone=canedDf['cNum'][i], storeID=currStoreID)

