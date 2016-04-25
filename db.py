# coding: utf-8
from datetime import date, datetime, timedelta
from titlecase import titlecase
from werkzeug.security import generate_password_hash, check_password_hash
from decimal import Decimal
import string
import random
import pymysql
import yagmail
import lxml
import dbInfo
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

####

# Inmate Functions

####

def getLastInmateId():
    try: 
        conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset)
        cur = conn.cursor()
        cur.execute("USE %s" % (dbInfo.db))

        cur.execute("SELECT id FROM inmates ORDER BY ID DESC LIMIT 1")
        cur.connection.commit()
        
        return int(cur.fetchone()[0])

        cur.close()
    finally:
        conn.close()

def checkInDB(bookingNumber):
    try: 
        conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset)
        cur = conn.cursor()
        cur.execute("USE %s" % (dbInfo.db))

        cur.execute('SELECT id FROM inmates WHERE bookingNumber = %s',(bookingNumber))
        cur.connection.commit()
        try:
            cur.fetchone()[0]
            return True
        except TypeError:
            return False
        cur.close()
    finally:
        conn.close()

def getInmateId(bookingNumber):
    try: 
        conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset)
        cur = conn.cursor()
        cur.execute("USE %s" % (dbInfo.db))

        cur.execute('SELECT id FROM inmates WHERE bookingNumber = %s',(bookingNumber))
        cur.connection.commit()
        try: 
            return int(cur.fetchone()[0])
        except TypeError:
            return -1
        cur.close()
    finally:
        conn.close()

def getCaseId(caseNumber):
    try: 
        conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset)
        cur = conn.cursor()
        cur.execute("USE %s" % (dbInfo.db))

        cur.execute('SELECT id FROM cases WHERE number = %s',(caseNumber))
        cur.connection.commit()
        try: 
            return int(cur.fetchone()[0])
        except TypeError:
            return -1
        cur.close()
    finally:
        conn.close()

def insertInmateData(inmateInfo):
    fname = titlecase(inmateInfo['fname'])
    lname = titlecase(inmateInfo['lname'])
    bookingNumber = inmateInfo['bookingNumber']
    pod = inmateInfo['pod']
    bookingDate = inmateInfo['bookingDate']
    mni = inmateInfo['mni']
    mugshotURL = inmateInfo['mugshotURL']
    totalBond = inmateInfo['totalBond']
    status = titlecase(inmateInfo['status'])
    federal = inmateInfo['federal']
    otherCounty = inmateInfo['otherCounty']
    hold = inmateInfo['hold']
    url = inmateInfo['url']
    removed = 0

    try: 
        conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset)
        cur = conn.cursor()
        cur.execute("USE %s" % (dbInfo.db))
        cur.execute('INSERT INTO inmates(fname, lname, bookingNumber, pod, bookingDate, mni, mugshotURL, totalBond, status, federal, otherCounty, hold, url,removed) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(fname,lname,bookingNumber,pod,bookingDate,mni,mugshotURL,totalBond,status,federal,otherCounty,hold,url,removed))
        cur.connection.commit()
        cur.close()
    finally:
        conn.close()

def insertCaseData(inmateId, caseInfo):
    caseNumber = caseInfo['caseNumber']
    agency = caseInfo['agency']
    bondAmount = caseInfo['bondAmount']
    status = titlecase(caseInfo['status'])

    try: 
        conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset)
        cur = conn.cursor()
        cur.execute("USE %s" % (dbInfo.db))
        cur.execute('INSERT INTO cases(inmateId, number, agency, bondAmount, status) VALUES(%s,%s,%s,%s,%s)',(inmateId,caseNumber,agency,bondAmount,status))
        cur.connection.commit()
        cur.close()
    finally:
        conn.close()

def insertChargeData(inmateId, caseId, chargeInfo):
    statute = chargeInfo['statute']
    description = chargeInfo['description'].lower().capitalize()
    level = chargeInfo['level']
    degree = chargeInfo['degree']

    try: 
        conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset)
        cur = conn.cursor()
        cur.execute("USE %s" % (dbInfo.db))
        cur.execute('INSERT INTO charges(inmateId, caseId, statute, description, level, degree) VALUES(%s,%s,%s,%s,%s,%s)',(inmateId,caseId,statute,description,level,degree))
        cur.connection.commit()
        cur.close()
    finally:
        conn.close()

