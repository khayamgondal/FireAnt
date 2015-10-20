#!/usr/bin/python
import MySQLdb,time,os,sys,ConfigParser,json,copy,random
#----------------------------------
# Fireant working environment setup
#----------------------------------
config = ConfigParser.ConfigParser()
home_directory = os.path.expanduser('~')
config.read(home_directory + '/.fireantenv')
folder_path = config.get('directory','path')
sys.path.insert(0, folder_path+'Common')
from ReadConfig import ReadConfig

DEBUG_MODULE = '[AnalyticsEngine]'
DEBUG_SCRIPT = '[AnalyticsEngine]' 
DEBUG_HEADER = DEBUG_MODULE + DEBUG_SCRIPT

#------------------------
# Read configuration file
#------------------------
config = ReadConfig()
request_timeout_seconds = int(config.get('AnalyticsEngine', 'request_timeout_seconds'))
neighbor_number = int(config.get('Neighbor','number'))

#-------------------------------------
# Function: Check if the record exists
#-------------------------------------
def isExistingRecord(uuid):
    print DEBUG_HEADER, "Request uuid: " + uuid
    print DEBUG_HEADER, "Query the request_status table..."
    db = MySQLdb.connect('localhost','fireant','fireant','fireant')
    cursor = db.cursor()
    sql = "SELECT * FROM request_status \
            WHERE uuid = '%s'" % (uuid)

    cursor.execute(sql)
    results = cursor.fetchall()
    print DEBUG_HEADER, "Query results: ", results
    if results == ():
        return_value = 'no'
    else:
        return_value = 'yes'
    #print DEBUG_HEADER, return_value

    db.close()
    return return_value

#------------------------------------------
# Function: Check if the request is timeout
#------------------------------------------
def isTimeout(uuid):
    print DEBUG_HEADER, "Request uuid: " + uuid
    print DEBUG_HEADER, "Check if the request is timeout or not..."
    db = MySQLdb.connect('localhost','fireant','fireant','fireant')
    cursor = db.cursor()
    sql = "SELECT UNIX_TIMESTAMP(last_update_time) FROM request_status \
            WHERE uuid = '%s'" % (uuid)
    cursor.execute(sql)
    results = cursor.fetchall()
    print DEBUG_HEADER, "Query results: ", results
    last_update_time_seconds = results[0][0]
    current_time_seconds = int(time.time())
    print DEBUG_HEADER, "Last update time:", last_update_time_seconds, "Current time:", current_time_seconds
    if current_time_seconds - last_update_time_seconds >= request_timeout_seconds:
        print DEBUG_HEADER, "The request is already timeout."
        return_value = 'yes'
    else:
        print DEBUG_HEADER, "The request is alive."
        return_value = 'no'
    db.close()
    return return_value
 
#-------------------------------------------
# Function: Check if the request was replied
#-------------------------------------------
def isReplied(uuid):
    print DEBUG_HEADER, "Request uuid: " + uuid
    print DEBUG_HEADER, "Check if the request was replied or not..."
    db = MySQLdb.connect('localhost','fireant','fireant','fireant')
    cursor = db.cursor()
    sql = "SELECT status FROM request_status \
            WHERE uuid = '%s'" % (uuid)
    cursor.execute(sql)
    results = cursor.fetchall()
    print DEBUG_HEADER, "Query results: ", results
    status = results[0][0]
    if status == 'replied':
        print DEBUG_HEADER, "The request was already replied."
        return_value = 'yes'
    elif status == 'pending':
        print DEBUG_HEADER, "The request is pending."
        return_value = 'no'
    db.close()
    return return_value

#--------------------------------------------------------------
# Function: Check if the in_direction is contained in the table
#--------------------------------------------------------------
def containInDirection(uuid, current_in_direction):
    print DEBUG_HEADER, "Request uuid: " + uuid
    print DEBUG_HEADER, "Check if the last hop IP is contained or not..."
    db = MySQLdb.connect('localhost','fireant','fireant','fireant')
    cursor = db.cursor()
    sql = "SELECT in_direction FROM request_status \
            WHERE uuid = '%s'" % (uuid)
    cursor.execute(sql)
    results = cursor.fetchall()
    print DEBUG_HEADER, "Query results: ", results
    in_direction_set = results[0][0].split(',')
    print DEBUG_HEADER, "In direction set: ", in_direction_set    
    if current_in_direction in in_direction_set:
        print DEBUG_HEADER, "The request was seen from the same direction before."
        return_value = 'yes'
    else:
        print DEBUG_HEADER, "The request is NOT seen from the same direction before."
        return_value = 'no'
    db.close()
    return return_value

   
