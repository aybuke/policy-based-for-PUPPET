#!/usr/local/bin/python

import OpenSSL
import sys
import smtplib
import subprocess
import  boto.ec2

csr = ""
for line in sys.stdin:
    csr += line

certdomain = sys.argv[1]

p = subprocess.Popen(['openssl', 'x509', '-noout', '-text'], stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

p.stdin.write(csr)
output = p.communicate()[0]
p.stdin.close()

#common_name value found.

array1 = []
try:
  for line in output.splitlines():
    if "Subject:" in line:
      array1.append(line)
 
  fixed = array1[0].split('CN=')
  common_name = fixed[1]
except Exception, VariableError:
  print "common_name value could not find."

#instance_id value found.

array2 = []
try:
  for line in output.splitlines():
    array2.append(line.strip())
  number =  array2.index('1.3.6.1.4.1.34380.1.1.2:')
  need = array2[number+1]
  need = need.split('@')
  avalibilty_zone = need[1]
  instance_id = need[0] 
except Exception, VariableError:
  print "instance_id value could not find."

#connect with boto
try:
  regions = boto.ec2.regions ()
  eu = regions[3]
  eu_conn = eu.connect()

except Exception, ConnectionError:
  print "Unable to connect."

#controls

if common_name and common_name == certdomain and eu_conn.get_all_instances(filters={'instance-id' : instance_id}):
  sys.exit(1)

#write log and send e-mail.
else:
  end = "common_name: %s " %common_name + "instance_id: %s " %instance_id + "certdomain: %s " %certdomain + "tried to connect to the machine.\n"
  try:

    with open("/var/log/csr.log", 'a') as logfile:
      logfile.write(end)
    server = smtplib.SMTP( "smtp.gmail.com", 587 )
    server.starttls()
    server.login( 'aybuke.147@gmail.com', '****************' )
    server.sendmail( 'master', '05543432144@mms.att.net', end)

  except Exception, SendmailError:
    print "Failed to send mail."
