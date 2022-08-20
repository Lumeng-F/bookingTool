from datetime import datetime, timedelta
import pandas as pd


# Sort list of AppointInfo by time and remove duplicates
def sortAppointInfo(girlAppInfo):
    temp = pd.DataFrame(
        girlAppInfo,
        columns=['gName', 'sTime', 'eTime', 'status', 'cName', 'cNum', 'device', 'dura', 'tier', 'storeID'])
    temp = temp.drop_duplicates(
        subset=temp.columns.difference(['status']))
    temp = temp.sort_values(by=['sTime'])
    allAppointInfo = temp.values.tolist()
    return allAppointInfo


# Sort girl appointment list by names for display
def getLists(allAppointInfo, matchname):
    temp = []
    for appInfo in allAppointInfo:
        if appInfo[0] == matchname:
            temp.append(appInfo)
    return temp


# Change status (had to do this to support python 3.9)
def statusChange(status):
    switcher = {
        "apbtn default": "apbtn done",
        "apbtn done": "apbtn cancel",
        "apbtn cancel": "apbtn default",
    }

    return switcher.get(status, "none")


# Change sTime & eTime & status
def onStatusChange(appInfo):
    appInfo[3] = statusChange(appInfo[3])
    appInfo[1] = datetime.now()
    appInfo[2] = (datetime.now() + timedelta(minutes=int(appInfo[7])))


# Check overlapping appointments
def checkOverlapping(currAppTime, newAppTime):
    if newAppTime[1] < currAppTime[1] or newAppTime[0] < currAppTime[1]:
        errMsg = f'Appointment exist between {str(currAppTime[0].time())[:5]} - {str(currAppTime[1].time())[:5]}'
        return errMsg
    if newAppTime[0] < currAppTime[0] and newAppTime[1] > currAppTime[1]:
        errMsg = f'Appointment exist between {str(currAppTime[0].time())[:5]} - {str(currAppTime[1].time())[:5]}'
        return errMsg
    else:
        return None