def insertInmate(info):
    insertInmateData(info)
    inmateId = getInmateId(info['bookingNumber'])
    for caseInfo in info['cases']:
        insertCaseData(inmateId, caseInfo)
        caseId = getCaseId(caseInfo['caseNumber'])
        for chargeInfo in caseInfo['charges']:
            insertChargeData(inmateId,caseId,chargeInfo)

def addChange(bookingNumber, changeType):
    now = str(datetime.now().strftime("%B %d, %Y at %I:%M:%S %p"))
    inmateId = getInmateId(bookingNumber)
    try: 
        conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset)
        cur = conn.cursor()
        cur.execute("USE %s" % (dbInfo.db))
        cur.execute('INSERT INTO changelog(inmateId, changeType, date) VALUES (%s,%s,%s)',(inmateId,changeType,now))
        cur.connection.commit()
        cur.close()
    finally:
        conn.close()

def getChanges():
    try: 
        conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset, cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()
        cur.execute("USE %s" % (dbInfo.db))
        cur.execute('SELECT inmates.fname, inmates.lname, inmates.bookingNumber, changelog.changeType, changelog.date FROM changelog JOIN inmates ON inmates.id = changelog.inmateId ORDER BY date DESC')
        cur.connection.commit()

        results = cur.fetchall()
        cur.close()
    finally:
        conn.close()

    return results

def startInsert():
    global lastInsert
    lastInsert = getAllInmateNumbers()

    global nextInsert 
    nextInsert = []

def appendNextInsert(info):
    nextInsert.append(info)
    if not checkInDB(info['bookingNumber']):
        insertInmate(info)

def commitInsert():
    newAdditions = []
    
    try: 
        conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset, cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()
        cur.execute("USE %s" % (dbInfo.db))

        cur.execute('SELECT * FROM inmates') 
        cur.connection.commit()

        allInmates = cur.fetchall()

        cur.close()
    finally:
        conn.close()

    nextInsertBookingNumbers = []
    for insert in nextInsert:
        nextInsertBookingNumbers.append(insert['bookingNumber'])
        correspondingDBEntry = getEntryByValue(allInmates, 'bookingNumber',insert['bookingNumber'])
        if titlecase(insert['status']) != correspondingDBEntry['status']:
            updateInmate(insert['bookingNumber'],'status',titlecase(insert['status']))
        if insert['totalBond'] != correspondingDBEntry['totalBond']:
            updateInmate(insert['bookingNumber'],'totalBond',insert['totalBond'])

    for bookingNumber in lastInsert:
        try:
            nextInsertBookingNumbers.index(bookingNumber.encode('utf_8'))
        except ValueError:
            removeInmate(bookingNumber)
            addChange(bookingNumber, 'removed')

    for bookingNumber in nextInsertBookingNumbers:
        try:
            lastInsert.index(bookingNumber.decode('utf_8'))
        except ValueError:
            addChange(bookingNumber, 'added')
            newAdditions.append(bookingNumber)

    # checkAlerts(newAdditions)


def updateInmate(bookingNumber, column, value):
    try: 
        conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset)
        cur = conn.cursor()
        cur.execute("USE %s" % (dbInfo.db))
        sql = 'UPDATE inmates SET %s=%s WHERE bookingNumber = %s' % (column,'%s','%s')
        cur.execute(sql,(value, bookingNumber))
        cur.connection.commit()
        cur.close()
    finally: 
        conn.close() 

    if column == 'totalBond':
        column = 'bond'
    addChange(bookingNumber, 'updated %s' % (column))

def removeInmate(bookingNumber):
    try: 
        conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset)
        cur = conn.cursor()
        cur.execute("USE %s" % (dbInfo.db))
        cur.execute('UPDATE inmates SET removed=1 WHERE bookingNumber = %s',(bookingNumber))
        cur.connection.commit()
        cur.close()
    finally: 
        conn.close() 
   
def getAllInmateNumbers():
    try: 
        conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset)
        cur = conn.cursor()
        cur.execute("USE %s" % (dbInfo.db))
        cur.execute('SELECT bookingNumber FROM inmates WHERE removed !=1')
        cur.connection.commit()

        result = cur.fetchall()

        cur.close()
    finally:
        conn.close()

    output = []
    for bookingNumber in result:
        output.append(bookingNumber[0])

    return output

