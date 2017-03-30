from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import sys
import traceback

import datetime
from time import sleep
import pprint
import re
pp = pprint.PrettyPrinter(indent=4)


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar' #.readonly'
CLIENT_SECRET_FILE = 'client_id.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'

service = ""

## remember Portgual, Germay
rhcountries = {
    'Croatia' : 'RH PTO Croatia',
    'Muharram' : 'RH PTO Malaysia', # Indonesia too?
    'Milan' : 'RH PTO Italy',
    'Victoria' : 'RH PTO Australia',
   'Argentina' : 'RH PTO Argentina',
   'Australia' : 'RH PTO Australia',
   'New South Wales' : 'RH PTO Australia',
   'Belgium' : 'RH PTO Belgium',
   'Brazil' : 'RH PTO Brazil',
   'Brisbane' : 'RH PTO Australia',
   'Queensland' : 'RH PTO Australia',
   'Canada' : 'RH PTO Canada',
   'Chile' : 'RH PTO Chile',
   'China' : 'RH PTO China',
   'Colombia' : 'RH PTO Colombia',
   'Colombita' : 'RH PTO Colombia',
   'Czech Republic' : 'RH PTO Czech Republic',
   'Denmark' : 'RH PTO Denmark',
    'Dubai' : 'RH PTO Dubai',
    'Finland' : 'RH PTO Finland',
    'France' : 'RH PTO France',
    'Germany' : 'RH PTO Germany',
    'Germay' : 'RH PTO Germany',
    'Hong Kong' : 'RH PTO Hong Kong',
    'Hungary' : 'RH PTO Hungary',
    'India' : 'RH PTO India',
    'Indonesia' : 'RH PTO Indonesia',
    'Ireland' : 'RH PTO Ireland',
    'Israel' : 'RH PTO Israel',
    'Italy' : 'RH PTO Italy',
    'Japan' : 'RH PTO Japan',
    'Korea' : 'RH PTO Korea',
    'Malaysia' : 'RH PTO Malaysia',
    'Mexico' : 'RH PTO Mexico',
    'Netherlands' : 'RH PTO Netherlands',
    'New Zealand' : 'RH PTO New Zealand',
    'Norway' : 'RH PTO Norway',
    'Poland' : 'RH PTO Poland',
    'Portgual' : 'RH PTO Portugal',
    'Portugal' : 'RH PTO Portugal',
    'Russia' : 'RH PTO Russia',
    'Singapore' : 'RH PTO Singapore',
    'South Africa' : 'RH PTO South Africa',
    'Spain' : 'RH PTO Spain',
    'Sweden' : 'RH PTO Sweden',
    'Switzerland' : 'RH PTO Switzerland',
    'Taiwan' : 'RH PTO Taiwan',
    'Thailand' : 'RH PTO Thailand',
    'The Netherlands' : 'RH PTO Netherlands',
    'Turkey' : 'RH PTO Turkey',
    'UAE' : 'RH PTO UAE',
    'UK' : 'RH PTO UK',
    'US' : 'RH PTO US',
    'Trading Window' : 'RH Company Events',
    'Red Hat Week' : 'RH Company Events',
    'ESPP Enrollment' : 'RH Company Events',
    'Company Quarterly Meeting' : 'RH Company Events',
    'Quarterly Company Meeting' : 'RH Company Events',
    'Earnings Call' : 'RH Company Events'
}

destcals = {}

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def clear_calendar(calId):
    global service
    page_token = None
    while True:
        events = service.events().list(calendarId=calId, pageToken=page_token).execute()
        for event in events['items']:
            service.events().delete(calendarId=calId, eventId=event['id']).execute()
            print("Deleted " + event['summary'])
            sleep(0.2)
        page_token = events.get('nextPageToken')
        if not page_token:
            break

