# Import the packages needed
import os
import shutil
import logging
# from pyngrok import ngrok  # import ngrok
import openai
import requests
import zipfile
import io
import docx2txt
import threading
# from fractions import Fraction
from flask import Flask, render_template, request
from openai import OpenAI
from datetime import datetime


# Compute the BERT score
# from bert_score import score


def create_log_file(meetingid, tdocnumber, workingfolder):
    """
    Creates a log file in the folder specified by workingfolder
    log file format is log_<meetingid>_<tdocnumber>_<timestamp>.log>
    Example: log_118_R1-2405963_20241112_094854.log
    :param meetingid (str): meeting id
    :param tdocnumber (str): tdoc number
    :param workingfolder (str): working folder
    :return logfilenamefull (str): log file full path
    """
    # String used for the log file name based on time
    time_stamp_format = '%Y%m%d_%H%M%S'
    file_time_stamp = datetime.now().strftime(time_stamp_format)

    logfilename = 'log_' + meetingid + '_' + tdocnumber + '_' + file_time_stamp + '.log'
    logfilenamefull = get_file_path(workingfolder, logfilename)

    # Configure the log file
    logging.basicConfig(filename=logfilenamefull,  # Log file name
                        level=logging.DEBUG,  # Log level
                        format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
                        force=True
                        )
    # Log a message to confirm
    logging.debug(f"Log file created {logfilenamefull}")
    # Return the log file path for later use
    return logfilenamefull


def create_log_folder(meeting_id):
    """
    Creates a folder for log file saving using the specified meeting_id
    :param meeting_id (str):
    :return log_folder (str): log folder name
    """
    # log folder path
    log_folder = './log_' + meeting_id
    try:
        os.makedirs(log_folder, exist_ok=True)
    except OSError as e:
        # Raise the error/exception
        raise e

    return log_folder


def create_working_folder(meeting_id):
    """
    Creates a folder using the specified meeting_id
    :param meeting_id (str): meeting id
    :return (str): folder path
    """
    # Create working_folder folder
    working_folder = './download_' + meeting_id
    try:
        os.makedirs(working_folder, exist_ok=True)
    except OSError as e:
        # Raise the error/exception
        raise e

    return working_folder


def delete_working_folder(folderpath):
    """
    Deletes the specified folder
    :param folderpath (str): folder path to be deleted
    :return: None
    """
    try:
        # Check if the folder exists
        if os.path.exists(folderpath):
            try:
                shutil.rmtree(folderpath)
                logging.info(f"Folder '{folderpath}' and all its contents have been deleted.")
            except OSError as e:
                logging.error(f"Error deleting the folder {folderpath} : {e}")
        else:
            logging.info(f"Folder '{folderpath}' does not exist.")
    except Exception as e:
        logging.error(f"Error in handling the folder {folderpath} : {e}")


def download_and_extract_tdoc(meetingid, tdocnumber, workingfolder):
    """
    Downloads the specified tdoc and extracts it into the specified workingfolder
    From the meeting id and tdocnumber, the url for downloading the tdoc is created
    The zip file may contain more than one file. Search through all extracted files to locate the tdoc
    :param meetingid (str): the meeting id of the tdoc
    :param tdocnumber (str): the tdoc number
    :param workingfolder (str): the folder where the tdoc will be extracted
    :return tdocfile (str): the extracted tdoc file name and empty string if no tdoc file was found
    :return err (str): error string (if any) otherwise an empty string
    """

    logging.debug(f'Download & extract: meeting#{meetingid},TDoc#{tdocnumber},working folder:{workingfolder}')

    # The url for the zip file in 3GPP site
    url_tdoc_zip_file = "https://www.3gpp.org/ftp/TSG_RAN/WG1_RL1/TSGR1_" + meetingid + "/Docs/" + tdocnumber + ".zip"

    err = ''

    try:
        # Send a GET request to the URL
        response = requests.get(url_tdoc_zip_file)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Create a ZipFile object from the content
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            # Extract all contents
            zip_ref.extractall(workingfolder)
            # Get the list of files in the ZIP
            files = zip_ref.namelist()

        # check if the provided tdoc number is a contribution or not
        # There are documents in the folder which are not TDoc.
        # They may be agreements, wayforwards etc
        # 3GPP TDoc name starts the docx file name with the tdoc number
        logging.debug(f'processing files {files}')
        tdocfile = ''
        for filename in files:
            if filename.lower().startswith((tdocnumber.lower())):

                logging.debug(f'Found a file name begins with tdoc number: {filename}')

                if filename.lower().endswith(('.docx')):
                    tdocfile = filename
                    err = ''
                    logging.debug(f'File found is a docx file: {tdocfile}')
                    break
                else:
                    logging.info(f'Not Found: {filename.lower()}, {tdocnumber.lower()}')
                    err = "File must be a Word document (.docx) format"

        # After iterating through all files, a docx file starting with tdoc number is not found
        if tdocfile == '':
            logging.warning(
                f'After iterating through all files, a docx file starting with tdoc number is not found: {filename.lower()}, {tdocnumber.lower()}')
            if err == '':
                err = f"After iterating through all files, a docx file starting with tdoc number is not found"
                logging.error(err)

        # return the file name
        return tdocfile, err

    except requests.exceptions.RequestException as e:
        err = f"Check if the meeting id and tdoc number are correct. Attempting to download the file: {e}"
        logging.error(err)
    except zipfile.BadZipFile:
        err = f"The file is not a zip file or is corrupted."
        logging.error(err)
    except Exception as e:
        err = f"An unexpected error occurred: {e}"
        logging.error(err)

    return [], err


