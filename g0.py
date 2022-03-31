import json
import os

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from typing import Tuple, Optional

from functions import from_base26
from sheet import Sheet

GOOGLE_DOCUMENT_ID_PREFIX = "https://docs.google.com/spreadsheets/d/"

GOOGLE_SPREADSHEET_SCOPE = "https://www.googleapis.com/auth/spreadsheets"


def range2int(r: str) -> Tuple[int, int]:
    assert "!" not in r, f"Unsupported format for range with list name: {r}"
    start, _, end = r.partition(":")
    return from_base26(start), from_base26(end)


class Creds:

    @staticmethod
    def auth(
            credentials_path: str,
            token_path: str,
            scopes: Tuple[str] = (GOOGLE_SPREADSHEET_SCOPE,)
    ) -> Credentials:
        creds = None
        scopes = list(scopes)  # not working with tuple
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, 'wt') as token:
                token.write(creds.to_json())
        return creds

    @staticmethod
    def service(path: str) -> Credentials:
        with open(path, "rt") as file:
            info = json.loads(file.read())

        return service_account.Credentials.from_service_account_info(info)


class Google(object):

    @staticmethod
    def get_sheet_id(url: str) -> str:
        assert url.startswith(GOOGLE_DOCUMENT_ID_PREFIX), f"Invalid URL for google sheet: {url}"
        without_prefix = url.lstrip(GOOGLE_DOCUMENT_ID_PREFIX)
        document_id, separator, leftovers = without_prefix.rpartition("/")  # should always return 3 items
        assert separator == "/", f"Invalid URL for google sheet: {url}"
        return document_id

    def __init__(self, credentials: Credentials):
        self.service = build('sheets', 'v4', credentials=credentials)
        self.sheets = self.service.spreadsheets()

    def load_sheet(self, document_id: str, cells: str, url: Optional[str] = None) -> Sheet:
        data = self.sheets.values()\
            .get(spreadsheetId=document_id, range=cells, valueRenderOption="FORMULA")\
            .execute()
        return Sheet(document_id, cells, data, url)

    def store_sheet(self, sheet: Sheet, cells: Optional[str] = None):
        if cells is not None:
            my_start, my_end = range2int(sheet.cells)
            req_start, req_end = range2int(cells)

            assert req_start >= my_start, f"Can't store sheet from {chr(req_start)} should be >= {chr(my_start)}"
            assert req_end <= my_end, f"Can't store sheet to {chr(req_end)} should be <= {chr(my_end)}"

            offset_start = req_start - my_start
            offset_end = req_end

            values = [row[offset_start:offset_end] for row in sheet.values]
            body = dict(range=cells, values=values)

            assert False, "This code is not tested!"
        else:
            body = sheet.data
            cells = sheet.cells

        self.sheets.values().update(
            spreadsheetId=sheet.document_id,
            valueInputOption='USER_ENTERED',
            range=cells,
            body=body
        ).execute()
