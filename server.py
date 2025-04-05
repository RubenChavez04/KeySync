import paramiko

hostname = "" #pi IP
username = "rubchave" #pi username
password = "7477" #pi password
port = 22

ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh_client.connect(hostname=hostname, port=port, username=username, password=password)