def get_file_path(folder, filename):
    """
    Returns the full file path by combining the folder and filename.

    Args:
    folder (str): The path to the folder.
    filename (str): The name of the file.

    Returns:
    str: The full path to the file.
    """
    return os.path.join(folder, filename)


def get_tdoc_content(filepath, userkey, callapi):
    """
    Generate text summary. If callapi is
    :param filepath (str): The full path to the file where input text is
    :param userkey (str): key to call gpt-4o API (prompt)
    :param callapi (bool): Whether to call the gpt-4o API (prompt) or not
    :return summary_generated (str): the summary generated from gpt-4o API
    :return inputtext (str): the text of the file
    :return err (str): any errors during the processing
    """
    if not filepath.lower().endswith(('.docx')):
        summary_generated = ''
        inputtext = ''
        err = "File must be a Word document (.docx) format"
        logging.error(err)
        return summary_generated, inputtext, err

    try:
        # Extract text from the specified file
        inputtext = docx2txt.process(filepath)
        err = ''
        logging.debug('Text extracted successfully')

        summary_generated, err = generate_text_summary(userkey, inputtext, callapi=callapi)
        logging.debug(f'Text summary generated successfully, APIcall:{callapi}')

        return summary_generated, inputtext, err

    except Exception as e:
        summary_generated = ''
        inputtext = ''
        err = Exception(f"Error in extracting text from tdoc {str(e)}")
        logging.error(err)
        return summary_generated, inputtext, err


# Generate the summary from AI model
def generate_text_summary(userkey, inputtext, callapi=False):
    """
    Generate text summary from input text.
    :param userkey (str): key to call gpt-4o API (prompt)
    :param inputtext (str): the text of the file (long original text)
    :param callapi (bool): Whether to call the gpt-4o API (prompt) or not:
    :return summary(str): The summary generated from gpt-4o API (prompt)
                          or first 2000 characters (for debugging purposes)
    :return err(str): any errors during the processing
    """

    # Generate a summary (return the first characters if callapi is False)
    if not callapi:
        summary = inputtext[0:2000]
        err = ''
        logging.debug(f'Text summary generation first characters APIcall:{callapi}')
    # Generate the summary from AI model (LLM)
    else:
        summary, err = generate_openai_summary(userkey, inputtext, temperature=0.1, model='gpt-4')
        logging.debug(f'Text summary generation openai APIcall:{callapi}')

    return summary, err


def generate_openai_summary(openAIkeyforUser, inputtext, temperature, model):
    """
    Generate text summary from input text using the gpt-4o API.
    :param openAIkeyforUser (str): key to call gpt-4o API (prompt)
    :param inputtext (str): the text of the file (long original text)
    :param temperature (float): the temperature of the gpt-4o API
    :param model (str): the gpt-4o model to generate summary from
    :return: summary(str): The summary generated from gpt-4o API (prompt)
    :return err(str): any errors during the processing
    """
    err = ''
    summarygenerated = ''

    logging.info(f"Open AI API {model}, {temperature}")

    # Get open AI key for the session
    openAIkeyforUser = os.getenv("OPENAI_API_KEY")

    # Generate summary using lower temperature, specific prompt and gpt-4o
    client = OpenAI(api_key=openAIkeyforUser)

    try:
        # Attempt to create a chat completion
        response_openai = client.chat.completions.create(
            messages=[
                {"role": "system",
                 "content": "You are acting as a 3GPP Standard Delegate specializing in the RAN (Radio Access "
                            "Network) Working Group 1 (WG1) for 5G/6G standardization. Generate a summary report from "
                            "the text using terms common in 3GPP."},
                {"role": "assistant",
                 "content": "Title of the summary is 'Document summary: Document title, document number. Include the "
                            "document title, meeting number, agenda item, document number, title, source, "
                            "document for, location information at the top of the summary. Some documents list "
                            "observations as items, for example, 'observation 1', 'observation 2' etc. If such "
                            "observations exists in the document, include such observations in the summary. If "
                            "explanations or reasons for such observation is described in the document, "
                            "provide a brief summary."},
                {"role": "system",
                 "content": "Some documents list proposals as items for example, 'proposal 1', 'proposal 2' etc. If "
                            "such proposals exists in the document, include such proposals in the summary."},
                {"role": "assistant",
                 "content": "An explanation for the proposal is usually provided. Include such explanation in the "
                            "summary."},
                {"role": "system",
                 "content": "Some documents list observations as items, for example, 'observation 1', 'observation 2' "
                            "etc. If such observations exists in the document, include such observations in the "
                            "summary."},
                {"role": "user", "content": inputtext}
            ],
            model=model,
            temperature=temperature,
        )

        # Retrieve and print the response if successful
        logging.info("OpenAI API call was successful.")

        # Extract the response content
        summarygenerated = response_openai.choices[0].message.content
        return summarygenerated, err

    except Exception as e:
        err = str(e)
        logging.error(f"OpenAI API returned an error: {err}")
        if "authentication" in err.lower():
            err = f"Authentication failed. Check your API key. {err}"
            logging.error(err)
        if "rate limit" in err.lower():
            err = f"Rate limit exceeded. Try again later. {err}"
            logging.error(err)
        if "invalid" in err.lower():
            err = f"The request was invalid. Check your parameters. {err}"
            logging.error(err)
        else:
            err = f"An unexpected OpenAI error occurred.{err}"
            logging.error(err)

        return summarygenerated, err


