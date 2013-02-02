import imaplib, email
import re, os, time, datetime, sys
import threading, logging, argparse
import constants
from utilities import ActivePool
from utilities import FileOperations
from cgitb import enable

def mail_downloader(s, pool, email_id):
    logging.debug('Waiting to join the pool')
    with s:
        name = threading.currentThread().getName()
        pool.makeActive(name)
        logging.info("Downloading email with ID: %s" % email_id)
        try:
            mail = imaplib.IMAP4_SSL(imap_server_address) if use_ssl else imaplib.IMAP4(imap_server_address)    
            mail.login(imap_username, imap_password)
            mail.select("inbox")
        except Exception:
            logging.error("There was a problem connecting to IMAP server. Try again later!")
            sys.exit(1)
        try:
            response, response_data = mail.fetch(email_id, '(RFC822)')
        except Exception:
            logging.error("There was a problem downloading matched emails. Try again later!")
            sys.exit(1)
        logging.info("Downloaded email with ID: %s" % email_id)
        try:
            whole_mail = email.message_from_string(response_data[0][1])
            hedaer_parser = email.Parser.HeaderParser()
            value = hedaer_parser.parsestr(response_data[0][1])
            email_subject = email.Header.decode_header(value['Subject'])[0][0]
            inner_folder_name = re.sub(subject_pattern, folder_pattern, email_subject)
            logging.debug("Folder name to save cotents of this email is: %s" % (inner_folder_name))
            for part in whole_mail.walk():
                if part.is_multipart():
                    continue            
                file_name = part.get_filename()
                if file_name:
                    logging.info("Found attachment %s in email with ID: %s" % (file_name, email_id))
                    folder_path = os.path.join(constants.ATTACHMENT_DOWNLOAD_DIRECTORY, folder_name, current_time_str, inner_folder_name)
                    file_path = os.path.join(folder_path, file_name)
                    FileOperations.create_directory(folder_path)
                    if not os.path.isfile(file_path):
                        temp = part.get_payload(decode=True)
                        with open(file_path, 'wb') as new_file:
                            new_file.write(temp)
                        logging.info("Saved attachment %s as %s" % (file_name, file_path))
                    else:
                        logging.info("Attachment %s already exists at %s" % (file_name, file_path))
                    cmd = "chmod -R 755 ."
                    os.system(cmd)
        except Exception:
            logging.error("There was a problem processing an email attachment. Contact developer!")
            sys.exit(1)
        try:
            mail.store(email_id, '+FLAGS', '\Seen')
            mail.close()
            mail.logout()
        except Exception:
            logging.error("There was a problem marking an email as 'Read' and closing the connection. Try again later!")
            sys.exit(1)                        
        pool.makeInactive(name)

def main():
    parser = argparse.ArgumentParser(conflict_handler='resolve', version='1.0', description='Dig The Mail!')
    parser.add_argument("--server-address", "-s", action="store", dest="server_address", help="IMAP Server Address", metavar="host_address", default="imap.gmail.com")
    parser.add_argument("--username", "-u", action="store", dest="username", help="IMAP Username", metavar="username")
    parser.add_argument("--password", "-p", action="store", dest="password", help="IMAP Server Address", metavar="password")
    parser.add_argument("--subject-pattern", "-R", action="store", dest="subject_pattern", help="RegEx pattern to look for in email subjects", metavar="subject_pattern")
    parser.add_argument("--folder-pattern", "-X", action="store", dest="folder_pattern", help="RegEx pattern to match folders with subjects", metavar="folder_pattern")
    parser.add_argument("--folder-name", "-F", action="store", dest="folder_name", help="Folder name for the current user", metavar="main_folder")
    parser.add_argument("--start-date", "-S", action="store", dest="start_date", help="Start date to look for emails", metavar="start_date")
    parser.add_argument("--end-date", "-E", action="store", dest="end_date", help="Finish date to look for emails", metavar="end_date")
    parser.add_argument("--use-ssl", "-P", action="store_true", dest="use_ssl", default=False, help="Force SSL Connection")
    
    global imap_server_address, imap_username, imap_password, folder_name, use_ssl, current_time_str, subject_pattern, folder_pattern
    
    current_time_str = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d_%H%M%S')
    logging.info("Job started on %s" % (current_time_str))
    
    args = parser.parse_args()
    imap_server_address = args.server_address
    imap_username = args.username
    imap_password = args.password
    subject_pattern = args.subject_pattern
    folder_pattern = args.folder_pattern
    folder_name = args.folder_name
    use_ssl = args.use_ssl
    try:
        start_date = datetime.datetime.strptime(args.start_date, '%d-%m-%Y')
        end_date = datetime.datetime.strptime(args.end_date, '%d-%m-%Y')
    except Exception as e:
        logging.error("Bad date arguments!")
        sys.exit(1)
        
    if(imap_username and imap_password and subject_pattern and folder_pattern and folder_name and start_date and end_date):
        fetch_subjects(start_date, end_date)
    else:
        logging.error("Bad input arguments!")
        sys.exit(1)

    
    
    
