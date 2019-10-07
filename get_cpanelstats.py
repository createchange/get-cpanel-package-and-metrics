import subprocess
from pprint import pprint
import json
import csv

def package_info():
    '''
    returns a list of accounts formatted as dicts, each dict consisting of:
    k = account name
    v = current package
    '''
    accounts = []

    subprocess.call('cat /etc/userplans > pkgs.txt', shell=True)
    with open('pkgs.txt','r') as f:
        pkg_info = f.read()
        pkg_info = pkg_info.split('\n')

    for entry in pkg_info[1:-1]:
        x = entry.split(": ")
        accounts.append(x[0])

    subprocess.call('rm pkgs.txt', shell=True)
    return accounts

def get_stats(accounts):
    '''
    Main function that calls all other functions which return desired information. 
    This returns a list of dicts, each dict consisting of: 
    key = account name
    values = account stats
    '''
    account_stats = {}
    for acct in accounts:
	account_stats[acct] = [get_package(acct), get_diskusage(acct), get_bandwidth(acct), get_ftpaccounts(acct), get_emailaccts(acct), get_emaillists(acct), get_databases(acct), get_subdomains(acct), get_parkeddomains(acct), get_addondomains(acct)]
    return account_stats
	
def get_package(account):
    infinityimg = "infinityimg=%2Fhome%2Fexample%2Finfinity.png"
    r = subprocess.check_output("uapi --user=%s StatsBar get_stats display='hostingpackage' warnings=0 warninglevel=high warnout=0 %s infinitylang='infinity' rowcounter=even --output=json" % (account, infinityimg), shell=True)
    data = json.loads(r)
    package = data['result']['data'][0]['value']
    return(package)

def get_diskusage(account):
    infinityimg = "infinityimg=%2Fhome%2Fexample%2Finfinity.png"
    r = subprocess.check_output("uapi --user=%s StatsBar get_stats display='diskusage' warnings=0 warninglevel=high warnout=0 %s infinitylang='infinity' rowcounter=even --output=json" % (account, infinityimg), shell=True)
    data = json.loads(r)
    disk_usage = data['result']['data'][0]['_count']
    return(disk_usage)

def get_emailaccts(account):
    r = subprocess.check_output("uapi --user=%s Email list_pops --output=json" % account, shell=True)
    data = json.loads(r)
    email_accts = len(data['result']['data'])
    return email_accts

def get_emaillists(account):
    r = subprocess.check_output("uapi --user=%s Email list_lists --output=json" % account, shell=True)
    data = json.loads(r)
    return len(data['result']['data'])

def get_databases(account):
    r = subprocess.check_output("cpapi2 --user=%s MysqlFE listdbs --output=json" % account, shell=True)
    data = json.loads(r)
    return len(data['cpanelresult']['data'])

def get_ftpaccounts(account):
    r = subprocess.check_output("uapi --user=%s Ftp list_ftp skip_acct_types='main|logaccess' --output=json" % account, shell=True)
    data = json.loads(r)
    return len(data['result']['data'])

def get_subdomains(account):
    infinityimg = "infinityimg=%2Fhome%2Fexample%2Finfinity.png"
    r = subprocess.check_output("uapi --user=%s StatsBar get_stats display='subdomains' warnings=0 warninglevel=high warnout=0 %s infinitylang='infinity' rowcounter=even --output=json" % (account, infinityimg), shell=True)
    data = json.loads(r)
#    pprint(data)
    try:
        subdomain_count = data['result']['data'][0]['_count']
        return subdomain_count
    except IndexError:
        return 0

def get_parkeddomains(account):
    r = subprocess.check_output("uapi --user=%s DomainInfo list_domains --output=json" % account, shell=True)
    data = json.loads(r)
    parkeddomain_count = len(data['result']['data']['parked_domains'])
    return parkeddomain_count

def get_addondomains(account):
    r = subprocess.check_output("uapi --user=%s DomainInfo list_domains --output=json" % account, shell=True)
    data = json.loads(r)
    addondomain_count = len(data['result']['data']['addon_domains'])
    return addondomain_count

def get_bandwidth(account):
    query = "grouping=year_month interval=daily protocols=http%7Cimap%7Csmtp timezone=America%2FChicago"
    r = subprocess.check_output("uapi --user=%s Bandwidth query %s --output=json" % (account, query), shell=True)
    data = json.loads(r)
    bw_data = data['result']['data'].values()
    bw_total = int(0)
    for data_point in bw_data:
        bw_total = bw_total + data_point
    try:
        bw_avg = bw_total / len(bw_data)
	# the divison below converts bytes to megabytes (kinda)
	return (int(bw_avg) / 1024) / 1024
    except ZeroDivisionError:
	    return 0


print("Getting account names...")
accounts = package_info()
print("Getting account stats...")
account_stats = get_stats(accounts)

# Output results in a csv file
print("Writing information to CSV file...")
with open("cpanel_stats.csv", 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["account", "package", "disk_use", "bandwidth_avg", "ftp_accts", "email_accts", "email_lists", "dbs", "subdomains", "parked_domains", "addon_domains"])
    for k,v in account_stats.items():
        writer.writerow([k, v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7], v[8], v[9]])
print("Done!")