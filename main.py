from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import time
import pyttsx3
import speech_recognition as sr
import playsound
import pytz
import subprocess

import webScraping

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
MONTHS = ["january", "february", "march", "april", "may", "june","july", "august", "september","october", "november", "december"] 
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"] 
DAY_EXTENTIONS = ["rd", "th", "st", "nd"]

def speak(text):
	engine = pyttsx3.init()

	# rate of speak
	rate = engine.getProperty('rate')
	engine.setProperty('rate', 125)

	# voice
	voices = engine.getProperty('voices')
	engine.setProperty('voice',voices[1].id)

	engine.say(text)
	engine.runAndWait()


def get_audio():
	r = sr.Recognizer()
	with sr.Microphone() as source:
		audio = r.listen(source)
		said = ""

		try:
			said = r.recognize_google(audio)
			print(said)
		except Exception as e:
			print("Exception: "+str(e))

	return said.lower()


def authenticate_google():
   
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service


def get_event(day, service):
    # Call the Calendar API
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc = pytz.UTC
    date = date.astimezone(utc)
    end = end.astimezone(utc)

    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end.isoformat(),
                                         singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])
        start_time = str(start.split("T")[1].split("+")[0])

        if int(start_time.split(":")[0]) < 12:
        	start_time = start_time + "am"

        else:
        	start_time = str(int(start_time.split(":")[0])-12) + start_time.split(":")[1]
        	start_time = start_time + "pm"



        speak(event["summary"] + " at " + start_time)


service = authenticate_google()

def get_date(text):
	text = text.lower()
	today = datetime.date.today()

	if text.count("today") > 0:
		return today

	day = -1
	day_of_week = -1
	month = -1
	year = today.year


	for word in text.split():
		if word in MONTHS:
			month = MONTHS.index(word) + 1
		
		elif word in DAYS:
			day_of_week=DAYS.index(word)

		elif word.isdigit():
			day = int(word)

		else:

			for ext in DAY_EXTENTIONS:
				found = word.find(ext)
				if found > 0:
					try:
						day = int(word[:found])
						
					except:
						pass

	if month < today.month and month != -1:
		year = year + 1

	if month == -1 and day != -1:
		if day < today.day:
			month = today.month + 1
		else:
			month = today.month

	if month == -1 and day == -1 and day_of_week != -1:

		current_day_of_week = today.weekday()

		dif = day_of_week - current_day_of_week
		
		if dif < 0:
			dif += 7
			if text.count("next")>=1:
				dif+=7

		return today + datetime.timedelta(dif)

	if day != -1:
		return datetime.date(month=month,day=day,year=year)

def note(text):
	date = datetime.datetime.now()
	file_name = str(date).replace(":","-") + "-note.txt"
	with open(file_name , "w" ,encoding="utf-8") as f:
		f.write(text)
	
	
	subprocess.Popen(["notepad.exe", file_name])

# text = get_audio()
# print(get_date(text))
def open_program(path):
	subprocess.call([path])


SERVICE = authenticate_google()
print('start')
text = get_audio()


CALENDAR_STR = ["what do i have", "do i have plans", "am i busy"]

for pharase in CALENDAR_STR:
	if pharase in text:
		date = get_date(text)
		if date:
			get_event(date,SERVICE)
		else:
			speak("sorry. please try again.")

NOTE_STR = ["make a note", "write this down", "remember this", "type this"]

for pharase in NOTE_STR:
	if pharase in text:
		speak("what would you like me to write down?")
		write_down = get_audio()
		note(write_down)
		speak("l've made a note fo that")
	

WEBSCRAPING_STR = ["get the information of" , "search for a product"]

for pharase in WEBSCRAPING_STR:
	if pharase in text:
		speak("what product are you looking for?")
		product = get_audio()
		scrap = webScraping.webscraping(product)
		note(scrap)