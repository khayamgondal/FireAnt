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

DEBUG_HEADER = '[FireantRun]'

# Read mysql db root password
DB_ROOT_PASSWORD = config.get('mysql','root_password')

#---------------------
# Check the fireant DB
#---------------------
print DEBUG_HEADER, "Check if 'fireant' DB already exists...[*]"
cmd = "mysql -u root --password="+DB_ROOT_PASSWORD+" -e 'USE fireant' 2> /dev/null"
output = subprocess.call(cmd,shell=True)
if output == 0:
    print DEBUG_HEADER, "The 'fireant' DB already exists. Good to go. [x]"
elif output == 1:
    print DEBUG_HEADER, "The 'fireant' DB does not exist. Creating one... [*]"
    cmd = "mysqladmin -u root --password="+DB_ROOT_PASSWORD+" create fireant"
    output = subprocess.call(cmd,shell=True)
    if output == 0:
        print DEBUG_HEADER, "The 'fireant' DB was created successfully. [x]"
    else:
        print DEBUG_HEADER, "Failed to create the 'fireant' DB. [ERROR]"
        sys.exit()

#--------------------------
# Check the fireant DB user
#--------------------------
print DEBUG_HEADER, "Check if 'fireant' user already exists...[*]"
cmd = "mysql -u root --password="+DB_ROOT_PASSWORD+" \
        -e 'use fireant; select User from mysql.user'| grep fireant > /dev/null 2>&1"
output = subprocess.call(cmd,shell=True)
if output == 0:
    print DEBUG_HEADER, "There exists the user 'fireant'. Good to go. [x]"
elif output == 1:
    print DEBUG_HEADER, "No user 'fireant' exists. Create the user... [*]"
    cmd = "mysql -u root --password="+DB_ROOT_PASSWORD+" -e \"GRANT ALL PRIVILEGES \
            ON fireant.* TO 'fireant'@'localhost' IDENTIFIED BY 'fireant'\"" 
    subprocess.call(cmd,shell=True)
    cmd = "mysql -u root --password="+DB_ROOT_PASSWORD+" \
            -e 'use fireant; select User from mysql.user'| grep fireant > /dev/null 2>&1"
    output = subprocess.call(cmd,shell=True)
    if output == 0:
        print DEBUG_HEADER, "The user 'fireant' was created successfully. [x]"
    else:
        print DEBUG_HEADER, "Failed to create the user 'fireant'. [ERROR]"

#----------------------------------------------------------
# Create request status table and weighted forwarding table
#----------------------------------------------------------
db = MySQLdb.connect("localhost","fireant","fireant","fireant")
cursor = db.cursor()

print DEBUG_HEADER, "Creating a new 'request_status' table... [*]"
cursor.execute("DROP TABLE IF EXISTS request_status")
sql = """CREATE TABLE request_status (
        uuid CHAR(36) NOT NULL PRIMARY KEY,
        status ENUM('pending','replied') NOT NULL,
        forwarded_direction BLOB,
        in_direction BLOB,
        last_update_time TIMESTAMP,
        request_content BLOB,
        reply_content BLOB
        );"""
output = cursor.execute(sql)
print DEBUG_HEADER, "The 'request_status' table was created successfully. [x]"

print DEBUG_HEADER, "Creating a new 'weighted_forwarding' table... [*]"
cursor.execute("DROP TABLE IF EXISTS weighted_forwarding")
sql = """CREATE TABLE weighted_forwarding (
        neighbor_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
        neighbor_ip_address VARCHAR(71) NOT NULL,
        replies_count INT NOT NULL DEFAULT 0,
        count_start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );"""
output = cursor.execute(sql)
print DEBUG_HEADER, "The 'weighted_forwarding' table was created successfully. [x]"

#---------------------------------------
# Initialize the weight_forwarding table
#---------------------------------------
config = ReadConfig()
neighbor_number = int(config.get('Neighbor','number'))
print DEBUG_HEADER, "There are " + str(neighbor_number) + " neighbors."

for i in range(1,neighbor_number+1):
    neighbor_ip = config.get('Neighbor'+str(i),'ip')
    print DEBUG_HEADER, "Neighbor " + str(i) + ": " + neighbor_ip
    print DEBUG_HEADER, "Inserting a record to 'weighted_forwarding' table... [*]"

    sql = "INSERT INTO weighted_forwarding\
            (neighbor_ip_address) VALUES ('%s')" % (neighbor_ip)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    print DEBUG_HEADER, "Insertion success. [x]"

db.close()

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
message_cache_name = config.get('MessageManagement','message_cache_name')
DeleteQueue(message_cache_name)
print DEBUG_HEADER, "The queue %s was deleted. [x]" % (message_cache_name)

resource_management_queue_name = config.get('ResourceManagement','message_queue_name')
DeleteQueue(resource_management_queue_name)
print DEBUG_HEADER, "The queue %s was deleted. [x]" % (resource_management_queue_name)

communication_queue_name = config.get('Communication','message_queue_name')
DeleteQueue(communication_queue_name)
print DEBUG_HEADER, "The queue %s was deleted. [x]" % (communication_queue_name)

#---------------------------
# Run fireant components
#---------------------------
print DEBUG_HEADER, "Starting MessageListenDaemon... [*]"
file_name = folder_path + "MessageManagement/MessageListenDaemon.py"
subprocess.Popen(['python',file_name])
print DEBUG_HEADER, "MessageListenDaemon started. [x]"

print DEBUG_HEADER, "Starting MessageCheck... [*]"
file_name = folder_path + "MessageManagement/MessageCheck.py"
subprocess.Popen(['python',file_name])
print DEBUG_HEADER, "MessageCheck started. [x]"

print DEBUG_HEADER, "Starting MessageTimeoutMonitoring... [*]"
file_name = folder_path + "MessageManagement/MessageTimeoutMonitoring.py"
subprocess.Popen(['python',file_name])
print DEBUG_HEADER, "MessageTimeoutMonitoring started. [x]"

print DEBUG_HEADER, "Starting ResourceManagementHandler... [*]"
file_name = folder_path + "ResourceManagement/ResourceManagementHandler.py"
subprocess.Popen(['python',file_name])
print DEBUG_HEADER, "ResourceManagementHandler started. [x]"

print DEBUG_HEADER, "Starting CommunicationHandler... [*]"
file_name = folder_path + "Communication/CommunicationHandler.py"
subprocess.Popen(['python',file_name])
print DEBUG_HEADER, "CommunicationHandler started. [x]"