def createIfDoesNotExist(event, destId, alias):
    try:
        event.pop('id', None)
        event.pop('attendees', None)
        #del event['extendedProperties']
        event.pop('htmlLink', None)
        event.pop('iCalUID', None)
        ##pp.pprint(event)
        ##service.events().delete(calendarId=srcId, eventId=event['id']).execute()
    
   

        if 'date' in event['start']:
            startDate = event['start']['date'] + "T00:00:00.0Z"
        else:
            startDate = event['start']['dateTime']

            
        ##startDate = datetime.datetime.strptime(event['start']['date'], "%Y-%m-%d").isoFormat() + "Z"

        summary = event['summary']

        sumq = summary
        ## add double quotes to make it possible to find events with apostrophes in them also trim the summary
        ## remove ( and )'s as they are not matched when searching with double quotes - put a space to avoid collision with next characters
        sumq = sumq.replace('(',' ')
        sumq = sumq.replace(')',' ')
        sumq = sumq.replace(',',' ')
        sumq = sumq.strip()
        sumq = '"'+sumq+'"'
        
        matches = service.events().list(calendarId=destId, timeMin=startDate, q=sumq, orderBy='updated').execute()
        foundevents = matches.get('items', [])
        foundsome = len(foundevents)
        if(foundsome>0):
            #print ("'" + summary + "' already exists in " + alias)
            sys.stdout.write('!')
            sys.stdout.flush()
            ## pp.pprint(foundevents)
        else:
            print("No match for '" + sumq + "' on " + alias)
            ##pp.pprint(event)
            newevent = service.events().insert(calendarId=destId, body=event).execute()
            print('Event created: %s' % (newevent.get('htmlLink')))
    except:
        e = sys.exc_info()[0]
        print("Error!")
        pp.pprint(event)
        traceback.print_exc()
        raise e

def enableSharing(calendar_list_entry):
    cid = calendar_list_entry['id']
    print("ACL " + calendar_list_entry['summary'])

    acl = service.acl().list(calendarId=cid).execute()
    for rule in acl['items']:
        pp.pprint(rule)
        if(rule['id']=='domain:redhat.com'):
            print(rule['role'])

            rule = {
                'scope': {
                    'type': 'domain',
                    'value': 'redhat.com',
                    },
                    'role': 'reader'
                }
                    
            created_rule = service.acl().insert(calendarId=cid, body=rule).execute()
                    
            print (created_rule['id'])
            
def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    global service

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)


    page_token = None
    while True:
        calendar_list = service.calendarList().list(showHidden = True, minAccessRole = 'writer', pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            destcals[calendar_list_entry['summary']] = calendar_list_entry['id']
            if(calendar_list_entry['summary'].startswith('RH ')):
            #    print("Clearing " + calendar_list_entry['summary'])
            #    clear_calendar(calendar_list_entry['id'])
            #    cid = calendar_list_entry['id']
            #    enableSharing(cid)
              ##  pp.pprint(calendar_list_entry)
                print(calendar_list_entry['summary'] + ' ' + "https://calendar.google.com/calendar/embed?src=" + calendar_list_entry['id'])
                          
                
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

    ##sys.exit(-1)
    ##pp.pprint(destcals)
    
    srcId = 'company@redhat.com'
   

    countries = {}
    page_token = None
    while True:
        events = service.events().list(calendarId=srcId, timeMin='2014-02-03T00:00:00.0Z', pageToken=page_token).execute()
        for event in events['items']:
            summary = event['summary']

            ## find all alias an event is relevant for
            all = set([])
            for s in rhcountries:
                if s in summary:
                    all.add(rhcountries[s])

            ## print what alias relevant or we failed.
            
            if(len(all)>0):
                #print(summary + " --> " + str(all))
                #print(".")
                sys.stdout.write('.')
                sys.stdout.flush()
            else:
                print("*** UNKNOWN -->" + summary)
                pp.pprint(event)
         

            ## Create event in matching alias, creating the calendar if not there.
            for alias in all:
                countries[alias] = countries.pop(alias,0) + 1
                destId = None
                if(alias in destcals):
                        destId = destcals[alias]
                else:
                    print("Want to create calendar: " + alias)
                    #service.calendars.insert(alias).execute()
                    newcalendar = {
                        'summary': alias,
                    }

                    created_calendar = service.calendars().insert(body=newcalendar).execute()
                    destId = created_calendar['id']
                    enableSharing(created_calendar)
                    destcals[alias] = destId

                createIfDoesNotExist(event, destId, alias)

                        
                
                
        sleep(0.2)
            
        page_token = events.get('nextPageToken')
        if not page_token:
            break

    print("I'm done!")
    pp.pprint(countries)
if __name__ == '__main__':
    main()
