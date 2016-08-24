import requests
import json
import sys
import tld
import os

 
CFKEY = os.environ.get('CFKEY')
CFEMAIL = os.environ.get('CFEMAIL')

if not CFKEY or not CFEMAIL:
    print("ERROR: There are no credentials in the env vars. Please set env vars CFKEY and CFEMAIL properly so this script can authenticate. You can find them at https://www.cloudflare.com/a/account/my-account after clicking 'view api key'")
    sys.exit(1)

my_domain=tld.get_tld("http://"+sys.argv[1])
headers={"X-Auth-Key": CFKEY, "X-Auth-Email": CFEMAIL, "Content-Type": "application/json"}
url_listzones="https://api.cloudflare.com/client/v4/zones"

r=requests.get(url=url_listzones, headers=headers)
domains=json.loads(r.text)
domain_id=False 
for domain in domains['result']:
    if domain['name'] == my_domain:
        domain_id = domain['id']
if not domain_id:
    print("ERROR: The domain " + my_domain + " doesn't appear in your list of domains. Did you spell it ok? Are you using proper credentials? Your CFEMAIL is " + CFEMAIL)
    print("Here's the list of available domains:")
    for domain in domains['result']:
        print(domain['name'])
    sys.exit(1)

url_listrecords="https://api.cloudflare.com/client/v4/zones/"+domain_id+"/dns_records?per_page=100"
if len(sys.argv) >= 3 and sys.argv[2] == "screen":
    r=requests.get(url=url_listrecords, headers=headers)
    records = json.loads(r.text)
    recordlist = records['result']
    while records['result_info']['page'] < records['result_info']['total_pages']:
        page=str(records['result_info']['page']+1)
        r=requests.get(url=url_listrecords+"&page="+page, headers=headers)
        records = json.loads(r.text)
        recordlist += records['result']
    for record in recordlist:
        print(record['name']+ ": " + record['type'] + " " + record['content'])


url_exportrecords="https://api.cloudflare.com/client/v4/zones/"+domain_id+"/dns_records/export"
r=requests.get(url=url_exportrecords, headers=headers)
with open(my_domain+".txt", "w") as file:
    file.write(r.text)
print("File " + my_domain + ".txt written")
