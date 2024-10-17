import random

import time

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

import pandas as pd
import zipfile
import io
import os
import logging

import fnmatch

from datetime import datetime

# The 3GPP directory info
meeting_str = input('Enter the meeting id:').strip()
# meeting_str = '117'

# zip files will process (download, unzip) one at a time. The processed files are updated to the file
# in 'unzipped_files_list_path' for each batch size of 'zip_file_processing_batch_size'
# Minimum batch size is set at 2
zip_file_processing_batch_size = max(int(input('Enter the batch size:').strip()), 2)
# zip_file_processing_batch_size = 2

# Program sleeps a (uniform) random time between (0.1, max_sleep_time_zipfile_download) after each zip file download
# This avoid overloading the 3GPP server and also avoid unnecessary flag/block from 3GPP site
max_sleep_time_zipfile_download = int(input('Enter the max sleep time:').strip())
# max_sleep_time_zipfile_download = 0.1


def fetch_3gpp_directory(url_3gpp, folder_path, file_name):
    """
    Extract the list of file names, size, date in the given 3GPP meeting URL
    and save it to the given folder name and file name

    Args:
    url_3gpp (str): The URL of the 3GPP for the given 3GPP meeting
    folder_path (str): The path to the directory where the file should be saved.
    file_name (str): The file name for saving the file list in the meeting URL

    Returns:
    tdoc_file_list (pandas DataFrame): A list of filenames, size and date in the given URL
    """
    try:
        # Send a GET request to the URL
        response = requests.get(url_3gpp)
        # Raise an exception for bad status codes
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all table rows (tr) in the table body (tbody)
        rows = soup.find('tbody').find_all('tr')

        # Initialize lists to store the data
        data = []

        # Iterate through each row and extract the information
        for row in rows:
            columns = row.find_all('td')
            # Ensure the row has enough columns
            if len(columns) >= 4:
                # Extract the filename column
                filename = columns[1].text.strip()
                # Skip the "Parent Directory" entry
                if filename != "Parent Directory":
                    # Extract the size and date columns
                    date_str = columns[2].text.strip()
                    size = columns[3].text.strip()

                    # Parse the date string (date_str) to desired format
                    date = datetime.strptime(date_str, "%Y/%m/%d %H:%M")

                    data.append({
                        'Filename': filename,
                        'Size': size,
                        'Date': date
                    })

        # Create a DataFrame from the collected data
        tdoc_file_list = pd.DataFrame(data)

        print(f"tdoc list identified {url_3gpp}")
        logging.info('tdoc list identified:%s', url_3gpp)

        # Save the DataFrame to a CSV file
        # Ensure the folder exists
        os.makedirs(folder_path, exist_ok=True)

        # Construct the full file path
        file_path = os.path.join(folder_path, file_name)
        tdoc_file_list.to_csv(file_path, index=False)

        print(f"File list saved to: {file_path}")
        logging.info('File list saved to: %s', file_path)

        return tdoc_file_list

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the data: {e}")
        logging.error("An error occurred while fetching the data: %s", e)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        logging.error("An unexpected error occurred: %s", e)

    return []


def download_and_extract(url, extract_to='.'):
    """
    Download a ZIP file from a URL and extract its contents.

    Args:
    url (str): The URL of the ZIP file to download.
    extract_to (str): The directory to extract the contents to. Defaults to the current directory.

    Returns:
    list: A list of filenames that were extracted.
    """
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Create a ZipFile object from the content
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            # Extract all contents
            zip_ref.extractall(extract_to)
            # Get the list of files in the ZIP
            files = zip_ref.namelist()

        # log information
        logging.info("Successfully downloaded and extracted ZIP file: %s", url)
        logging.info("Extracted %s files to %s", len(files), os.path.abspath(extract_to))

        # return list of files extracted
        return files

    except requests.exceptions.RequestException as e:
        logging.error('Error downloading the file: %s', e)
        print(f"Error downloading the file: {e}")
    except zipfile.BadZipFile:
        logging.error('The file is not a zip file or is corrupted.')
        print("The file is not a zip file or is corrupted.")
    except Exception as e:
        logging.error('An unexpected error occurred: %s', e)
        print(f"An unexpected error occurred: {e}")

    return []


def get_meeting_directory_content_file_name(folder_path, file_name) -> str:
    """
    Check if a file exists and return the file path if it does, empty string otherwise.

    Args:
    folder_path (str): The path to the folder where the file should be located.
    file_name (str): The file name to check if it exists.

    Returns:
    full file path or empty string: The full file path if the file exists, empty string otherwise.
    """
    # Ensure the folder exists, if not create it
    os.makedirs(folder_path, exist_ok=True)

    file_path = os.path.join(folder_path, file_name)

    if os.path.isfile(file_path):
        return file_path
    else:
        return ""


