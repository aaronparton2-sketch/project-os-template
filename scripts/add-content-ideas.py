"""Add content ideas to Aaron's Google Sheets content planner.

Usage: python add-content-ideas.py
Edit the `new_rows` list below with your content ideas before running.
"""
import json, sys, os

sys.stdout.reconfigure(encoding='utf-8')

# Load env vars from .env in project root
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, '..', '.env')

env_vars = {}
with open(env_path, 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, val = line.split('=', 1)
            env_vars[key.strip()] = val.strip()

sa_info = json.loads(env_vars['GOOGLE_SERVICE_ACCOUNT_JSON'])

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = service_account.Credentials.from_service_account_info(sa_info, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)

SPREADSHEET_ID = env_vars.get('GOOGLE_SHEETS_SPREADSHEET_ID', '')

# Columns: ID, Title/Hook, Audience Focus, Funnel Stage, Content Type, Primary Platform,
#           Cross-post, Angle, Core Promise, Problem/Pain, CTA, Assets Needed,
#           Priority, Effort, Due Date, Status, Owner, Link, Notes, Publish Date

new_rows = [
    # Add content idea rows here. Example:
    # ['1',
    #  'Video Title / Hook',
    #  'B2C - Creators',        # Audience Focus
    #  'Awareness',              # Funnel Stage
    #  'Long video',             # Content Type
    #  'YouTube',                # Primary Platform
    #  'IG, TikTok',            # Cross-post
    #  'Build-in-public',        # Angle
    #  'Core promise in one sentence.',
    #  'Problem or pain point this addresses.',
    #  'Call to action',
    #  'Assets needed (B-roll, screen recordings, etc.)',
    #  'P1',                     # Priority
    #  'M',                      # Effort (S/M/L)
    #  '01/01/2026',            # Due Date
    #  'Backlog',                # Status
    #  'Aaron',                  # Owner
    #  '',                       # Link
    #  'Notes about this content idea.',
    #  '05/01/2026'],            # Publish Date
]

if not new_rows:
    print("No rows to add. Edit the new_rows list in this script first.")
    sys.exit(0)

body = {'values': new_rows}
result = service.spreadsheets().values().append(
    spreadsheetId=SPREADSHEET_ID,
    range='Content!A2',
    valueInputOption='RAW',
    insertDataOption='INSERT_ROWS',
    body=body
).execute()

updated = result.get('updates', {})
print(f"Appended {updated.get('updatedRows', 0)} rows to Content sheet")
print(f"Range: {updated.get('updatedRange', 'unknown')}")
print("Done! Check your spreadsheet.")