#--------------------------
# Function: Insert a record
#--------------------------
def InsertRecord(uuid, status, forwarded_direction, in_direction, message_content):
    #print DEBUG_HEADER, uuid, status, forwarded_direction, in_direction, content
    print DEBUG_HEADER, "Inserting a record into the request_status table..."
    db = MySQLdb.connect('localhost','fireant','fireant','fireant')
    in_direction_set = []
    in_direction_set.append(in_direction)
    forwarded_direction_set = []
    forwarded_direction_set.append(forwarded_direction)
    in_direction_set_string = ','.join(map(str,in_direction_set))
    forwarded_direction_set_string = ','.join(map(str,forwarded_direction_set))

    print DEBUG_HEADER, message_content
    request_content_json = json.loads(message_content)
    del request_content_json['last_hop_ip']
    request_content = json.dumps(request_content_json)

    cursor = db.cursor()
    sql = "INSERT INTO request_status(uuid, status, forwarded_direction, in_direction, request_content)\
            VALUES ('%s','%s','%s','%s','%s')" \
            % (uuid, status, forwarded_direction_set_string, in_direction_set_string, request_content)
    cursor.execute(sql)
    db.commit()
    print DEBUG_HEADER, "Record insertion success."
    db.close()
    return

#--------------------------
# Function: Delete a record
#--------------------------
def DeleteRecord(uuid):
    print DEBUG_HEADER, "Request uuid:", uuid
    print DEBUG_HEADER, "Deleting a record from the request_status table..."
    db = MySQLdb.connect('localhost','fireant','fireant','fireant')
    cursor = db.cursor()
    sql = "DELETE FROM request_status WHERE uuid = '%s'" % (uuid)
    cursor.execute(sql)
    db.commit()
    print DEBUG_HEADER, "Record deletion success."
    db.close()
    return

#------------------------------
# Function: Update in_direction
#------------------------------
def UpdateInDirection(uuid, in_direction):
    print DEBUG_HEADER, "Request uuid:", uuid
    print DEBUG_HEADER, "Updating the in_direction for the request..."
    db = MySQLdb.connect('localhost','fireant','fireant','fireant')
    cursor = db.cursor()
    in_direction_set = ReadInDirection(uuid)
    in_direction_set.append(in_direction)
    in_direction_set_string = ','.join(map(str,in_direction_set))
    sql = "UPDATE request_status SET in_direction = '%s' \
            WHERE uuid = '%s'" % (in_direction_set_string, uuid)
    cursor.execute(sql)
    db.commit()
    print DEBUG_HEADER, "Record in_direction update success."
    db.close()
    return

#------------------------
# Function: Update status
#------------------------
def UpdateStatus(uuid, new_status):
    print DEBUG_HEADER, "Request uuid:", uuid
    print DEBUG_HEADER, "Updating the status for the request..."
    db = MySQLdb.connect('localhost','fireant','fireant','fireant')
    cursor = db.cursor()
    sql = "UPDATE request_status SET status = '%s' \
            WHERE uuid = '%s'" % (new_status, uuid)
    cursor.execute(sql)
    db.commit()
    print DEBUG_HEADER, "Record status update success."
    db.close()
    return

#------------------------
# Function: Update status
#------------------------
def UpdateReplyContent(uuid, reply_content):
    print DEBUG_HEADER, "Request uuid:", uuid
    print DEBUG_HEADER, "Updating the reply_content for the request..."
    db = MySQLdb.connect('localhost','fireant','fireant','fireant')
    cursor = db.cursor()
    sql = "UPDATE request_status SET reply_content = '%s' \
            WHERE uuid = '%s'" % (reply_content, uuid)
    cursor.execute(sql)
    db.commit()
    print DEBUG_HEADER, "Record reply_content update success."
    db.close()
    return