def find_latest_downloaded_zipfilename(folder_path, format_timestamp) -> str:
    """
    Find the previously unzipped/downloaded zip file in the working folder exists.
    If one or more file exist, get the last downloaded zip file name and return
    Otherwise return an empty string ""

    Args:
    folder_path (str): The path to the folder where the file should be located.
    file_name (str): The filename to check if it exists.

    Returns:
    last_zipfile_name (str): The last downloaded zip file name or an empty string:
        The last downloaded zip file name if files exists, empty string otherwise.
    """
    # Ensure the folder exists, if not create it
    os.makedirs(folder_path, exist_ok=True)

    # Get the list of all files in the folder
    list_of_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    # Filter and get the desired format files. Desired format is 'unzipped_files_*.csv'
    # file_name_pattern = 'unzipped_files_*.csv'
    filtered_list_of_files = fnmatch.filter(list_of_files, pat='unzipped_files_*.csv')

    # If the list of 'filtered_list_of_files' is empty, return empty ("") string
    if len(filtered_list_of_files) == 0:
        print(f"Previously unzipped/downloaded files does not exist:{folder_path}")
        logging.info("Previously unzipped/downloaded files does not exist %s", folder_path)

        return ""

    # Iterate through all the files of desired format to find the last file
    # The file name has the time stamp and sort based on the time stamp
    time_stamp_of_files_list = []  # An empty list to save the time stamps of the files

    for current_file in filtered_list_of_files:
        # Find all the indices with '_'
        underscore_indices = [i for i, character in enumerate(current_file) if character == '_']

        # Convert the time stamp to date time object
        time_stamp_of_files = current_file[underscore_indices[2] + 1:len(current_file) - 4]
        time_stamp_of_files_list.append(time_stamp_of_files)

    # Sort the list of files in descending order (first element has the most recent file time stamp)
    time_stamp_of_files_list.sort(reverse=True, key=lambda date: datetime.strptime(date, format_timestamp))

    # Get the file name of the most recent file
    latest_name_unzipped_log_file = 'unzipped_files_' + meeting_str + '_' + time_stamp_of_files_list[0] + '.csv'
    latest_name_unzipped_log_file_fullpath = os.path.join(folder_path, latest_name_unzipped_log_file)

    print(f"Previously unzipped/downloaded files exist in folder {folder_path}, file {latest_name_unzipped_log_file}")
    logging.info("Previously unzipped/downloaded files exist in folder %s, file %s", folder_path, latest_name_unzipped_log_file)

    # Read from the file to a DataFrame
    unzipped_files_df = pd.read_csv(latest_name_unzipped_log_file_fullpath)
    # Get the last row 'zip_filename' column
    last_zipfile_name = unzipped_files_df.iloc[-1]['zip_filename']

    print(f"The last unzipped/downloaded file is {last_zipfile_name}")
    logging.info("The last unzipped/downloaded file is %s", last_zipfile_name)

    return last_zipfile_name



# A folder named ./Download_(meeting id) in the current folder - Use for saving log file, list of tdoc files etc
working_folder = './Download_' + meeting_str
# A folder named ./Download_(meeting id)/Docs in the current folder - Use for saving downloaded and unzipped files etc
doc_folder = working_folder + '/Docs'

# URL for the 3gpp site where the tdocs are located
url_meeting_docs = "https://www.3gpp.org/ftp/TSG_RAN/WG1_RL1/TSGR1_" + meeting_str + "/Docs"

# A file named '3gpp_directory_(meeting_str).csv' is created listing all the file names in the 'doc_folder'.
# If '3gpp_directory_(meeting_str).csv' file exist, read the tdoc list from the file.
# If '3gpp_directory_(meeting_str).csv' file does not exist, read the webpage 'url' and create the file
directory_content_csv = '3gpp_directory_' + meeting_str + '.csv'

# String used for the log file name based on time
time_stamp_format = '%Y%m%d_%H%M%S'
file_time_stamp = datetime.now().strftime(time_stamp_format)

# Configure the log file
logging.basicConfig(
    filename='SC3GPP' + meeting_str + '_' + file_time_stamp + '.log',  # Log file name
    level=logging.DEBUG,  # Log level
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log message format
)

# Print to console / log file
if len(meeting_str):
    print(
        f"Start processing meeting# {meeting_str}, with batch size {zip_file_processing_batch_size} in URL {url_meeting_docs}")
    logging.info("Start processing meeting# %s, with batch size %s in URL %s", meeting_str,
                 zip_file_processing_batch_size, url_meeting_docs)
else:
    print(f"Empty meeting# {meeting_str}")
    logging.error("Empty meeting# %s", meeting_str)

# Check if a file the '3gpp_directory_(meeting_str).csv' file exists and return the file path if it does,
# empty string otherwise.
meeting_dir_content_filename = get_meeting_directory_content_file_name(working_folder, directory_content_csv)

