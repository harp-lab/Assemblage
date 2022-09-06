#!/usr/bin/env python

"""

This script will grab data from S3 and push it into Google Drive.

I mostly cribbed it from a Medium article, and edited it to work with the needs of Assemblage.

Originally Adapted from
https://github.com/dspenard/google-drive-with-aws/blob/main/src/google-drive-lambda.py
MIT Licensed
More info at the blog post: https://medium.com/analytics-vidhya/push-aws-s3-files-to-google-drive-dabf5005a278
"""


import tempfile
import os
import sys
import json
import tarfile
import zipfile
from datetime import date

from apiclient import discovery
from apiclient import errors
from apiclient.http import MediaFileUpload

import boto3

from google.oauth2 import service_account
import googleapiclient.discovery

def get_folder_id_and_service_account_creds(folder_id_param, credentials_param):
    """
    Queries AWS SSM's ParameterStore for stored data,
    And then forms the credentials to access Google Drive API.

    returns: The Google Drive folder we will push into, and a credentials object to access the Google API.
    """

    sesh = boto3.Session(profile_name='assemblage')
    ssm_client = sesh.client('ssm')

    folder_id = ssm_client.get_parameter(Name=folder_id_param, WithDecryption=True)['Parameter']['Value']
    creds_str = ssm_client.get_parameter(Name=credentials_param, WithDecryption=True)['Parameter']['Value']
    creds_json = json.loads(creds_str)

    scopes_list = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file'
    ]

    credentials = service_account.Credentials.from_service_account_info(creds_json, scopes=scopes_list)

    # note for using a credentials json file instead
    # service_account_file = './credentials.json'
    # credentials = service_account.Credentials.from_service_account_file(service_account_file, scopes=scopes_list)

    return folder_id, credentials

def upload_file(service, file_name_with_path, file_name, description, folder_id, mime_type):
    """
    Uploads a file to Google Drive to the designated folder in a shared drive.

    Args:
        service: Google Drive API service instance.
        file_name_with_path: Source location of the file just downloaded to the Python tmp folder.
        file_name: Name of file to be saved to Google, and also for its title in the file metadata.
        description: Description of the file to insert, for the file metadata.
        folder_id: Parent folder's ID for the Google Drive shared folder where the file will be uploaded.
        mime_type: MIME type of the file to insert.

    Returns: file info
    """
    media_body = MediaFileUpload(file_name_with_path, mimetype=mime_type)

    # If two files with the same name are created, GDrive does not care, they are given different IDs.
    # So, Lets not do that.
    body = {
        'name': file_name,
        'title': file_name,
        'description': description,
        'mimeType': mime_type,
        'parents': [folder_id]
    }

    file = service.files().create(
        supportsAllDrives=True,
        body=body,
        media_body=media_body).execute()

    print(f"Uploaded: {file_name}, {file}")

    return file


def main_handler():
    """
    Pull files from S3 and push into a shared folder in GDrive.
    """

    bucket = "assemblage-data"
    # Two parameters found in the AWS 'Parameter Store' (search for that in the search-bar).
    # Create/Find this by checking the medium article at the top of this file.
    credentials_parameter = "google-service-account-credentials"
    # Get this by going into the folder on GDrive and looking at the URL.
    folder_id_parameter = "google-drive-folder-id"

    folder_id, credentials = get_folder_id_and_service_account_creds(folder_id_parameter, credentials_parameter)

    # note regarding cache_discovery=False
    # https://github.com/googleapis/google-api-python-client/issues/299
    service = discovery.build('drive', 'v3', credentials=credentials, cache_discovery=False)

    sesh = boto3.Session(profile_name='assemblage')
    s3_client = sesh.client('s3')


    # Set this to False for testing with smaller amounts.
    move_all = True

    files_to_move = []
    if move_all:
        paginator = s3_client.get_paginator('list_objects')
        # Get all files in the `data` folder of the bucket.
        page_iter = paginator.paginate(Bucket='assemblage-data', Prefix='data')

        for page in page_iter:
            files = [item['Key'] for item in page['Contents']]
            files_to_move.extend(files)
    else:
        # Retrieve MaxKeys objects from S3 (max/default is 1000).
        files = s3_client.list_objects(Bucket='assemblage-data', Prefix='data', MaxKeys=1000)['Contents']
        files_to_move = [f['Key'] for f in files]



    with tempfile.TemporaryDirectory() as tmpdir:
        upload_path = f'{tmpdir}/completed.tar'
        # This is the folder hierarchy that the data in S3 uses.
        hierarchy_dirs = f'{tmpdir}/data/binaries/ftp'
        # This is where the zips in the nightly will be aggregated before 'tar'ing.
        out_path = f'{tmpdir}/output'
        os.makedirs(hierarchy_dirs, exist_ok=True)
        os.makedirs(out_path, exist_ok=True)
        for file_name in files_to_move:
            s3_client.download_file(bucket, file_name, f'{tmpdir}/{file_name}')
        today = date.today().strftime('%Y_%m_%d')
        out_tar_location = f'{tmpdir}/nightly_{today}.tar'

        # Dont need to delete the tar, should be swept with the tmpdir.
        with tarfile.open(upload_path, 'w') as tar:
            for dl_zip in os.listdir(hierarchy_dirs):
                with zipfile.ZipFile(f'{hierarchy_dirs}/{dl_zip}', 'r') as z:
                    dl_zip_name = dl_zip[:-4]
                    for zf in (zf for zf in z.namelist() if zf.endswith('.exe') or zf.endswith('.dll')):
                        z.extract(zf)
                        final_zip_name = f'{dl_zip_name}_{zf}.zip'
                        with zipfile.ZipFile(f'{out_path}/{final_zip_name}', 'w') as outz:
                            outz.write(zf, arcname=f'{dl_zip_name}_{zf}')
                        tar.add(f'{out_path}/{final_zip_name}', arcname=final_zip_name)
                        os.remove(zf)
                        os.remove(f'{out_path}/{final_zip_name}')

        today = date.today().strftime('%Y_%m_%d')
        upload_name = f'nightly_{today}.tar'
        upload_file(service, upload_path, upload_name, upload_name, folder_id, 'application/zip')


if __name__ == '__main__':
    main_handler()
