#!/usr/bin/python

import argparse
import os

import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from io import FileIO
import httplib2
from oauth2client import client, GOOGLE_TOKEN_URI

CLIENT_SECRETS_FILE = "client_secret_929791903032-hpdm8djidqd8o5nqg2gk66efau34ea6q.apps.googleusercontent.com.json"
SCOPES = ['https://www.googleapis.com/auth/yt-analytics-monetary.readonly']
API_SERVICE_NAME = 'youtubereporting'
API_VERSION = 'v1'

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets

CLIENT_ID = "929791903032-hpdm8djidqd8o5nqg2gk66efau34ea6q.apps.googleusercontent.com"
CLIENT_SECRET = "YHDd4FrEFtqjhIkZhprwUMuy"
REFRESH_TOKEN = "1/RinJvsjGrAUvBj3QoHsHMvopmsf-7U0x1KCvhpo0cq0"
ACCESS_TOKEN = "ya29.GlubBs2CfFIMOsQRkqSxgAyff5rQ8aiu1IWI6j2Ery5MsuL4VOnr9s7owicF0C_vgM8USc1IDY03jXxWlQn7dCjn2MMa5Gzh6LWZlxqLdLnU2ib8YXPR8nialM1F"
credentials = client.OAuth2Credentials(
    access_token = ACCESS_TOKEN,
    client_id = CLIENT_ID,
    client_secret = CLIENT_SECRET,
    refresh_token = REFRESH_TOKEN,
    token_expiry = 3600,
    token_uri = "https://oauth2.googleapis.com/token",
    scopes= "https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
    user_agent="Bearer",
    revoke_uri= None)

http = credentials.authorize(httplib2.Http())
# Authorize the request and store authorization credentials.
def get_authenticated_service():
    # flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    # credentials = flow.run_local_server()
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

# Remove keyword arguments that are not set.
def remove_empty_kwargs(**kwargs):
    good_kwargs = {}
    if kwargs is not None:
        for key, value in kwargs.items():
            if value:
                good_kwargs[key] = value
    return good_kwargs


# Call the YouTube Reporting API's jobs.list method to retrieve reporting jobs.
def list_reporting_jobs(youtube_reporting, **kwargs):
    # Only include the onBehalfOfContentOwner keyword argument if the user
    # set a value for the --content_owner argument.
    kwargs = remove_empty_kwargs(**kwargs)

    # Retrieve the reporting jobs for the user (or content owner).
    results = youtube_reporting.jobs().list(**kwargs).execute()

    if 'jobs' in results and results['jobs']:
        jobs = results['jobs']
        for job in jobs:
            print('Reporting job id: %s\n name: %s\n for reporting type: %s\n'
                  % (job['id'], job['name'], job['reportTypeId']))
    else:
        print('No jobs found')
        return False
    return True

# Call the YouTube Reporting API's reports.list method to retrieve reports created by a job.
def retrieve_reports(youtube_reporting, **kwargs):
    # Only include the onBehalfOfContentOwner keyword argument if the user
    # set a value for the --content_owner argument.
    kwargs = remove_empty_kwargs(**kwargs)

    # Retrieve available reports for the selected job.
    results = youtube_reporting.jobs().reports().list(**kwargs).execute()
    print("results: ",results)
    if 'reports' in results and results['reports']:
        reports = results['reports']
        print(reports)
        for report in reports:
            try:
                print('Report dates: %s to %s\n       download URL: %s\n'
                  % (report['startTime'], report['endTime'], report['downloadUrl']))
            except KeyError:
                print('Report dates: %s to %s\n       download URL: %s\n'
                  % (report['startTime'], report['createTime'], report['downloadUrl']))

# Call the YouTube Reporting API's media.download method to download the report.
def download_report(youtube_reporting, report_url, local_file):
    request = youtube_reporting.media().download(
        resourceName=' '
    )
    request.uri = report_url
    fh = FileIO(local_file, mode='wb')
    # Stream/download the report in a single request.
    downloader = MediaIoBaseDownload(fh, request, chunksize=-1)

    done = False
    while done is False:
        status, done = downloader.next_chunk()
        if status:
            print('Download %d%%.' % int(status.progress() * 100))
    print('Download Complete!')

# Prompt the user to select a job and return the specified ID.
def get_job_id_from_user():
    job_id = input('Please enter the job id for the report retrieval: ')
    print('You chose "%s" as the job Id for the report retrieval.' % job_id)
    return job_id

# Prompt the user to select a report URL and return the specified URL.
def get_report_url_from_user():
    report_url = input('Please enter the report URL to download: ')
    print('You chose "%s" to download.' % report_url)
    return report_url


if __name__ == '__main__':
    #    Music: UPtu1ivBRvjYBGoz0m0Dfg
    #    Kids: ra8f1uKU-uu9osqlt3jb5g
    #    Ent: ncwbWh1Q1LCsMAeryRBocQ
    #    Aff: 9C1hXNjkMN_2GO7ARpaplw
    #    Music-TH: iTE9_S8Uo42n3JzGAiht1w
    #    Ent-TH: RPppPCMzH4DTihKfvR8EeA
    #    Aff-TH: xtl5pd5oPxbhI0dI0Qpkyg

    parser = argparse.ArgumentParser()
    parser.add_argument('--content_owner', default='UPtu1ivBRvjYBGoz0m0Dfg',
                        help='ID of content owner for which you are retrieving jobs and reports')
    parser.add_argument('--includeSystemManaged', default='True',
                        help='ID of content owner for which you are retrieving jobs and reports')
    parser.add_argument('--job_id', default=None,
                        help='ID of the job for which you are retrieving reports. If not ' +
                             'provided AND report_url is also not provided, then the script ' +
                             'calls jobs.list() to retrieve a list of jobs.')
    parser.add_argument('--report_url', default=None,
                        help='URL of the report to retrieve. If not specified, the script ' +
                             'calls reports.list() to retrieve a list of reports for the ' +
                             'selected job.')
    parser.add_argument('--local_file', default='yt_report.txt',
                        help='The name of the local file where the downloaded report will be written.')
    args = parser.parse_args()
    try:
        youtube_reporting = get_authenticated_service()
    except AttributeError:
        youtube_reporting = get_authenticated_service()
    try:
        # If the user has not specified a job ID or report URL, retrieve a list
        # of available jobs and prompt the user to select one.
        if not args.job_id and not args.report_url:
            if list_reporting_jobs(youtube_reporting,
                                   onBehalfOfContentOwner=args.content_owner,
                                   includeSystemManaged=args.includeSystemManaged):
                args.job_id = get_job_id_from_user()
        # If the user has not specified a report URL, retrieve a list of reports
        # available for the specified job and prompt the user to select one.
        if args.job_id and not args.report_url:
            retrieve_reports(youtube_reporting,
                             jobId=args.job_id,
                             onBehalfOfContentOwner=args.content_owner)
            args.report_url = get_report_url_from_user()
        # Download the selected report.
        if args.report_url:
            download_report(youtube_reporting, args.report_url, args.local_file)
    except HttpError as e:
        print('An HTTP error %d occurred:\n %s' % (e.resp.status, e.content))