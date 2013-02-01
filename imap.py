import imaplib
import datetime
from email.parser import HeaderParser
from email.header import decode_header
import re

imap_server_address = 'imap.gmail.com'
imap_username = 'amre2005@gmail.com'
imap_password = 'mhjllmfoucbskddm'

regex_pattern = '.*HW2'

mail = imaplib.IMAP4_SSL(imap_server_address)
mail.login(imap_username, imap_password)
mail.list()
# Out: list of "folders" aka labels in gmail.
mail.select("inbox") # connect to inbox.


start_date = (datetime.date.today() - datetime.timedelta(1)).strftime("%d-%b-%Y")
end_date = datetime.date.today().strftime("%d-%b-%Y")
typ, email_ids = mail.search (None, '(SENTSINCE {} SENTBEFORE {})'.format(start_date, end_date))


#print "Message IDs for Today:"
#print msgnums

email_ids_string = str(email_ids).replace(" ", ",")
email_ids_string = email_ids_string.replace("['", "")
email_ids_string = email_ids_string.replace("']", "")

email_ids_list = email_ids[0].split(" ")
#print email_ids_list

msgs = mail.fetch(email_ids_string, '(BODY[HEADER.FIELDS (SUBJECT)])')


hedaer_parser = HeaderParser()
email_id_subject_dict = dict()
for i in range(0, len(msgs[1]), 2):
    value = hedaer_parser.parsestr(msgs[1][i][1])
#    print decode_header(value['Subject'])[0][0]
    email_id_subject_dict[email_ids_list[i/2]] = decode_header(value['Subject'])[0][0]

regex_compiled = re.compile(regex_pattern)
selected_email_ids_list = list()
for email_id in email_id_subject_dict.keys():
    if(regex_compiled.match(email_id_subject_dict[email_id])):
        selected_email_ids_list.append(email_id)
        print email_id_subject_dict[email_id] + " : Matched"
    else:
        print email_id_subject_dict[email_id] + " : No Match"
print selected_email_ids_list        