#-------------------------------------
# Function: Update forwarded_direction
#-------------------------------------
def UpdateForwardedDirection(uuid, decision_forwarded_direction_set):
    print DEBUG_HEADER, "Request uuid: ", uuid
    print DEBUG_HEADER, "Updating the forwarded_direction for the request..."
    db = MySQLdb.connect('localhost','fireant','fireant','fireant')
    cursor = db.cursor()
    forwarded_direction_set = ReadForwardedDirection(uuid)
    if forwarded_direction_set is None:
        forwarded_direction_set = []
    for direction in decision_forwarded_direction_set:
        forwarded_direction_set.append(direction)
    forwarded_direction_set_string = ','.join(map(str,forwarded_direction_set))
    sql = "UPDATE request_status SET forwarded_direction = '%s' \
            WHERE uuid = '%s'" % (forwarded_direction_set_string, uuid)
    cursor.execute(sql)
    db.commit()
    print DEBUG_HEADER, "Record forwarded_direction update success."
    db.close()
    return

#----------------------------------------
# Function: Read all request uuid entries
#----------------------------------------
def ReadRequestUUID():
    print DEBUG_HEADER, "Reading all request uuid entries..."
    db = MySQLdb.connect('localhost','fireant','fireant','fireant')
    cursor = db.cursor()
    sql = "SELECT uuid FROM request_status"
    cursor.execute(sql)
    results = cursor.fetchall()
    if results == ():
        return None
    else:
        return results

#----------------------------
# Function: Read in_direction
#----------------------------
def ReadInDirection(uuid):
    print DEBUG_HEADER, "Request uuid:", uuid
    print DEBUG_HEADER, "Reading the in_direction for the request..."
    db = MySQLdb.connect('localhost','fireant','fireant','fireant')
    cursor = db.cursor()
    sql = "SELECT in_direction FROM request_status \
            WHERE uuid = '%s'" % (uuid)
    cursor.execute(sql)
    results = cursor.fetchall()
    if results[0][0] is None:
        db.close()
        return None
    else:
        in_direction_set = results[0][0].split(',')
        print DEBUG_HEADER, "Read in_direction success."
        db.close()
        return in_direction_set

#-----------------------------------
# Function: Read forwarded_direction
#-----------------------------------
def ReadForwardedDirection(uuid):
    print DEBUG_HEADER, "Request uuid:", uuid
    print DEBUG_HEADER, "Reading the forwarded_direction for the request..."
    db = MySQLdb.connect('localhost','fireant','fireant','fireant')
    cursor = db.cursor()
    sql = "SELECT forwarded_direction FROM request_status \
            WHERE uuid = '%s'" % (uuid)
    cursor.execute(sql)
    results = cursor.fetchall()
    #print DEBUG_HEADER, results
    if results[0][0] == 'None':
        return None
        db.close()
    else:
        forwarded_direction_set = results[0][0].split(',')
        print DEBUG_HEADER, "Read forwarded_direction success."
        db.close()
        return forwarded_direction_set

#-------------------------------------------
# Function: Read reply count for a neighbor
#-------------------------------------------
def ReadRepliesCount(ip):
    print DEBUG_HEADER, "Reading the replies count for '%s'..." % (ip)
    db = MySQLdb.connect('localhost','fireant','fireant','fireant')
    cursor = db.cursor()
    sql = "SELECT replies_count FROM weighted_forwarding \
            WHERE neighbor_ip_address = '%s'" % (ip)
    cursor.execute(sql)
    results = cursor.fetchall()
    print DEBUG_HEADER, "The results fetched are %s." % (results)
    if results[0][0] == 'None':
        return None
        db.close()
    else:
        replies_count = results[0][0]
        print DEBUG_HEADER, "Read replies_count success."
        db.close()
        return replies_count
        
    
#----------------------------
# Function: Read neighor list
#----------------------------
def ReadNeighborList():
    print DEBUG_HEADER, "Reading neighbor list..."
    neighbor_list = []
    for i in range(1,neighbor_number+1):
        neighbor_ip = config.get('Neighbor'+str(i),'ip')
        neighbor_list.append(neighbor_ip)
    return neighbor_list

#-------------------------------------------
# Function: Forwarding direction calculation
#-------------------------------------------
def ForwardDirectionCalculation(uuid):
    print DEBUG_HEADER, "Calculating the forwarded direction..."
    neighbor_list = ReadNeighborList()
    print DEBUG_HEADER, "Neighbor list: ", neighbor_list
    in_direction_set = ReadInDirection(uuid)
    print DEBUG_HEADER, "In direction: ", in_direction_set
    forwarded_direction_set = ReadForwardedDirection(uuid)
    print DEBUG_HEADER, "Forwarded direction: ", forwarded_direction_set

    decision_forwarded_direction = neighbor_list
    if in_direction_set is not None:
        decision_forwarded_direction = list( \
            set(neighbor_list).difference(set(in_direction_set)))
    if forwarded_direction_set is not None:
        decision_forwarded_direction = list( \
            set(decision_forwarded_direction).difference(set(forwarded_direction_set)))

    print DEBUG_HEADER, "The decision of forwarded direction: ", decision_forwarded_direction
    return decision_forwarded_direction

