#%%
import os
import sys
import json
import smtplib
import platform
import requests
from email.message import EmailMessage


def f(non_f_str: str):
    """
    f string implementation for the json variables
    """
    return eval(f'f"""{non_f_str}"""')

def get_file_path(filename):
    path = os.path.realpath(__file__) + "/"
    if platform.system() == "Windows": path.replace("\\", "/")
    return os.path.join(path, filename)

def check_login(address, password):
    """
    Verifies if the user put a valid email
    """
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(address, password)
        result = True
    except:
        result = False
    return result

def _send_email(address, to_email, subject, body, smtp):
    """
    Sends the email to the patient and doctors informing the test results
    """
    try:
        with open("mail_list.txt", "r") as _emails:
            emails = _emails.read()
        # transform ",", new lines and ";" into whitespace
        emails_list = emails.replace("\n"," ").replace(","," ").replace(";"," ").split(" ")
        cc = list(filter(lambda x: x!= "", emails_list)) # clean up the list
    except FileNotFoundError:
        cc = [""]

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = address
    msg['To'] = to_email
    msg['CC'] = cc
    msg.set_content(body)

    smtp.send_message(msg)

def send_mail(address, password, to_emails, subject, body):
    if type(to_emails) == str: to_emails = [to_emails]
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(address, password)
        for to_email in to_emails:
            _send_email(address, to_email, subject, body, smtp)
# %%
