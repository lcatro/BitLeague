
# coding: utf-8 

from email import MIMEText
import smtplib

import configure


def send_email(target_email,title,data) :
    msg = email.MIMEText(data,'html','utf-8')
    msg['From'] = configure.smtp['email']
    msg['To'] = target_email
    msg['Subject'] = title
    server = smtplib.SMTP(configure.smtp['host'], configure.smtp['port'])
    
    server.login(configure.smtp['email'], configure.smtp['password'])
    server.sendmail(configure.smtp['email'], [target_email], msg.as_string())
    server.quit()

def send_valid_code_email(target_email,valid_code) :
    temple_title = 'Valid Code'
    temple_html = '''Valid Code is %d
    ''' % (valid_code)
    
    send_email(target_email,temple_title,temple_html)

def send_tips_email(target_email,data) :
    temple_title = 'Tips'
    temple_html = '''Dear User : <br/> %s
    ''' % (data)
    
    send_email(target_email,temple_title,temple_html)

def send_regedit_success_tips(target_email) :
    send_tips_email(target_email,'You Has Regedit This User ,Let go for new World !')