#--------------------------------------
# Function: Reply direction calculation
#--------------------------------------
def ReplyDirectionCalculation(uuid, message_content):
    print DEBUG_HEADER, "Calculating the reply direction..."
    message_content_json = json.loads(message_content)
    message_action = message_content_json['action']
    print DEBUG_HEADER, "The message action is %s. " % (message_action)
    if message_action == 'reply':
        in_direction_set = ReadInDirection(uuid)
        print DEBUG_HEADER, "In direction: ", in_direction_set
        if in_direction_set is not None:
            decision_forwarded_direction = in_direction_set
        else:
            print DEBUG_HEADER, "THERE IS SOMETHING WRONG WITH THE REQUEST RECORD."

    elif message_action == 'forward':
        in_direction_set = ReadInDirection(uuid)
        print DEBUG_HEADER, "In direction: ", in_direction_set
        if in_direction_set is not None:
            decision_forwarded_direction = in_direction_set
        else:
            neighbor_list = ReadNeighborList()
            last_hop = message_content_json['last_hop_ip']
            decision_forwarded_direction = list( \
                set(neighbor_list).differentce(set(last_hop)))

    print DEBUG_HEADER, "The decision of forwarded direction: ", decision_forwarded_direction
    return decision_forwarded_direction

#-------------------------------------------------
# Function: Select opportunistic unicast direction
#-------------------------------------------------
def SelectOpportunisticUnicastDirection(directions_ip_set):
    if directions_ip_set is None:
        print DEBUG_HEADER, "There is no directions to be forwarded."
        return None
    
    temp = {}
    for ip in directions_ip_set:
        temp[ip] = ReadRepliesCount(ip)
    print DEBUG_HEADER, "The temp dict is %s. " % (temp)
    ip_list = list(temp.keys())
    count_list = list(temp.values())
    #print DEBUG_HEADER, "The ip_list is %s. " % (ip_list)
    #print DEBUG_HEADER, "The count_list is %s." % (count_list)
    index_max_set = [i for i in range(len(count_list)) if count_list[i]==max(count_list)]
    #print DEBUG_HEADER, "The index_max_set %s" % (index_max_set)
    index_max = index_max_set[random.randint(1,len(index_max_set)) - 1]
    #print DEBUG_HEADER, "The selected index_max is %s" % (index_max)
    direction_max_count = []
    direction_max_count.append(ip_list[index_max])
    print DEBUG_HEADER, "The direction with the maximum replies count is %s." % (direction_max_count)
    return direction_max_count


#--------------------------------------------
# Function: Increase the replies count by one
#--------------------------------------------
def IncreaseRepliesCountByOne(ip):
    print DEBUG_HEADER, "Increasing the replies count by one..."
    db = MySQLdb.connect('localhost','fireant','fireant','fireant')
    cursor = db.cursor()
    sql = "UPDATE weighted_forwarding SET replies_count = replies_count + 1 \
            WHERE neighbor_ip_address = '%s'" % (ip)
    cursor.execute(sql)
    db.commit()
    print DEBUG_HEADER, "Replies count was increased by one successfully."
    db.close()
    return



#UpdateInDirection('e3f514a0-919a-4c96-8693-1070c97aec53','172.16.10.111')
#in_direction_set = ReadInDirection('e3f514a0-919a-4c96-8693-1070c97aec53')
#print DEBUG_HEADER, "in_direction:", in_direction_set

"""
forwarded_direction_set = ReadForwardedDirection('e3f514a0-919a-4c96-8693-1070c97aec53')
print DEBUG_HEADER, "forwarded_direction:", forwarded_direction_set

neighbor_list = ReadNeighborList()
print DEBUG_HEADER, "Neighbor list:", neighbor_list
decision = ForwardDirectionCalculation('e3f514a0-919a-4c96-8693-1070c97aec53')
UpdateForwardedDirection('e3f514a0-919a-4c96-8693-1070c97aec53',decision)
"""