# If file exists, read the file and create a DataFrame 'zip_file_df'
# If the file does not exist, fetch the website and create the 'zip_file_df'
# 'zip_file_df' columns are 'Filename', 'Size', 'Date'
if meeting_dir_content_filename == "":
    # Fetch the data from the 3GPP website (URL) and create the DataFrame 'zip_file_df'
    print(f"Reading from:{url_meeting_docs} to create file {directory_content_csv} in folder {working_folder}")
    logging.info("Reading from:%s to create file %s in folder %s", url_meeting_docs, directory_content_csv,
                 working_folder)

    zip_file_df = fetch_3gpp_directory(url_meeting_docs, working_folder, directory_content_csv)

else:
    # Read from already existing csv file 'meeting_dir_content_filename' to create the 'zip_file_df'
    print(f"Reading from:{meeting_dir_content_filename} to download/unzip")
    logging.info("Reading from: %s to download/unzip", meeting_dir_content_filename)

    zip_file_df = pd.read_csv(meeting_dir_content_filename)

# Print to console the first few lines read
print(zip_file_df.head())

# DataFrame for storing the files downloaded and unzipped
# Column 0: filename contains the zip filename
# Column 1: files contains the extracted files comma separated
downloaded_files = pd.DataFrame(columns=['zip_filename', 'extracted_file_names'])

# Construct the full file path for saving the names of the downloaded and unzipped list of files for the given meeting
# filename format is 'unzipped_files_(meeting#)_(timestamp).csv'
# Use the same time stamp as the logfile for easy cross-reference
unzipped_files_list_name = 'unzipped_files_' + meeting_str + '_' + file_time_stamp + '.csv'
unzipped_files_list_path = os.path.join(working_folder, unzipped_files_list_name)

# Find the previously unzipped/downloaded zip file in the working folder
last_downloaded_zipfile_name = find_latest_downloaded_zipfilename(working_folder, time_stamp_format)

# If last downloaded is empty string, iterate over the entire list
# Otherwise, start from where last left off
if last_downloaded_zipfile_name == "":
    # In order to iterate over the entire list, set index_last_downloaded=0
    index_last_downloaded = -1
    print(f"No previously downloaded file {working_folder}")
    logging.info("No previously downloaded file: %s", working_folder)
else:
    # Find the row in 'zip_file_df' with value 'last_downloaded_zipfile_name'
    row_last_downloaded = zip_file_df.loc[zip_file_df['Filename'] == last_downloaded_zipfile_name]
    index_last_downloaded = row_last_downloaded.index

    print(f"Previously downloaded file exists. Start from {index_last_downloaded}")
    logging.info("Previously downloaded file exists. Start from: %s", index_last_downloaded)

# Keep track of the number of files processed
zip_file_count = 0

# Iterate over the list of zip files and download them
for row_index, file_info_row_value in zip_file_df.iterrows():
    # If the row_index is
    if row_index > index_last_downloaded:
        # Check if the file name is .zip
        # Download the zip file from the folder and unzipped it. Otherwise do nothing.
        zip_filename = file_info_row_value['Filename']

        if zip_filename[-4:] == '.zip':
            # The url for the zip file in 3GPP site
            url_zip_file = url_meeting_docs + '/' + zip_filename

            # Write to logfile/console
            print('Processing: ', url_zip_file)
            logging.info('Downloading: %s', url_zip_file)

            # Download and extract the ZIP file
            extracted_file_names = download_and_extract(url_zip_file, doc_folder)

            # Sleep for a uniform random time between 0.1s - 1s
            # Avoid too quick downloads to 3gpp website to avoid server overloading
            # and reduce the risk of blocking the program from the server side
            time.sleep(random.uniform(0.1, max_sleep_time_zipfile_download))

            # Append the list of extracted files to the list 'downloaded_files'
            extracted_zip_file_info = [zip_filename, ','.join(str(val) for val in extracted_file_names)]
            downloaded_files.loc[len(downloaded_files)] = extracted_zip_file_info

            # Print the list of extracted files
            if extracted_file_names:
                print(f"List of extracted files {zip_filename}")
                logging.info('List of extracted files %s', zip_filename)

                for file_name_tmp in extracted_file_names:
                    print(f"- {file_name_tmp}")
                    logging.info(file_name_tmp)
        else:
            print(f"File is not a zip file:{zip_filename}")
            logging.info("File is not a zip file: %s", zip_filename)

        zip_file_count = zip_file_count + 1

        # Write to file in every 'zip_file_processing_batch_size'
        if (zip_file_count % zip_file_processing_batch_size) == 0:
            # Write the names of the downloaded files to CSV file
            downloaded_files.to_csv(unzipped_files_list_path, index=False)

            print(f"Extracted list of files are written to:{unzipped_files_list_path}")
            logging.info("Extracted list of files are written to : %s", unzipped_files_list_path)
    else:
        zip_filename = file_info_row_value['Filename']
        print(f"Skip file (download/unzip):{zip_filename}")
        logging.info("Skip file (download/unzip):%s", zip_filename)

# Write the names of the downloaded files to CSV file (At the end of the for loop over all zip files)
downloaded_files.to_csv(unzipped_files_list_path, index=False)
