# snapgroup
Tool for managing group snapshot on infinibox

## Prerequisites
the script uses python 3 

## Authentication
Please make sure to create credential file for the relevant ibox you want the script to manage.
the file content should be as follows: 
```
ibox ibox_name
user ibox_username
password ibox_password
snaps_num amount_of_snaps_to_keep
```
password value should be encrypted using base64

## Usage
```
usage: snapgroup_v7.py [-h] -o {create,query,delete,restore} [-n NAME] -c
                       CREDFILE [-v VOLUMES [VOLUMES ...]]

Script for managing snap groups.

optional arguments:
  -h, --help            show this help message and exit
  -o {create,query,delete,restore}, --option {create,query,delete,restore}
                        Choose the needed option
  -n NAME, --name NAME  Name of the snap group
  -c CREDFILE, --credfile CREDFILE
                        Credentials file name
  -v VOLUMES [VOLUMES ...], --volumes VOLUMES [VOLUMES ...]
                        Specify volume names with space
```

## Example
the following creates a group snapshot named test4 for volumes vol1 vol2 vol3: \
`./snapgroup_v2.py -c .testing.sec --o create -n test4 -v vol1 vol2 vol3`

the following queries for all snap groups named test4: \
`./snapgroup_v2.py --option query -n test4 -c .testing.sec`

