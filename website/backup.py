import os
import sys
import pwd
from datetime import datetime
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

gauth = GoogleAuth()
scope = ["https://www.googleapis.com/auth/drive"]
gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'secrets.json', scope)
drive = GoogleDrive(gauth)


def convert_bytes(byte_size):
    byte_size = float(byte_size)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if byte_size < 1024.0:
            break
        byte_size /= 1024.0
    return "{:.2f} {}".format(byte_size, unit)


def create_tar_archive():
    print('Creating tar archive...')
    if os.system('sudo docker ps | grep mariadb') != 0:
        print('MariaDB container is not running.')
        print('run docker compose up -d')
        sys.exit(1)

    os.system('sudo chmod a+w db_dump')
    os.system(
        'docker exec mariadb mysqldump --user=root --password=admin presta_database > db_dump/db.sql')
    os.system(f'sudo tar czf {FILENAME} src db_dump')


def upload_to_google_drive():

    create_tar_archive()
    file = drive.CreateFile({'title': FILENAME})
    file.SetContentFile(f'{FILENAME}')
    print('Uploading file to Google Drive...')
    file.Upload()
    print(f'Uploaded {FILENAME} to Google Drive.')


def list_files_in_google_drive():

    file_list = drive.ListFile().GetList()

    if len(file_list) == 0:
        print('No files found on Google Drive.')
        sys.exit(1)
    file_list.sort(key=lambda x: x['createdDate'], reverse=True)

    for i, file in enumerate(file_list):
        print(f"[{i}] {file['title']} - {convert_bytes(file['fileSize'])}")

    return file_list


def download_from_google_drive():

    file_list = list_files_in_google_drive()

    index = int(
        input('Enter id of the file to download (default: 0): ') or 0)

    if index < 0 or index >= len(file_list):
        print('Invalid id.')
        sys.exit(1)

    file = file_list[index]
    print('Downloading file from Google Drive...')
    if os.path.exists(file['title']):
        os.remove(file['title'])
    file.GetContentFile(file['title'])
    print('Deleting src and database directories...')
    os.system('sudo rm -rf src database db_dump')
    print('Extracting tar archive...')
    os.system(f'sudo tar xzfp {file["title"]}')


def delete_from_google_drive():

    file_list = list_files_in_google_drive()

    index = int(
        input('Enter id of the file to delete (default: 0): ') or 0)

    if index < 0 or index >= len(file_list):
        print('Invalid id.')
        sys.exit(1)

    file = file_list[index]
    print('Deleting file from Google Drive...')
    file.Delete()
    print(f'Deleted {file["title"]} from Google Drive.')


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print('Usage: python script.py <upload|download|delete>')
        sys.exit(1)

    OPERATION = sys.argv[1]
    FILENAME = f'backup_{datetime.now().replace(microsecond=0).isoformat().replace(":", "-")}' + \
        f'_{pwd.getpwuid(os.getuid())[0]}.tar.gz'

    info = drive.GetAbout()
    print(
        f"Disk usage: {convert_bytes(info['quotaBytesUsed'])} / " +
        f"{convert_bytes(info['quotaBytesTotal'])}")

    if OPERATION == 'upload':
        upload_to_google_drive()
    elif OPERATION == 'download':
        download_from_google_drive()
    elif OPERATION == 'delete':
        delete_from_google_drive()
    else:
        print('Invalid operation. Please specify either upload or download.')
