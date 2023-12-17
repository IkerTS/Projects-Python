Script in Catalan that automates the creation of user accounts and secure passwords, organizes this data in CSV files, 
also generates PowerShell commands for the creation of users in an Active Directory environment, all based on a CSV file of students.
It also generates a csv for each group to name all its members and another one for the emails of all the students.
- usuaris.csv: Contains the usernames and passwords generated for each user account.
- (group).csv: Contains detailed information of the students grouped by their respective group, including first name, last name, usernames and passwords.
- createComptes.ps1: This is a PowerShell script file containing commands for creating users in Active Directory. Each command is built with student data to generate users in the Active Directory environment.
- correus.csv: Contains information for creating emails, including email addresses, first names, last names, passwords, and organizational unit (OU) paths.
- correugrups.csv: CSV file that describes users' membership in email groups, with information about the group address, the member's email address, and their role in the group.
