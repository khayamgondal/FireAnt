#!/usr/bin/python
import subprocess,sys,MySQLdb,ConfigParser,os

#----------------------------------
# Fireant working environment setup
#----------------------------------
config = ConfigParser.ConfigParser()
home_directory = os.path.expanduser('~')
config.read(home_directory + '/.fireantenv')
folder_path = config.get('directory','path')
sys.path.insert(0, folder_path+'/Common')
from ReadConfig import ReadConfig
from DeleteQueue import DeleteQueue

DEBUG_HEADER = '[FireantShutdown]'

# Read mysql db root password
DB_ROOT_PASSWORD = config.get('mysql','root_password')

#----------------
# Clean log files
#----------------
cmd = "ls %s -all | grep fireant.log > /dev/null 2>&1" % (folder_path+'Log/')
#print DEBUG_HEADER, cmd
output = subprocess.call(cmd,shell=True)
if output == 0:
    cmd = "rm -rf %s" % (folder_path+'Log/fireant.log')
    subprocess.call(cmd,shell=True)
print DEBUG_HEADER, "The log file was checked and cleaned. [x]"

#------------------
# Kill old programs
#------------------
cmd = "ps -aux | grep [M]essageListenDaemon.py"
child_process = subprocess.Popen([cmd],stdout=subprocess.PIPE,shell=True)
output = child_process.communicate()[0].split()
#print DEBUG_HEADER, output
if output != []:
    pid = output[1]
    #print DEBUG_HEADER, pid
    print DEBUG_HEADER, "Found existing MessageListenDaemon.py. Killing the process... [*]"
    cmd = "kill -9 " + pid
    subprocess.call(cmd,shell=True)
    print DEBUG_HEADER, "Running process was killed. [x]"

cmd = "ps -aux | grep [M]essageCheck.py"
child_process = subprocess.Popen([cmd],stdout=subprocess.PIPE,shell=True)
output = child_process.communicate()[0].split()
#print DEBUG_HEADER, output
if output != []:
    pid = output[1]
    #print DEBUG_HEADER, pid
    print DEBUG_HEADER, "Found existing MessageCheck.py. Killing the process... [*]"
    cmd = "kill -9 " + pid
    subprocess.call(cmd,shell=True)
    print DEBUG_HEADER, "Running process was killed. [x]"

cmd = "ps -aux | grep [R]esourceManagementHandler.py"
child_process = subprocess.Popen([cmd],stdout=subprocess.PIPE,shell=True)
output = child_process.communicate()[0].split()
#print DEBUG_HEADER, output
if output != []:
    pid = output[1]
    #print DEBUG_HEADER, pid
    print DEBUG_HEADER, "Found existing ResourceManagementHandler.py. Killing the process... [*]"
    cmd = "kill -9 " + pid
    subprocess.call(cmd,shell=True)
    print DEBUG_HEADER, "Running process was killed. [x]"

cmd = "ps -aux | grep [C]ommunicationHandler.py"
child_process = subprocess.Popen([cmd],stdout=subprocess.PIPE,shell=True)
output = child_process.communicate()[0].split()
#print DEBUG_HEADER, output
if output != []:
    pid = output[1]
    #print DEBUG_HEADER, pid
    print DEBUG_HEADER, "Found existing CommunicationHandler.py. Killing the process... [*]"
    cmd = "kill -9 " + pid
    subprocess.call(cmd,shell=True)
    print DEBUG_HEADER, "Running process was killed. [x]"

cmd = "ps -aux | grep [M]essageTimeoutMonitoring.py"
child_process = subprocess.Popen([cmd],stdout=subprocess.PIPE,shell=True)
output = child_process.communicate()[0].split()
#print DEBUG_HEADER, output
if output != []:
    pid = output[1]
    #print DEBUG_HEADER, pid
    print DEBUG_HEADER, "Found existing MessageTimeoutMonitoring.py. Killing the process... [*]"
    cmd = "kill -9 " + pid
    subprocess.call(cmd,shell=True)
    print DEBUG_HEADER, "Running process was killed. [x]"

#------------------
# Delete old queues
#------------------
config = ReadConfig()
message_cache_name = config.get('MessageManagement','message_cache_name')
DeleteQueue(message_cache_name)
print DEBUG_HEADER, "The queue %s was deleted. [x]" % (message_cache_name)

resource_management_queue_name = config.get('ResourceManagement','message_queue_name')
DeleteQueue(resource_management_queue_name)
print DEBUG_HEADER, "The queue %s was deleted. [x]" % (resource_management_queue_name)

communication_queue_name = config.get('Communication','message_queue_name')
DeleteQueue(communication_queue_name)
print DEBUG_HEADER, "The queue %s was deleted. [x]" % (communication_queue_name)
