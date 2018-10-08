#!/usr/bin/env python3

import json
import requests
from requests.auth import HTTPBasicAuth
import urllib3
import argparse
import os
import base64
from time import strftime
import operator
import itertools
from operator import itemgetter
urllib3.disable_warnings()


headers = {'content-type': "application/json"}


def args_from_cfgfile(file):
    with open('{}/{}'.format(scriptpath, file)) as cfg:
        conf_file = dict(line for line in (l.split() for l in cfg) if line)
    return conf_file


#returns id of a volume
def get_vol_id(vol):
    return r.get('{}volumes?name={}'.format(url, vol))


def create_volist(vlist):
    vol_list=[]
    for volume in vlist:
        v=get_vol_id(volume)
        if v.json()['result']:
             vol_list.append(v.json()['result'][0]['id'])
        else:
            print('{} not found, skipping...'.format(volume))
    return vol_list


def create_snapgroup(vol_list):
    sdata={
        "entities": [
            ], 
            "snap_suffix": '_SG_'+args.name[0]+'_'+strftime("%Y-%m-%d-%H%M%S"), 
            }
    for vol in vol_list:
        sdata['entities'].append({'id':vol})
    outp=r.post('{}volumes/group_snapshot'.format(url), json=sdata)
    if outp.status_code == 200:
        print("Snap group created successfully")
    else:
        print('something went wrong: {}'.format(outp.json()['error']['message']))


def get_snapgroup(sgname):
    snapsurl='{}volumes?type=SNAPSHOT&page_size=1000&name=like:_SG_{}'.format(url, sgname)
    snaps_list=r.get(url=snapsurl)
    sg_list=[]
    snaps = []
    for page in range(1, snaps_list.json()['metadata']['pages_total']+1):
        snapslist=r.get(url='{}&page={}'.format(snapsurl, page))
        for s in snapslist.json()['result']:
            snaps.append(s)
    for key, items in itertools.groupby(snaps, operator.itemgetter('created_at')):
            sg_list.append(list(items))
    snapnames=[[igroup['name'] for igroup in group] for group in sg_list]
    for i,x in enumerate(snapnames):
            print(i,"-", " ".join(map(str, x)))
    return snapnames


def del_snapgroup(sgname):
    del_snap_list=get_snapgroup(sgname)
    if del_snap_list:
        for snap in del_snap_list[0]:
            snapsurl=url+'volumes?type=SNAPSHOT&name=eq:{}'.format(snap)
            snap=r.get(url=snapsurl)
            if snap.status_code == 200:
                outp=r.delete(url='{}volumes/{}'.format(url, snap.json()['result'][0]['id']))
                print((outp.json()['error']['message']))
                choice=user_input()
                if choice == 'y':
                    r.delete(url='{}volumes/{}?approved=true'.format(url, snap.json()['result'][0]['id']))
                else:
                    break
            else:
                print("snapshot not found")
        else:
            print("finished")
    else:
        print("snap group not found")
        

def restore_snapgroup(sgname):
    rstr_snap_list=get_snapgroup(sgname)
    if rstr_snap_list:
        for snap in rstr_snap_list[0]:
            snapsurl='{}volumes?type=SNAPSHOT&name=eq:{}'.format(url, snap)
            snap=r.get(url=snapsurl)
            if snap.status_code == 200:
                data = {"source_id": snap.json()['result'][0]['id'] }
                outp=r.post(url='{}volumes/{}/restore'.format(url, snap.json()['result'][0]['parent_id']), json=data)
                print((outp.json()['error']['message']))
                choice=user_input()
                if choice == 'y':
                    outp=r.post(url='{}volumes/{}/restore?approved=true'.format(url, snap.json()['result'][0]['parent_id']), json=data)
                else:
                    break
            else:
                print("snapshot not found")
        else:
            print("finished")
    else:
        print("snap group not found")


def user_input():
    user_input = str(input("Press y to approve "))
    return user_input


def get_args():
    """
    Supports the command-line arguments listed below.
    """
    parser = argparse.ArgumentParser(description="Script for managing snap groups.")
    parser.add_argument('-o', '--option', choices=['create', 'query', 'delete', 'restore'], required=True, help='Choose the needed option')
    parser.add_argument('-n', '--name', nargs=1, required=False, help='Name of the snap group')
    parser.add_argument('-c', '--credfile', nargs=1, required=True, help='Credentials file name')
    parser.add_argument('-v', '--volumes', nargs='+', required=False, help='Specify volume names with space')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = get_args()
    if args.credfile:
        scriptpath = os.path.dirname(os.path.abspath(__file__))
        if os.path.isfile('{}/{}'.format(scriptpath, args.credfile[0])):
            cfgargs = args_from_cfgfile(args.credfile[0])
            ibox1=cfgargs['ibox']
            user=cfgargs['user']
            enc_pw=cfgargs['password']
            pw = base64.b64decode(enc_pw).decode("utf-8", "ignore")
            creds1 = HTTPBasicAuth(user, pw)
            url = "http://{}/api/rest/".format(ibox1)
            r = requests.session()
            r.auth = creds1
            r.headers.update = headers
            if args.option == 'create':
                print("creating Snap Group")
                if args.volumes and args.name:
                    create_snapgroup(create_volist(args.volumes))
                else:
                    print('Please supply Snap Group name and space delimited volume list')
            elif args.option == 'query':
                print("querying")
                if args.name:
                    get_snapgroup(args.name[0])
                else:
                    print('Please supply Snap Group name')
            elif args.option == 'delete':
                print("deleting")
                if args.name:
                    del_snapgroup(args.name[0])
                else:
                    print('Please supply Snap Group name')
            elif args.option == 'restore':
                print("restoring")
                if args.name:
                    restore_snapgroup(args.name[0])
                else:
                    print('Please supply Snap Group name')
            else:
                print("please select a valid option")
        else:
            print('Credentials File Not Found')
    