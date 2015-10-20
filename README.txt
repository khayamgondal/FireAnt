[Environment]

The fireant environment config file should be configured first.
Create a new '.fireantenv' in your home directory. Refer to the example
in the file 'Config/.fireantenv'

== Working directory setup ==
A correct working directory should be set up first before running fireant.
The content should be like this:
e.g.,
    [directory]
    path = /home/dell/Documents/Fireant/
Make sure the value of the key 'path' be the fireant actual folder.
NOTE: Make sure include the '/' at the end of the path.

== MySQL DB credential setup ==
Fireant uses mysql db for maintaining request and forwarding tables.
Make sure the root password is correct:
e.g.,
    [mysql]
    root_username = root
    root_password = dellpassword
NOTE: You can find the root_password in the file '~/packstack-answers-XXXXXXXX-XXXXXX.txt'
under the key "CONFIG_MARIADB_PW"



[Requirements]

== RabbitMQ ==
NOTE: RabbitMQ should be installed by OpenStack. You can ignore if you already have OpenStack.

-- Installation on Ubuntu --
> Add rabbitmq APT repository to /etc/apt/sources.list
deb http://www.rabbitmq.com/debian/ testing main

> Add rabbitmq public key to the trusted key list
wget https://www.rabbitmq.com/rabbitmq-signing-key-public.asc
sudo apt-key add rabbitmq-signing-key-public.asc

> Install rabbitmq server
sudo apt-get update
sudo apt-get install rabbitmq-server

> Delete downloaded temporary key file
rm ./rabbitmq-signing-key-public.asc


== RabbitMQ Python Libraries ==
NOTE: This dependency should be installed.

-- Installation on Ubuntu --

> Install dependencies
sudo apt-get install python-pip git-core

> Install pika
sudo pip install pika==0.10.0

-- Installation on Fedora --

> Install dependencies
sudo yum install python-pip git-core

> install pika
sudo pip install pika==0.10.0


== MySQL ==
NOTE: mysql should be installed by OpenStack. You can ignore if you already have OpenStack.

-- Installation on Ubuntu --
> Install mysql server
sudo apt-get install mysql-server

> Install mysql python libraries
sudo apt-get install python-mysqldb

-- Installation on Fedora --
> Install mysql server
sudo yum install mysql-server

> Install mysql python libraries
sudo yum install MySQL-python


[Fireant Config]
In the file Config/FireantNode.conf, change the values accordingly.
> [local][ip]
> [Neighbor][number]
> [NeighborX][ip]