def getAllInmateData(activeOnly):
    try: 
        conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset, cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()
        cur.execute("USE %s" % (dbInfo.db))
        if activeOnly:
            cur.execute('SELECT * FROM inmates WHERE removed !=1')
        else:
           cur.execute('SELECT * FROM inmates') 
        cur.connection.commit()

        results = cur.fetchall()

        cur.close()
    finally:
        conn.close()

    for inmateData in results:
        inmateData['bookingDate'] = convertToDateString(inmateData['bookingDate'])
        inmateData['totalBond'] = '${:,.2f}'.format(inmateData['totalBond'])


    return results

def getSingleInmateData(bookingNumber):
    try: 
        conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset, cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()
        cur.execute("USE %s" % (dbInfo.db))

        cur.execute('SELECT * FROM inmates WHERE bookingNumber = %s',(bookingNumber))
        cur.connection.commit()
        inmateData = cur.fetchone()

        inmateId = getInmateId(bookingNumber)
        cur.execute('SELECT * FROM cases WHERE inmateId = %s',(inmateId))
        cur.connection.commit()
        inmateData['cases'] = cur.fetchall()

        for case in inmateData['cases']:
            cur.execute('SELECT * FROM charges WHERE caseId = %s',(case['id']))
            cur.connection.commit()
            case['charges'] = cur.fetchall()

        cur.close()
    finally:
        conn.close()

    inmateData['bookingDate'] = str(convertToDate(inmateData['bookingDate']).strftime("%B %d, %Y"))
    inmateData['totalBond'] = '${:,.2f}'.format(inmateData['totalBond'])
    for case in inmateData['cases']:
        case['bondAmount'] = '${:,.2f}'.format(case['bondAmount'])

    return inmateData

def removeDuplicates(dictList):
    outputDict = []
    for dictionary in dictList:
        if(dictionary not in outputDict):
            outputDict.append(dictionary)

    return outputDict