# Get the user authenticated and return the respective key for the API
def authenticate_user():
    """
    Retrieve the openai API key from the environment
    :return userkey (str): openai api key
    :return err (str): error message (if API key is not set)
    """
    err = ''
    userkey = os.getenv("OPENAI_API_KEY")
    # Check if the API key is not found
    if not userkey:
        err = f"Error: OPENAI_API_KEY environment variable is not set."
        logging.error(err)
    else:
        logging.info("OPENAI_API_KEY successfully retrieved.")

    # return the API key and error
    return userkey, err


def calculate_bert_score(tdoc_summary_txt, tdoc_txt):
    # Calculate BERTScore
    P, R, F1 = score([tdoc_txt], [tdoc_summary_txt], lang="en", model_type="bert-base-uncased")

    # Log BERTScore results
    p_mean = P.mean().item()
    r_mean = R.mean().item()
    f1_mean = F1.mean().item()

    logging.info(f"Precision:{p_mean}, Recall: {r_mean}, F1 Score: {f1_mean}")

    return p_mean, r_mean, f1_mean


# Rate (semantic) the summary with gpt model
def calculate_semantic_score(tdocsummarytxt, tdoctxt, userkey, model):
    """
    Generate a semantic score for the given abstractive summary. Prompt specifies the score style
    :param tdocsummarytxt: summary text
    :param tdoctxt: original long text
    :param userkey: API key for gpt-4o
    :param model: openai model (gpt-4o)
    :return: Score in the following format
                Relevance: [score]/10
                Coherence: [score]/10
                Completeness: [score]/10
                Conciseness: [score]/10
                Overall: [score]/10
    """
    # openai.api_key = userkey
    openai.api_key = os.getenv("OPENAI_API_KEY")

    logging.info(f'Calculate semantic score')
    # Rating prompt for OpenAI API
    prompt = f""" Given the following original text and its generated summary, please evaluate the quality of the 
    summary based on four criteria: relevance, coherence, completeness, and conciseness. For each criterion, 
    provide a rating from 1 to 10, with 10 being the best. Then, give an overall rating.

      Original Text:
      {tdoctxt}

      Generated Summary:
      {tdocsummarytxt}

      Provide your response in the following format:
      Relevance: [score]/10
      Coherence: [score]/10
      Completeness: [score]/10
      Conciseness: [score]/10
      Overall: [score]/10
  """
    err = ''
    ratingsummary = ''

    try:
        # Send the prompt to OpenAI API
        response_summary_rating = openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],  # the messages format
            temperature=0.01  # Set to a low temperature for more consistent ratings
        )

        # Extract the response content
        ratingsummary = response_summary_rating.choices[0].message.content
        # log the message
        logging.info(f'Rating summary {ratingsummary}')

        return ratingsummary, err

    except Exception as e:
        err = str(e)
        logging.error(f"OpenAI API returned an error: {err}")
        if "authentication" in err.lower():
            err = f"Authentication failed. Check your API key. {err}"
            logging.error(err)
        if "rate limit" in err.lower():
            err = f"Rate limit exceeded. Try again later. {err}"
            logging.error(err)
        if "invalid" in err.lower():
            err = f"The request was invalid. Check your parameters. {err}"
            logging.error(err)
        else:
            err = f"An unexpected OpenAI error occurred.{err}"
            logging.error(err)

        return ratingsummary, err


# Main code for Flask

