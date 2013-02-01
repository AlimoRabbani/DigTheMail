import imaplib, email
import re, os, time, datetime, sys
import threading, logging
import constants
from utilities import ActivePool
from utilities import FileOperations
from optparse import OptionParser

def mail_downloader(s, pool, email_id):
    logging.debug('Waiting to join the pool')
    with s:
        name = threading.currentThread().getName()
        pool.makeActive(name)
        logging.info("Downloading email with ID: " + email_id)
        mail = imaplib.IMAP4_SSL(imap_server_address)
        mail.login(imap_username, imap_password)
        mail.list()
        mail.select("inbox") # connect to inbox.
        response, response_data = mail.fetch(email_id, '(RFC822)')
        logging.info("Downloaded email with ID: " + email_id)
        whole_mail = email.message_from_string(response_data[0][1])
        for part in whole_mail.walk():
            if part.is_multipart():
                continue            
            file_name = part.get_filename()
            if file_name:
                logging.info("Found attachment " + file_name + " in email with ID: " + email_id)
                file_path = os.path.join(constants.ATTACHMENT_DOWNLOAD_DIRECTORY + email_id, file_name)
                FileOperations.create_directory(constants.ATTACHMENT_DOWNLOAD_DIRECTORY + email_id)
                if not os.path.isfile(file_path) :
                    new_file = open(file_path, 'wb')
                    temp = part.get_payload(decode=True)
                    new_file.write(temp)
                    new_file.close()
                    logging.info("Saved attachment " + file_name + " as " + file_path)
                else:
                    logging.info("Attachment " + file_name + " already exists at " + file_path)
                cmd = "chmod -R 755 ."
                os.system(cmd)
                
        mail.store(email_id, '+FLAGS', '\Seen')
        mail.close()
        mail.logout()
        pool.makeInactive(name)

def main():
    parser = OptionParser()
    parser.add_option("-s", "--server-address", dest="server_address", help="IMAP Server Address", metavar="SERVER", default="imap.gmail.com")
    parser.add_option("-u", "--user-name", dest="username", help="IMAP Username", metavar="UNAME")
    parser.add_option("-p", "--password", dest="password", help="IMAP Server Address", metavar="PASS")
    parser.add_option("-R", "--regex-pattern", dest="regex_pattern", help="RegEx pattern to look for in email subjects", metavar="REGEX")
#    parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True, help="don't print status messages to stdout")
    
    (options, args) = parser.parse_args()
    global imap_server_address, imap_username, imap_password, regex_pattern
    imap_server_address = options.server_address
    imap_username = options.username
    imap_password = options.password
    regex_pattern = options.regex_pattern
    
    if(imap_username and imap_password and regex_pattern):
        fetch_subjects()
    else:
        logging.error("Bad input arguments!")
        sys.exit(1)

    
    
    
def fetch_subjects():
    mail = imaplib.IMAP4_SSL(imap_server_address)
    mail.login(imap_username, imap_password)
    mail.list()
    mail.select("inbox") # connect to inbox.
    
    start_date = (datetime.date.today() - datetime.timedelta(1)).strftime("%d-%b-%Y")
    end_date = datetime.date.today().strftime("%d-%b-%Y")
    #typ, email_ids = mail.search (None, '(SENTSINCE {} SENTBEFORE {} X-GM-RAW has:attachment)'.format(start_date, end_date))
    typ, email_ids = mail.search (None, '(SENTSINCE {} SENTBEFORE {})'.format(start_date, end_date))
        
    email_ids_string = str(email_ids).replace(" ", ",")
    email_ids_string = email_ids_string.replace("['", "")
    email_ids_string = email_ids_string.replace("']", "")
    email_ids_list = email_ids[0].split(" ")
    
    msgs = mail.fetch(email_ids_string, '(BODY.PEEK[HEADER.FIELDS (SUBJECT)])')
    mail.close()
    mail.logout()
    
    
    hedaer_parser = email.Parser.HeaderParser()
    email_id_subject_dict = dict()
    for i in range(0, len(msgs[1]), 2):
        value = hedaer_parser.parsestr(msgs[1][i][1])
        email_id_subject_dict[email_ids_list[i/2]] = email.Header.decode_header(value['Subject'])[0][0]
    
    regex_compiled = re.compile(regex_pattern)
    selected_email_ids_list = list()
    logging.info("Fetched " + str(len(email_id_subject_dict.keys())) + " subjects matching specified dates")     
    for email_id in email_id_subject_dict.keys():
        logging.debug(email_id + " -> " + email_id_subject_dict[email_id])
        if(regex_compiled.match(email_id_subject_dict[email_id])):
            selected_email_ids_list.append(email_id)
    logging.info("Matched " + str(len(selected_email_ids_list)) + " subjects to regex criteria")     
    
        
    download_threads_pool = ActivePool()
    my_semaphor = threading.Semaphore(constants.MAX_IMAP_CONNECTIONS)
    for email_id in selected_email_ids_list: 
        new_thread = threading.Thread(target=mail_downloader, name="DownloadThread " + email_id, args=(my_semaphor, download_threads_pool, email_id))
        new_thread.start()
        

logging.basicConfig(level=logging.INFO, format='(%(threadName)-2s) %(message)s',)
if __name__ == "__main__":
    main()