#!/usr/bin/python

import re, urllib2, smtplib, time
from email.mime.text import MIMEText
from optparse import OptionParser

crns=[]
emailAddr=""
interval=10
term=20131

parser = OptionParser()
parser.add_option("-c", "--crn", type="int", dest="crns", action="append", help="Course Registration Number of the class to watch", metavar="CRN")
parser.add_option("-m", "--email", type="string", dest="emailAddr", help="Email to send updates to", metavar="EMAIL ADDRESS")
parser.add_option("-i", "--interval", type="int", dest="interval", help="Minutes to pause between checks, default is 10", metavar="INTERVAL")
parser.add_option("-t", "--term", type="int", dest="term", action="store", help="Integer representing term to check in format (YEAR OF SPRING TERM)(SEASON CODE) season code is 1 for fall, 2 for spring, and 3 for summer. defaults to fall 2012.", metavar="TERM")
(options, args)=parser.parse_args()

emailAddr = options.emailAddr;
crns = options.crns;
if (options.interval):
    interval = options.interval
if(options.term):
    term = options.term

def sendEmail(toAddr, fromAddr, subject, message):
    message = MIMEText(message);
    message["Subject"] = subject;
    message["From"] = fromAddr;
    message["To"] = toAddr;
    
    s = smtplib.SMTP("smtp.purdue.edu");
    s.sendmail(fromAddr, [toAddr], message.as_string());
    s.quit();

def getAvailable(crn):
    # Download the web page
    url = "https://selfservice.mypurdue.purdue.edu/prod/bwckschd.p_disp_detail_sched?term_in=" + str(term) + "0&crn_in=" + str(crn);
    print url
    res = urllib2.urlopen(url);
    data = res.read(1024 * 1024);
    
    # RegExp Match
    pattern = "<td class=\"dddefault\">([0-9]*)</td>.*?<td class=\"dddefault\">([0-9]*)</td>.*?<td class=\"dddefault\">([0-9]*)</td>";
    matches = re.findall(pattern, data, re.MULTILINE + re.DOTALL + re.I);
    return matches[0][2];
    
def loop():
    reported=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    #Initialize the boolean array
    #for q in range(len(crns)):
    #    reported[q] = 0
    #    print reported[q]
    #    print crns

    while True:
        for k in range(len(crns)):
            openSeats=getAvailable(crns[k]);
	    if(openSeats >= 1 and reported[k] == 0): #When it is open
                subject = "{seats} Seats are open for CRN #{crn}".format(seats = openSeats, crn=crns[k])
                message = "{seats} Seats are open in the class you are watching with CRN #{crn}".format(seats = openSeats, crn=crns[k])
                sendEmail(emailAddr, "PresidentCordova@purdue.edu", subject,  message)
                reported[k] = 1
            elif(openSeats < 1 and reported[k] == 0): #When it is closed
                subject = "Registration for CRN #{crn} is closed.".format(crn=crns[k])
                message = "We regret to inform you that the class for which you are trying to register (CRN #{crn}) has closed registration after filling all of its seats. We will happily keep an eye on it for you and notify you of any changes.".format(crn=crns[k])
                sendEmail(emailAddr, "PresidentCordova@purdue.edu", subject,  message)
                reported[k] = 1

        time.sleep(interval * 60);

loop();