os.environ["FLASK_DEBUG"] = "1"  # "development"

app = Flask(__name__)


# port = 5000
# Open a ngrok tunnel to the HTTP server
# public_url = ngrok.connect(port).public_url
# print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, port))

# Update any base URLs to use the public ngrok URL
# app.config["BASE_URL"] = public_url


@app.route('/', methods=['GET', 'POST'])
def index():
    text_summary = ''
    error_message = None
    meeting_id = ""  # Empty field
    tdoc_number = ""  # Empty field
    score = ''

    if request.method == 'POST':
        # Extract meeting ID and tdoc number from the request form
        meeting_id = request.form.get("meeting_id")
        tdoc_number = request.form.get("tdoc_number")

        # Create a folder to save the log files
        log_folder = create_log_folder(meeting_id)
        log_path = create_log_file(meeting_id, tdoc_number, log_folder)
        logging.info(f"Loging file created at:{log_path}")

        logging.info(f"Summarization request: meeting:{meeting_id},Tdoc:{tdoc_number}")

        # Check for errors in the user input
        error_tdoc = ''
        if tdoc_number.strip().startswith('R1-'):
            tdoc_number = tdoc_number.strip()
            logging.info(f"Processing request {tdoc_number}")
        elif tdoc_number.strip().lower().startswith('r1-'):
            tdoc_number = tdoc_number.strip().replace('r1-', 'R1-')
            logging.info(f"Processing request {tdoc_number}")
        else:
            tdoc_number = tdoc_number
            error_tdoc = 'Wrong input TDoc number:' + tdoc_number
            error_message = error_tdoc
            logging.error(error_message)

        # Create a folder to work (download/extract the tdoc)
        # This folder is deleted at the end
        working_folder = create_working_folder(meeting_id)
        logging.info(f"Working folder created at: {working_folder}")

        logging.info(f"Processing request: meeting id:{meeting_id},TDoc#:{tdoc_number}")

        # No errors found on the TDoc number
        if error_tdoc == '':
            # Download the tdoc from 3GPP FTP server, extract the zip file and find the word (.docx) file
            # .docx file is saved in the working folder

            tdoc_file_name, err = download_and_extract_tdoc(meeting_id, tdoc_number, working_folder)
            if err != '':
                logging.error(f"Download/extract error: {err}")
                error_message = err
            else:
                logging.info(f"Download success:{tdoc_file_name}")
                # TDoc (.docx) file path
                file_path = get_file_path(working_folder, tdoc_file_name)

                # call_api is used for controlling the gpt-4o api call
                # gpt-4o api calls bills based on the number of requests/tokens.
                # When developer debugging other functional blocks, call_api = False does not call gpt-4o prompt.
                # If call_api = False, only first 2000 characters of the extracted TDoc is returned
                # If call_api = True, gpt-4o prompt is called (billed)
                call_api = True  # False  #

                # Get the user authenticated and get an API key
                # Set the OPENAI_API_KEY environment variable
                user_key = authenticate_user()

                # Generate the text summary
                tdoc_summary_txt, tdoc_txt, err_summary_gen = get_tdoc_content(file_path, user_key, call_api)
                if err_summary_gen != '':
                    logging.error(f"error:', {err_summary_gen}")
                    error_message = err_summary_gen
                else:
                    logging.info(f"Summary generated:'{err_summary_gen}")
                    text_summary = tdoc_summary_txt
                    # print('content:', tdoc_summary_txt)

                # p_mean, r_mean, f1_mean = calculate_bert_score(tdoc_summary_txt, tdoc_txt)
                # logging.info(f"BERTScore: Precision:{p_mean}, Recall: {r_mean}, F1 Score: {f1_mean}")

                if call_api:
                    logging.info(f"Semantic score from API")
                    rating_summary, err_score_cal = calculate_semantic_score(tdoc_summary_txt, tdoc_txt, user_key,
                                                                             model='gpt-4')

                    # If score calculation is successful,show to the user
                    if err_score_cal == '':
                        logging.info(f"Semantic score {rating_summary}")

                        # Split the string into lines and find the line that starts with "Overall"
                        for line in rating_summary.splitlines():
                            if line.startswith("Overall:"):
                                overall_score = line.split(": ")[1]
                                logging.info(f"Overall score: {overall_score}")
                                score = overall_score
                else:
                    score = 'Not calculated'

        # Remove the working folder
        delete_working_folder(working_folder)

    # Return a render_template function, passing text summary, error messages, score
    # The meeting id and the tdoc number also sent back to update/display the web interface
    return render_template("index.html", text_summary=text_summary, error_message=error_message,
                           meeting_id=meeting_id, tdoc_number=tdoc_number, score=score)


if __name__ == '__main__':
    # Start the Flask server in a new thread
    threading.Thread(target=app.run, kwargs={"use_reloader": False}).start()



