# coding: utf-8
from urllib import urlopen
from bs4 import BeautifulSoup
from datetime import datetime
import schedule
from threading import Thread
import lxml
import time
import string
import db

def getInmates(url):
    html = urlopen(url)
    bsObj = BeautifulSoup(html, "lxml")

    rows = bsObj.findAll('tr')

    for i in range(1,len(rows)):
        getInmateData(rows[i])
        time.sleep(1)

def getInmateData(row):
    data = row.findAll('td')
    url = data[0].a.attrs['href']
    bookingNumber = url[url.index('bookno=')+7:]

    name = data[0].getText()
    fname = name[name.index(',')+2:]
    lname = name[:name.index(',')]
    pod = data[1].getText()
    bookingDate = convertScrapeDate(data[2].getText())
    mni = data[3].getText().strip()
    mugshotURL = 'http://oldweb.circuit8.org/' + data[4].a.attrs['href']
    cases = getInmateCases(url)

    info = {
        'fname':fname,
        'lname':lname,
        'pod':pod,
        'bookingDate':bookingDate,
        'mni':mni,
        'mugshotURL':mugshotURL,
        'url':url,
        'bookingNumber':bookingNumber,
        'cases':cases
    }

    info.update(getInnerInmateData(url))
    print 'Scraping data for %s' % (info['bookingNumber'])
    db.appendNextInsert(info)



def getInnerInmateData(url):
    html = urlopen('http://oldweb.circuit8.org/' + url)
    bsObj = BeautifulSoup(html, "lxml")

    tables = bsObj.findAll('table')

    try:
        inmateInfo = tables[0].findAll('tr')[1].findAll('td')

        totalBond = float(inmateInfo[3].getText().replace(' ', '').replace('$','').replace(',',''))
        status = inmateInfo[4].getText()
        federal = inmateInfo[5].getText()
        otherCounty = inmateInfo[6].getText()
        hold = inmateInfo[7].getText()

        return {
            'totalBond':totalBond,
            'status':status,
            'federal':federal,
            'otherCounty':otherCounty,
            'hold':hold
        }
    except IndexError:
        return {
            'totalBond':'',
            'status':'',
            'federal':'',
            'otherCounty':'',
            'hold':''
        }



def getInmateCases(url):
    html = urlopen('http://oldweb.circuit8.org/' + url)
    bsObj = BeautifulSoup(html, "lxml")
    tables = bsObj.findAll('table')

    cases = []

    for i in range(1,len(tables)):
        cases.append(getCaseData(tables[i]))

    return cases

def getCaseData(table):
    rows = table.findAll('tr')
    caseData = rows[0].findAll('td')

    caseNumberTD = caseData[0].getText();
    caseNumber = caseNumberTD[caseNumberTD.index('#')+2:]

    agencyTD = caseData[1].getText();
    agency = agencyTD[agencyTD.index(':')+2:]

    bondAmountTD = caseData[2].getText();
    bondAmount = float(bondAmountTD[bondAmountTD.index(':')+2:].replace(' ', '').replace('$','').replace(',',''))

    statusTD = caseData[3].getText();
    status = statusTD[statusTD.index(':')+2:]

    charges = []

    for i in range(2,len(rows)):
        charges.append(getChargeData(rows[i]))

    return {
        'caseNumber':caseNumber,
        'agency':agency,
        'bondAmount':bondAmount,
        'status':status,
        'charges':charges
    }


def getChargeData(row):
    chargeData = row.findAll('td')

    statute = chargeData[1].getText()
    description = chargeData[2].getText()
    level = chargeData[3].getText()
    degree = chargeData[4].getText()

    return {
        'statute':statute,
        'description':description,
        'level':level,
        'degree':degree
    }

def convertScrapeDate(dateStr):
    date = string.split(dateStr, '/')
    dateObj = datetime(int(date[2]),int(date[0]),int(date[1]))
    return db.convertToSeconds(dateObj)


def scrapeJailSite():
    print 'Starting scrape...'
    db.startInsert();

    url = 'http://oldweb.circuit8.org/inmatelist.php'
    getInmates(url)

    db.commitInsert();
    print 'Scrape finished.'

def activateScraperTimer():
    schedule.every().day.at("00:00").do(scrapeJailSite)
    schedule.every().day.at("12:00").do(scrapeJailSite)
    while True:
        schedule.run_pending()
        time.sleep(1)

def newScrapeThread():
    thr = Thread(target=activateScraperTimer)
    thr.start()


