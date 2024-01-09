from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from flask import Flask, render_template, request, redirect, url_for
import sys

SCOPES = [
    'https://www.googleapis.com/auth/calendar'
    ]

# トップ画面を読み込み
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route("/connection", methods=["post"])
def connection():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        return '連携済みです'
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('calendar', 'v3', credentials=creds)
    # topic_name = 'projects/leafy-unity-409311/topics/gcal_auto' 
    return '同期が完了しました'

# def setup_webhook():
#     creds = connection()
#     service = build('calendar', 'v3', credentials=creds)

#     # ウェブフックの設定
#     webhook_request = {
#         'id': 'my-webhook-id',
#         'address': 'https://your-webhook-endpoint.com',  # ウェブフックを受信するエンドポイントのURL
#         'type': 'web_hook',
#         'params': {
#             'ttl': '3600000'  # ウェブフックの有効期限 (ミリ秒)
#         }
#     }

#     # ウェブフックの登録
#     service.calendarList().watch(body=webhook_request).execute()


# Google APIに接続
@app.route("/sync", methods=["post"])
def sync():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    calendar_id_a = 'masayuki.ikeda@datasuccess.co.jp'

    # アカウントAのカレンダーから新しいイベントを取得
    now = datetime.utcnow()
    start_time = now 
    end_time = now + timedelta(days=5)
    events_result = service.events().list(calendarId=calendar_id_a, timeMin=start_time.isoformat() + 'Z', timeMax=end_time.isoformat() + 'Z').execute()
    events = events_result.get('items', [])
    two_days_ago = now - timedelta(days=1)
    event_result = []
    for event in events:
        updated_str = event.get('updated')  # 'updated'キーから値を取得
        if updated_str:
            if datetime.strptime(event['updated'], "%Y-%m-%dT%H:%M:%S.%fZ") > two_days_ago:
                event_result.append(event)

    # カレンダーID（アカウントB）と新しいイベントの詳細を指定してイベントを作成
    for event in event_result:
        summary = '予定ブロック'
        description = ''
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))

        # 新しいイベントの情報を作成
        new_event = {
            'summary': summary,
            'description': description,
            'start': {'dateTime': start},
            'end': {'dateTime': end},
            'attendees': [{'email': 'masayuki.0927.ikeda@gmail.com'}]
        }
        service.events().insert(calendarId='masayuki.0927.ikeda@gmail.com', body=new_event).execute()
    return '同期が完了しました'

if __name__ == '__main__':
    app.run(port=8000)