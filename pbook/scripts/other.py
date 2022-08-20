import pandas as pd

storeId = 0
storeAppInfo = {}
allAppInfo = []

girlListDic = {'g1': [], 'g2': [], 'g3': [], 'g4': []}
girlPayDic = {'g1Pay': {}, 'g2Pay': {}, 'g3Pay': {}, 'g4Pay': {}}

currTier = 1


def colClassName(arg):
    colSwitcher = {
        1: "grid one",
        2: "grid two",
        3: "grid tre",
        4: "grid for",
    }
    return colSwitcher.get(arg, "none")


def setPTier(results):
    pTier1 = {'30': [results[5], results[15], results[5] - results[15]],
              '60': [results[6], results[16], results[6] - results[16]],
              '70': [results[7], results[17], results[7] - results[17]],
              '90': [results[8], results[18], results[8] - results[18]],
              '120': [results[9], results[19], results[9] - results[19]],
              }
    pTier2 = {'30': [results[10], results[20], results[10] - results[20]],
              '60': [results[11], results[21], results[11] - results[21]],
              '70': [results[12], results[22], results[12] - results[22]],
              '90': [results[13], results[23], results[13] - results[23]],
              '120': [results[14], results[24], results[14] - results[24]],
              }
    return [pTier1, pTier2]


def setGD(results):
    girlList = [results[1], results[2], results[3], results[4]]
    girlList = [name for name in girlList if name != ""]
    deviceList = [results[25], results[26], results[27], results[28]]
    deviceList = [device for device in deviceList if device != ""]
    return [girlList, deviceList]


''' This is dumb asf, but I cant figure out better ways.
    Take all the appInfo, sort them, isolate by name,
    then count by durations, return a dictionary.'''


def getGirlPay(allAppointInfo, girlName, priceTier):
    # Init dict that needs to be returned
    payDict = {'30': [0, 0, 0, 0, 0],
               '60': [0, 0, 0, 0, 0],
               '70': [0, 0, 0, 0, 0],
               '90': [0, 0, 0, 0, 0],
               '120': [0, 0, 0, 0, 0], }

    # Clean the data so it only contains info needed
    payDf = pd.DataFrame(
        allAppointInfo,
        columns=['gName', 'sTime', 'eTime', 'status', 'cName', 'cNum', 'device', 'dura', 'tier', 'storeID'])
    payDf = payDf.drop(['sTime', 'sTime', 'eTime', 'cName',
                        'cNum', 'device'], axis=1)
    payDf = payDf.loc[payDf['status'] == 'apbtn done']
    payDf.sort_values(by=['gName', 'dura'], inplace=True)

    # Return times done based on duration
    mask = payDf['gName'] == girlName
    payDf = payDf[mask].groupby(['dura']).count()
    payDf = payDf.drop(['status'], axis=1)

    # Map the times to dic
    for i in payDf.index:
        payDict[str(i)][0] = payDf.loc[str(i), 'gName']

    # Map pay ratio to dic and calculate total per duration
    for key in priceTier:
        payDict[key][1] = priceTier[key][1]
        payDict[key][2] = priceTier[key][2]
        payDict[key][3] = payDict[key][0] * payDict[key][1]
        payDict[key][4] = payDict[key][0] * payDict[key][2]

    compTotal = sum([payDict[key][3] for key in payDict])
    girlTotal = sum([payDict[key][4] for key in payDict])
    payDict['Comp Total'] = compTotal
    payDict['Girl Total'] = girlTotal
    return payDict


def dayEndPay(payDict):
    dayCharged = sum(
        [payDict[key]['Comp Total'] + payDict[key]['Girl Total'] for key in payDict.keys()])
    dayEarned = sum([payDict[key]['Comp Total'] for key in payDict.keys()])
    return [dayCharged, dayEarned]
