import imaplib, email
import re, os, time, datetime, sys
import threading, logging
import constants
from utilities import ActivePool
from utilities import FileOperations
from optparse import OptionParser
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
            for part in whole_mail.walk():
                if part.is_multipart():
                    continue            
                file_name = part.get_filename()
                if file_name:
                    logging.info("Found attachment %s in email with ID: %s" % (file_name, email_id))
                    file_path = os.path.join("%s%s" % (constants.ATTACHMENT_DOWNLOAD_DIRECTORY, email_id), file_name)
                    FileOperations.create_directory("%s%s" % (constants.ATTACHMENT_DOWNLOAD_DIRECTORY, email_id))
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
    parser = OptionParser()
    parser.add_option("-s", "--server-address", dest="server_address", help="IMAP Server Address", metavar="SERVER", default="imap.gmail.com")
    parser.add_option("-u", "--user-name", dest="username", help="IMAP Username", metavar="UNAME")
    parser.add_option("-p", "--password", dest="password", help="IMAP Server Address", metavar="PASS")
    parser.add_option("-R", "--regex-pattern", dest="regex_pattern", help="RegEx pattern to look for in email subjects", metavar="REGEX")
    parser.add_option("-F", "--folder-name", dest="folder_name", help="Folder name for the current user", metavar="FOLDER")
    parser.add_option("-S", "--start-date", dest="start_date", help="Start date to look for emails", metavar="DATE")
    parser.add_option("-E", "--end-date", dest="end_date", help="Finish date to look for emails", metavar="DATE")
    parser.add_option("-P", "--use-ssl", action="store_true", dest="use_ssl", default=False, help="Force SSL Connection")
    
    (options, args) = parser.parse_args()
    global imap_server_address, imap_username, imap_password, folder_name, use_ssl
    imap_server_address = options.server_address
    imap_username = options.username
    imap_password = options.password
    regex_pattern = options.regex_pattern
    folder_name = options.folder_name
    use_ssl = options.use_ssl
    try:
        start_date = datetime.datetime.strptime(options.start_date, '%d-%m-%Y')
        end_date = datetime.datetime.strptime(options.end_date, '%d-%m-%Y')
    except Exception as e:
        logging.error(str(e))
        sys.exit(1)
        
    if(imap_username and imap_password and regex_pattern and folder_name and start_date and end_date):
        fetch_subjects(start_date, end_date, regex_pattern)
    else:
        logging.error("Bad input arguments!")
        sys.exit(1)

    
    
    
def fetch_subjects(start_date, end_date, regex_pattern):
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
    
    regex_compiled = re.compile(regex_pattern)
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
        

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-2s) %(message)s',)
if __name__ == "__main__":
    main()