def searchDB(searching, searchType):
    if searchType == 'simple':
        searchTerms = string.split(searching, ' ')
        results = []
        for term in searchTerms:
            try:
                statusTerm = term;
                term = '%' + term + '%'

                conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset, cursorclass=pymysql.cursors.DictCursor)
                cur = conn.cursor()

                sql = "SELECT fname,lname,bookingNumber,bookingDate FROM inmates JOIN cases ON inmates.id = cases.inmateId JOIN charges ON cases.id = charges.caseId WHERE inmates.fname LIKE %s OR inmates.lname LIKE %s OR inmates.bookingNumber LIKE %s OR inmates.status LIKE %s OR inmates.mni LIKE %s OR cases.number LIKE %s OR cases.agency LIKE %s OR cases.status LIKE %s OR charges.statute LIKE %s OR charges.description LIKE %s OR charges.level LIKE %s OR charges.degree LIKE %s GROUP BY bookingNumber ORDER BY lname, fname"
                
                cur.execute(sql,(term,term,term,statusTerm,term,term,term,statusTerm,term,term,term,term))
                
                cur.connection.commit()
                results.extend(cur.fetchall())

                cur.close()
            finally:
                conn.close()

        results = removeDuplicates(results)
        for inmateData in results:
            inmateData['bookingDate'] = convertToDateString(inmateData['bookingDate'])

        return results

    elif searchType == 'advanced':
        searchTerms = {}

        # remove empty form results except for 'removed' which is needed
        removed = searching['removed']
        for key, value in searching.items():
            if searching[key] is not None and searching[key] != ''.decode('utf_8') and searching[key] is not False and searching[key] != 'None'.decode('utf_8'):
                searchTerms[key] = searching[key]
        searchTerms['removed'] = removed

        # date format cleanup
        if 'bookingDateMin' in searchTerms:
            bookingDatetimeMin = datetime.combine(searchTerms['bookingDateMin'], datetime.min.time())
            searchTerms['bookingDateMin'] = convertToSeconds(bookingDatetimeMin)

        if 'bookingDateMax' in searchTerms:
            bookingDatetimeMax = datetime.combine(searchTerms['bookingDateMax'], datetime.min.time())
            searchTerms['bookingDateMax'] = convertToSeconds(bookingDatetimeMax)

        # min/max cleanup
        if 'bookingDateMin' in searchTerms and 'bookingDateMax' in searchTerms and searchTerms['bookingDateMin'] > searchTerms['bookingDateMax']:
            temp = searchTerms['bookingDateMax']
            searchTerms['bookingDateMax'] = searchTerms['bookingDateMin']
            searchTerms['bookingDateMin'] = temp

        if 'bondMin' in searchTerms and 'bondMax' in searchTerms and searchTerms['bondMin'] > searchTerms['bondMax']:
            temp = searchTerms['bondMax']
            searchTerms['bondMax'] = searchTerms['bondMin']
            searchTerms['bondMin'] = temp

        sqlStart = 'SELECT * FROM inmates JOIN cases ON inmates.id = cases.inmateId JOIN charges ON cases.id = charges.caseId'
        sqlFilters = ' WHERE'
        sqlEnd = ' GROUP BY bookingNumber ORDER BY lname, fname'
        sqlParams = ()

        # start adding filters
        if 'fname' in searchTerms:
            sqlFilters += ' fname LIKE %s AND'
            sqlParams = sqlParams + ('%' + searchTerms['fname'] + '%',)

        if 'lname' in searchTerms:
            sqlFilters += ' lname LIKE %s AND'
            sqlParams = sqlParams + ('%' + searchTerms['lname'] + '%',)

        if 'bookingNumber' in searchTerms:
            sqlFilters += ' bookingNumber LIKE %s AND'
            sqlParams = sqlParams + ('%' + searchTerms['bookingNumber'] + '%',)

        if 'bookingDateMin' in searchTerms:
            sqlFilters += ' bookingDate >= %s AND'
            sqlParams = sqlParams + (searchTerms['bookingDateMin'],)

        if 'bookingDateMax' in searchTerms:
            sqlFilters += ' bookingDate <= %s AND'
            sqlParams = sqlParams + (searchTerms['bookingDateMax'],)

        if 'bondMin' in searchTerms:
            sqlFilters += ' totalBond >= %s AND'
            sqlParams = sqlParams + (searchTerms['bondMin'],)

        if 'bondax' in searchTerms:
            sqlFilters += ' totalBond >= %s AND'
            sqlParams = sqlParams + (searchTerms['bondMax'],)

        if 'agency' in searchTerms:
            sqlFilters += ' agency LIKE %s AND'
            sqlParams = sqlParams + ('%' + searchTerms['agency'] + '%',)

        if 'status' in searchTerms:
            sqlFilters += ' inmates.status = %s AND'
            sqlParams = sqlParams + (searchTerms['status'],)

        if 'statute' in searchTerms:
            sqlFilters += ' statute = %s AND'
            sqlParams = sqlParams + (searchTerms['statute'],)

        if 'description' in searchTerms:
            descriptionSearchTerms = string.split(searchTerms['description'], ' ')
            sqlFilters += ' ('
            for term in descriptionSearchTerms:
                sqlFilters += ' description LIKE %s OR'
                sqlParams = sqlParams + ('%' + term + '%',)
            sqlFilters = sqlFilters[:-3]
            sqlFilters += ') AND'

        if 'level' in searchTerms:
            sqlFilters += ' level = %s AND'
            sqlParams = sqlParams + (searchTerms['level'],)

        if 'degree' in searchTerms:
            sqlFilters += ' degree LIKE %s AND'
            sqlParams = sqlParams + ('%' + searchTerms['degree'] + '%',)

        if len(sqlFilters) <= 6:
            sqlFilters = ''
        else:
            sqlFilters = sqlFilters[:-4]

        sql = sqlStart + sqlFilters + sqlEnd

        try:
            conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset, cursorclass=pymysql.cursors.DictCursor)
            cur = conn.cursor()

            cur.execute(sql,sqlParams)
            
            cur.connection.commit()
            results = cur.fetchall()

            cur.close()
        finally:
            conn.close()

        results = removeDuplicates(results)

        for inmateData in results:
            inmateData['bookingDate'] = convertToDateString(inmateData['bookingDate'])
            inmateData['totalBond'] = '${:,.2f}'.format(inmateData['totalBond'])

        return results


def convertToDate(seconds):
    date = datetime(1970,1,1) + timedelta(seconds=seconds)
    return date

def convertToDateString(seconds):
    date = convertToDate(seconds)
    dateString = str(date.strftime("%m/%d/%y"))
    return dateString

def convertToSeconds(date):
    seconds = (date-datetime(1970,1,1)).total_seconds()
    return seconds

####

# User Functions

####

def addUser(username, password, fname, lname, email, permissions):
    pwHash = generate_password_hash(password)
    fname = titlecase(fname)
    lname = titlecase(lname)

    try:
        conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset)
        cur = conn.cursor()

        cur.execute("INSERT INTO users(username, password, fname, lname, email, permissions) VALUES (%s,%s,%s,%s,%s,%s)", (username, pwHash, fname, lname, email, permissions))
        
        cur.connection.commit()
        results = cur.fetchall()

        cur.close()
    finally:
        conn.close()