def fetch_subjects(start_date, end_date):
    try:
        mail = imaplib.IMAP4_SSL(imap_server_address) if use_ssl else imaplib.IMAP4(imap_server_address)    
        mail.login(imap_username, imap_password)
#        mail.list()
        mail.select("inbox")
    except Exception:
        logging.error("There was a problem connectin to IMAP server. Try again later!")
        sys.exit(1)
    
    start_date_str = start_date.strftime("%d-%b-%Y")
    end_date_str = (end_date + datetime.timedelta(1)).strftime("%d-%b-%Y")
    logging.debug("Searching for mails sent between %s and %s" % (start_date_str, end_date_str))
    #typ, email_ids = mail.search (None, '(SENTSINCE {} SENTBEFORE {} X-GM-RAW has:attachment)'.format(start_date, end_date))
    try:
        typ, email_ids = mail.search (None, '(SENTSINCE {} SENTBEFORE {})'.format(start_date_str, end_date_str))
    except Exception:
        logging.error("There was a problem with search query. Contact developer!")
        sys.exit(1)

    
    if(not email_ids[0]):
        logging.error("No email found for the specified dates. Terminating application!")
        sys.exit(1)
    
    email_ids_string = str(email_ids).replace(" ", ",")
    email_ids_string = email_ids_string.replace("['", "")
    email_ids_string = email_ids_string.replace("']", "")
    email_ids_list = email_ids[0].split(" ")
    
    try:
        msgs = mail.fetch(email_ids_string, '(BODY.PEEK[HEADER.FIELDS (SUBJECT)])')
    except Exception:
        logging.error("There was a problem fetching email subjects. Try again later!")
        sys.exit(1)
    
    try:    
        mail.close()
        mail.logout()
    except Exception as e:
        logging.error(str(e))
        sys.exit(1)        
    
    
    hedaer_parser = email.Parser.HeaderParser()
    email_id_subject_dict = dict()
    for i in range(0, len(msgs[1]), 2):
        value = hedaer_parser.parsestr(msgs[1][i][1])
        email_id_subject_dict[email_ids_list[i/2]] = email.Header.decode_header(value['Subject'])[0][0]
    
    if(len(email_id_subject_dict.keys())==0):
        logging.error("There was a problem processing email subjects. Contact developer!")
        sys.exit(1)        
    try:
        regex_compiled = re.compile(subject_pattern)
    except Exception:
        logging.error("Your regex is not a regex!!! Try with another regex!")
        sys.exit(1)
    
    selected_email_ids_list = list()
    logging.info("Fetched " + str(len(email_id_subject_dict.keys())) + " subjects matching specified dates")     
    for email_id in email_id_subject_dict.keys():
        logging.debug(email_id + " -> " + email_id_subject_dict[email_id])
        if(regex_compiled.match(email_id_subject_dict[email_id])):
            selected_email_ids_list.append(email_id)
    logging.info("Matched " + str(len(selected_email_ids_list)) + " subjects to regex criteria")    
    
    if(str(len(selected_email_ids_list))==0):
        logging.error("Could not match any subjects to your regex. Try changing your regex!")
        sys.exit(1)
         
    
        
    download_threads_pool = ActivePool()
    my_semaphor = threading.Semaphore(constants.MAX_IMAP_CONNECTIONS)
    for email_id in selected_email_ids_list: 
        new_thread = threading.Thread(target=mail_downloader, name="DownloadThread " + email_id, args=(my_semaphor, download_threads_pool, email_id))
        new_thread.start()
        

logging.basicConfig(level=logging.INFO, format='(%(threadName)-2s) %(message)s',)
if __name__ == "__main__":
    main()