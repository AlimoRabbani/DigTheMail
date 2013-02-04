DigTheMail
==========


License Information:
--------------------------------------

Copyright (C) 2013  Alimohammad Rabbani

DigTheMail is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

DigTheMail is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with iTunification.  If not, see <http://www.gnu.org/licenses/>.


About:
--------------------------------------
We started DigTheMail based on an observation of TAs behavior at the Department of Computer Engineering, Sharif University of Technology. At the department, instructors, TAs, and students can use online courseware systems. But non of them are reliable, easy-to-use systems. Therefore, many teaching assistants prefer to have students deliver their electronic assignments by email. They usually create a unique email address for the course and instruct students to attach their files to an email with a specific subject (e.g. CE44088-HW2-881184213). However, downloading and organizing those attachments is performed on an email-by-email basis and is not very easy.

DigTheMail helps teaching assistants download and orginize these assignments automatically. It uses IMAP technology to connect to a mail server that supports IMAP (e.g. gmail) and download the emails you want. This part is done using regular expressions.

**Engineering & Development:** Alimohammad Rabbani, Sadjad Fouladi

For information on how to use this software, continue reading.


Prerequistes:
--------------------------------------
* Python v2.7 or later.
* Any operating system.
* An email address with IMAP capability.


How to Use:
--------------------------------------
1. Download the files located in DigTheMail's GitHub directory.
2. Use command `python main.py` with the following options:
	* `--server-address my_imap_server.com`
	* `--username my_username@my_server.com`
	* `--password my_password`
	* `--subject-pattern my_subject_regex` (Example: CE44088-HW2-(\d{8}) for emails with subject pattern: CE44088-HW2-STID if STIDs are 8 letters exactly)
	* `--folder-pattern my_folder_regex` (For the above example \1 would create directories based on STID only)
	* `--folder-name my_root_folder_name` (Relative to ../DigTheMailDownloadDirectory/)
	* `--start-date start_date` (Start date to look for emails. Format: mm-dd-yyyy)
	* `--end-date end_date` (End date to look for emails. Format: mm-dd-yyyy)
	* `--use-ssl` (Use this option only if your mail server requires SSL to connect)
3. Your attachments will be downloaded to '../DigTheMailDownloadDirectory/RootFolder/JobStartTime/' if everything goes well.
4. Use `python main.py --help` if you need help.
5. Contact me at a.rabbani@me.com if you have further questions on how to use this software.
6. Report issues if you found any here in GitHub.


Release History:
--------------------------------------
* **Version 1.0:**
    * Initial Public Release.