def getAllUsers():
    try:
        conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset, cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()

        cur.execute("SELECT username,fname,lname,email,permissions FROM users")
        
        cur.connection.commit()
        results = cur.fetchall()

        cur.close()
    finally:
        conn.close()

    return results

def authenticateUser(username, password):
    try:
        conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset)
        cur = conn.cursor()

        cur.execute("SELECT password FROM users WHERE username = %s", (username))
        
        cur.connection.commit()

        try:
            result = cur.fetchone()[0]
        except TypeError:
            return False

        cur.close()
    finally:
        conn.close()

    return check_password_hash(result, password)

def getUserData(username):
    try: 
        conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset, cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()
        cur.execute("USE %s" % (dbInfo.db))

        cur.execute("SELECT username, fname, lname, permissions, email FROM users WHERE username = %s", (username))

        cur.connection.commit()

        results = cur.fetchone()

        cur.close()
    finally:
        conn.close()

    return results

def getUserId(username):
    try: 
        conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset)
        cur = conn.cursor()
        cur.execute("USE %s" % (dbInfo.db))

        cur.execute('SELECT id FROM users WHERE username = %s',(username))
        cur.connection.commit()
        try: 
            return int(cur.fetchone()[0])
        except TypeError:
            return -1
        cur.close()
    finally:
        conn.close()

####

# Alert Functions

####

def generateNewKey():
    usedKeys = [];

    try: 
        conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset, cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()
        cur.execute("USE %s" % (dbInfo.db))

        cur.execute('SELECT uniqueKey FROM alerts')

        cur.connection.commit()

        results = cur.fetchall();

        cur.close()
    finally:
        conn.close()

    for result in results:
        usedKeys.append(result)

    output = ''

    for x in range(0, 39):
        determineType = random.random()
        if determineType < 0.4:
            charac = chr(int(random.random()*26+65))
        elif determineType < 0.8:
            charac = chr(int(random.random()*26+97))
        else:
            charac = int(random.random()*10)
        output += str(charac)

    if output in usedKeys:
        generateNewKey()
    else:
        return output


def addAlert(username, attribute, comparison, value):
    userId = getUserId(username)
    try: 
        conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset, cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()
        cur.execute("USE %s" % (dbInfo.db))

        cur.execute("INSERT INTO alerts(userId, attribute, comparison, value, uniqueKey) VALUES(%s, %s, %s, %s, %s)", (userId, attribute, comparison, value, generateNewKey()))

        cur.connection.commit()

        results = cur.fetchone()

        cur.close()
    finally:
        conn.close()

def deleteAlert(uniqueKey):
    try: 
        conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset, cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()
        cur.execute("USE %s" % (dbInfo.db))

        cur.execute("DELETE FROM alerts WHERE uniqueKey = %s", (uniqueKey))

        cur.connection.commit()

        results = cur.fetchone()

        cur.close()
    finally:
        conn.close()

def getAllAlerts(username):
    userId = getUserId(username)
    try: 
        conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset, cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()
        cur.execute("USE %s" % (dbInfo.db))

        cur.execute("SELECT * FROM alerts WHERE userId = %s", (userId))

        cur.connection.commit()

        results = cur.fetchall()

        cur.close()
    finally:
        conn.close()

    for result in results:
        result = cleanUpAlertNames(result)

    return results

def cleanUpAlertNames(alert):
    if alert['attribute'] == "totalBond":
        alert['value'] = '${:,.2f}'.format(float(alert['value']))
    elif alert['attribute'] == "description":
        alert['value'] = "'" + alert['value'] + "'" 
    else:
        alert['value'] =  titlecase(alert['value'])

    if alert['comparison'] == "==":
        alert['comparison'] = "is"
    elif alert['comparison'] == "in":
        alert['comparison'] = "contains"

    alert['attribute'] = alert['attribute'].replace('totalBond', 'Bond Amount')
    alert['attribute'] = alert['attribute'].replace('description', 'Charge')
    alert['attribute'] = alert['attribute'].replace('name', 'Name')
    alert['attribute'] = alert['attribute'].replace('level', 'Level')
    alert['attribute'] =  titlecase(alert['attribute'])

    return alert

def cleanUpAlerts(email):
    output = []
    # Remove Duplicates and clean up alert names
    for alert in email:
        alert['alert'] = cleanUpAlertNames(alert['alert'])

        unique = True
        for outputAlert in output:
            if alert['bookingNumber'] == outputAlert['bookingNumber'] and alert['alert'] == outputAlert['alert']:
                unique = False
        if unique:
            output.append(alert)

    return output


