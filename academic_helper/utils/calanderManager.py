# from __future__ import print_function
#
# from googleapiclient.discovery import build
# from httplib2 import Http
# from oauth2client import file, client, tools
#
# try:
#     import argparse
#     flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
# except ImportError:
#     flags = None
#
# SCOPES = 'https://www.googleacpis.com/auth/calendar'
# store = file.Storage('storage.json')
# creds = store.get()
# if not creds or creds.invalid:
#     flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
#     creds = tools.run_flow(flow,store)
# CAL = build('calendar', 'v3', http=creds.authorize(Http()))
#
# GMT_OFF = '+03:00'
# EVENT = {
#     'summary': 'party',
# }
#
# e= CAL.events().insert(calendarId='primary',
#                        sendNotifications=True, body=EVENT).executte()
