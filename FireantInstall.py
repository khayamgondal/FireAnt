#!/usr/bin/python
import subprocess,sys,ConfigParser,os,glob

home_directory = os.path.expanduser('~')

DEBUG_HEADER = '[FireantInstall]'

# Install dependencies
print DEBUG_HEADER, "Installing dependencies..."
cmd = "sudo yum install python-pip git-core"
output = subprocess.call(cmd,shell=True)
if output == 0:
    print DEBUG_HEADER, "Dependencies installation done."
elif output == 1:
    print DEBUG_HEADER, "Dependencies installation failed."

# Install pika
print DEBUG_HEADER, "Installing pika (rabbitmq python lib)..."
cmd = "sudo pip install pika==0.10.0"
output = subprocess.call(cmd,shell=True)
if output == 0:
    print DEBUG_HEADER, "Pika installation done."
elif output == 1:
    print DBEUG_HEADER, "Pika installation failed."

# Install mysql lib
print DEBUG_HEADER, "Installing MySQL-python..."
cmd = "sudo yum install MySQL-python"
output = subprocess.call(cmd,shell=True)
if output == 0:
    print DEBUG_HEADER, "MySQL-pyhthon installation done."
elif output == 1:
    print dEBUG_HEADER, "MySQL-python installation failed."

# Setup the environment config file
print DEBUG_HEADER, "Configuring the fireant working directory..."
cmd = "pwd"
output, error = subprocess.Popen([cmd], stdout=subprocess.PIPE).communicate()
fireant_path = output.splitlines()[0] + '/'
cmd = "echo '[directory]' > %s/.fireantenv" % (home_directory)
output = subprocess.call(cmd,shell=True)
cmd = "echo 'path = %s' >> %s/.fireantenv" % (fireant_path, home_directory)
output = subprocess.call(cmd,shell=True)
cmd = "echo '' >> %s/.fireantenv" % (home_directory)
output = subprocess.call(cmd,shell=True)
print DEBUG_HEADER, "The fireant working directory was configured."

# Setup the mysql credentials
print DEBUG_HEADER, "Configuring the mysql credential..."
cmd = "echo '[mysql]' >> %s/.fireantenv" % (home_directory)
output = subprocess.call(cmd,shell=True)
cmd = "echo 'root_username = root' >> %s/.fireantenv" % (home_directory)
output = subprocess.call(cmd,shell=True)
cmd = "%s/packstack*.txt" % (home_directory)
packstack_answers_file = glob.glob(cmd)[0]
#print packstack_answers_file
config = ConfigParser.ConfigParser()
config.read(packstack_answers_file)
root_password = config.get('general','CONFIG_MARIADB_PW')
cmd = "echo 'root_password = %s' >> %s/.fireantenv" % (root_password, home_directory)
output = subprocess.call(cmd,shell=True)