def checkAlerts(newAdditions):
    try: 
        conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset, cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()
        cur.execute("USE %s" % (dbInfo.db))

        cur.execute("SELECT * FROM alerts")

        cur.connection.commit()

        alerts = cur.fetchall()

        cur.close()
    finally:
        conn.close()

    charges = [];
    for inmate in newAdditions:
        try: 
            conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset, cursorclass=pymysql.cursors.DictCursor)
            cur = conn.cursor()
            cur.execute("USE %s" % (dbInfo.db))

            cur.execute('SELECT bookingNumber, fname, lname, totalBond, description, level FROM charges JOIN cases  ON charges.caseId = cases.id JOIN inmates ON charges.inmateId = inmates.id WHERE bookingNumber = %s', (inmate))
            cur.connection.commit()
            charges += cur.fetchall()

            cur.close()
        finally:
            conn.close()

    triggeredAlerts = []

    for alert in alerts:
        for charge in charges:
            if alert['attribute'] == 'totalBond':
                alert['value'] = Decimal(alert['value'])

            if alert['attribute'] == 'name':
                charge['name'] = charge['fname'] + ' ' + charge['lname']

            if alert['comparison'] == 'in':
                exec("if %r %s %r: triggeredAlerts.append({'to':%r,'bookingNumber':%r,'name':%r,'alert':{'attribute':%r,'comparison':%r,'value':%r}})" % (alert['value'], alert['comparison'], charge[alert['attribute']], alert['userId'], charge['bookingNumber'], charge['fname'] + " " + charge['lname'],str(alert['attribute']), str(alert['comparison']), str(alert['value'])))
            else:
                exec("if %r %s %r: triggeredAlerts.append({'to':%r,'bookingNumber':%r,'name':%r,'alert':{'attribute':%r,'comparison':%r,'value':%r}})" % (charge[alert['attribute']], alert['comparison'], alert['value'], alert['userId'], charge['bookingNumber'], charge['fname'] + " " + charge['lname'],str(alert['attribute']), str(alert['comparison']), str(alert['value'])))

    sendEmails(triggeredAlerts)


def sendEmails(triggeredAlerts):
    emails = {}
    for alert in triggeredAlerts:
        try:
            emails[alert['to']].append({'bookingNumber':alert['bookingNumber'],'name':alert['name'],'alert':alert['alert']})
        except KeyError:
            emails[alert['to']] = [{'bookingNumber':alert['bookingNumber'],'name':alert['name'],'alert':alert['alert']}]

    for key,email in emails.iteritems():
        email = cleanUpAlerts(email)
        try: 
            conn = pymysql.connect(host=dbInfo.host, unix_socket=dbInfo.unix_socket, user=dbInfo.user, passwd=dbInfo.passwd, db=dbInfo.db, charset=dbInfo.charset, cursorclass=pymysql.cursors.DictCursor)
            cur = conn.cursor()
            cur.execute("USE %s" % (dbInfo.db))

            cur.execute('SELECT email FROM users WHERE id = %s', (key))
            cur.connection.commit()
            emailAddress = cur.fetchone()['email']

            cur.close()
        finally:
            conn.close()

        to = emailAddress.encode("utf_8")
        subject = 'Email Alert (%s)' % (str(datetime.now().strftime("%m/%d/%y %p at %I:%M:%S")))
        html = 'The following alerts were triggered in the latest Alachua County Jail Inmate update. Click <a href="http://oldweb.circuit8.org/inmatelist.php">here</a> for the official source.'
        html += '<ul>'
        for alert in email:
            html += '<li><a href="http://localhost:5000/inmates/%s">%s</a> was added and meets the requirement "%s %s %s"</li>' % (alert['bookingNumber'],alert['name'],alert['alert']['attribute'],alert['alert']['comparison'],alert['alert']['value'])
        html += '</ul><p><em>You are recieving this email because you have elected to recieve email alerts based on Alachua County Inmate updates. If this is a mistake please contact alachuajailalert@gmail.com.</em></p>'
        
        yag = yagmail.SMTP({'alachuajailalert':'Alachua Jail Alert System'})
        yag.send(to, subject, contents = [html])

####

# Util Functions

####

def getEntryByValue(dictionary, key, value):
    for entry in dictionary:
        if entry[key] == value:
            return entry








        










