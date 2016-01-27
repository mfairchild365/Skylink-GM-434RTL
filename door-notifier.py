import os
import sys
import subprocess
import time
import smtplib
import signal
from email.mime.text import MIMEText
from config import Config

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

f = file(os.path.join(__location__, 'door-notifier.cfg'))
cfg = Config(f)

#We need to start rtl_433 in default mode, then kill it in order for things to calibrate correctly (very odd)
p = subprocess.Popen('exec rtl_433 -s250000 -A -f '+cfg.frequency, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#let it run for a little bit
target_kill = time.time() + 5;
while p.poll() is None:
	if time.time() > target_kill:
		break

#End the sub-process
p.kill()

#continue with normal application
closed_text = 'garage door is CLOSED'
open_text = 'garage door is OPEN'

smtp = smtplib.SMTP(cfg.smtp_host)
smtp.starttls()
smtp.login(cfg.smtp_user, cfg.smtp_pass)

cmd = 'rtl_433 2>&1 -s'+cfg.sample_rate+' -A -f '+cfg.frequency

print 'running command: ' + cmd

p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

last_message = 0

while p.poll() is None:
	out = p.stdout.readline()

	if cfg.closed_code in out and time.time() > last_message+5:
		print time.strftime('%c') + ': CLOSED'
		msg = MIMEText(closed_text);
		msg['Subject'] = closed_text
		msg['From'] = cfg.email_from
		msg['To'] = cfg.email_to
		smtp.sendmail(cfg.email_from, [cfg.email_to], msg.as_string())

		last_message = time.time()
	elif cfg.open_code in out and time.time() > last_message+5:
		print time.strftime('%c') + ': OPEN'
                msg = MIMEText(open_text);
                msg['Subject'] = open_text 
                msg['From'] = cfg.email_from
                msg['To'] = cfg.email_to
                smtp.sendmail(cfg.email_from, [cfg.email_to], msg.as_string())

		last_message = time.time()

print 'finished'



