import os
import sys
import pwd
from tqdm import tqdm
from datetime import datetime
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

gauth = GoogleAuth()
scope = ["https://www.googleapis.com/auth/drive"]
gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'secrets.json', scope)
drive = GoogleDrive(gauth)

FILENAME = f'backup_{datetime.now().replace(microsecond=0).isoformat().replace(":", "-")}' + \
    f'_{pwd.getpwuid(os.getuid())[0]}.tar.gz'
IMAGES_FILENAME = f'images_{datetime.now().replace(microsecond=0).isoformat().replace(":", "-")}' + \
    f'_{pwd.getpwuid(os.getuid())[0]}.tar.gz'


def convert_bytes(byte_size):
    byte_size = float(byte_size)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if byte_size < 1024.0:
            break
        byte_size /= 1024.0
    return "{:.2f} {}".format(byte_size, unit)


def create_tar(filename, directories, change_dir=False):
    print('Creating tar archive...')
    if change_dir:
        os.system(
            f'sudo tar -C {change_dir} -czf {filename} {" ".join(directories)}')
    else:
        os.system(f'sudo tar czf {filename} {" ".join(directories)}')


def extract_tar(filename):
    print('Extracting tar archive...')
    os.system(f'sudo tar xzfp {filename}')


def upload_to_google_drive(filename):
    file = drive.CreateFile({'title': filename})
    file.SetContentFile(f'{filename}')
    print(f'Uploading {filename}...')
    file.Upload()
    print(f'Uploaded {filename} to Google Drive.')


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

    with tqdm(total=float(file['fileSize']), unit='B', unit_scale=True, unit_divisor=1024, desc="Downloading file") as pbar:
        def progress_callback(bytes_downloaded, total_bytes):
            pbar.update(bytes_downloaded - pbar.n)

        if not os.path.exists(file['title']):
            file.GetContentFile(file['title'], callback=progress_callback)
        else:
            pbar.update(float(file['fileSize']) - pbar.n)

    if file['title'].startswith('backup'):
        extract_website_backup(file['title'])
    elif file['title'].startswith('images'):
        extract_images_backup(file['title'])


def delete_from_google_drive():
    file_list = list_files_in_google_drive()
    index = int(
        input('Enter id of the file to delete (default: 0): ') or 0)
    if index < 0 or index >= len(file_list):
        print('Invalid id.')
        sys.exit(1)
    file = file_list[index]
    print(f'Deleting {file["title"]}...')
    file.Delete()
    print(f'Deleted {file["title"]} from Google Drive.')


def upload_website_backup():
    print('Checking if MariaDB container is running...')
    if os.system('sudo docker ps | grep mariadb') != 0:
        print('MariaDB container is not running.')
        print('run docker compose up -d')
        sys.exit(1)

    os.system('sudo chmod -R 777 src db_dump')
    os.system(
        'docker exec mariadb mysqldump --user=root --password=admin presta_database > db_dump/db.sql')
    create_tar(FILENAME, ['src', 'db_dump'])
    upload_to_google_drive(FILENAME)
    option = input('Delete created archive? (y/n): ')
    if option == 'y':
        os.system(f'sudo rm -rf {FILENAME}')


def extract_website_backup(filename):
    print('Deleting src, database and db_dump directories...')
    os.system('sudo rm -rf src database db_dump')
    extract_tar(filename)


def upload_images_backup():
    create_tar(IMAGES_FILENAME, ['images'], change_dir='../scraper_results')
    upload_to_google_drive(IMAGES_FILENAME)
    option = input('Delete created archive? (y/n): ')
    if option == 'y':
        os.system(f'sudo rm -rf {IMAGES_FILENAME}')


def extract_images_backup(filename):
    print('Deleting images directory...')
    os.system('sudo rm -rf ../scraper_results/images')
    extract_tar(filename)
    os.system('sudo mv images ../scraper_results/')


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print('Usage: python script.py <upload|download|delete>')
        sys.exit(1)

    OPERATION = sys.argv[1]

    info = drive.GetAbout()
    print(
        f"Disk usage: {convert_bytes(info['quotaBytesUsed'])} / " +
        f"{convert_bytes(info['quotaBytesTotal'])}")

    if OPERATION == 'upload':
        print('[0] CREATE AND UPLOAD WEBSITE BACKUP')
        print('[1] CREATE AND UPLOAD IMAGES BACKUP')
        option = int(input('Enter option (default: 0): ') or 0)
        if option == 0:
            upload_website_backup()
        elif option == 1:
            upload_images_backup()
    elif OPERATION == 'download':
        download_from_google_drive()
    elif OPERATION == 'delete':
        delete_from_google_drive()
    else:
        print('Invalid operation. Please specify either upload, download or delete.')
