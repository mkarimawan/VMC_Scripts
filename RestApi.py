import requests
import os
import sys
from colorama import init
from colorama import Fore, Back, Style

def login():
    #key = ''
    baseurl = 'https://console.cloud.vmware.com/csp/gateway'
    uri = '/am/api/auth/api-tokens/authorize'
    headers = {'Content-Type':'application/json'}
    payload = {'refresh_token': key}
    r = requests.post(f'{baseurl}{uri}', headers = headers, params = payload)
    if r.status_code != 200:
        print(Fore.RED + f'Unsuccessful Login Attmept. Error code {r.status_code}' + Fore.RESET)
        return None
    else:
        print(Fore.GREEN + 'Login successful. ' + Fore.RESET)
        auth_json = r.json()['access_token']
        auth_Header = {'Content-Type':'application/json','csp-auth-token':auth_json}
        return auth_Header


def getOrgList(auth_header):
    ol = requests.get('https://vmc.vmware.com/vmc/api/orgs', headers = auth_header)
    if ol.status_code != 200:
        print (f'Unsuccessful Org Listing. Error code {ol.status_code}')
    else:
        return ol

def displayOrgList(ol):
    for org in ol.json():
        print("Org Name: " + org['display_name'])
        print("Org ID: " + org['id'])

def getSddcList(auth_header, orgList):
    orgID = orgList.json()[0]['id']
    sddcList = requests.get(f'https://vmc.vmware.com/vmc/api/orgs/{orgID}/sddcs', headers = auth_header)
    if sddcList.status_code != 200:
        print('API Error')
    else:
        return sddcList

def displaySDDCList(sddcList):
    for i,sddc in enumerate(sddcList.json()):
        print("\n")
        print(f"SDDC Index: {i}" )
        print("SDDC Name: " + sddc['name'])
        print("SDDC Create Date: " + sddc['created'])
        print("SDDC Provider: " + sddc['provider'])
        print("SDDC Region: " + sddc['resource_config']['region'])
        print("SDDC ID: " + sddc['id'])
   
def deleteSDDC(auth_header, orgList, sddcIndex):
    orgID = orgList.json()[0]['id']
    sddcID = sddcList.json()[sddcIndex]['id']
    r = requests.delete(f'https://vmc.vmware.com/vmc/api/orgs/{orgID}/sddcs/{sddcID}', headers = auth_header)
    return r

def addEsxHost(auth_header, orgList, sddcID):
    orgID = orgList.json()[0]['id']
    data = { "action":"add", "availability_zone": "", "num_hosts": "1"}
    r = requests.post(f'https://vmc.vmware.com/vmc/api/orgs/{orgID}/sddcs/{sddcID}/esxs', params = data, headers = auth_header)
    return r


def addSDDC(auth_header, orgList):
    orgID = orgList.json()[0]['id']
    strRequest = {
        "num_hosts": "4",
        "name": "MK-Test-API",
        "provider": "ZEROCLOUD",
        "region": "EU_WEST_2",
        "account_link_sddc_config":
            [
                {
                    "customer_subnet_ids": ["subnet-d9d9de94"],
                    "connected_account_id": "def702b1-333c-4219-af22-206ac6e3ed66"
                }
            ],
        "sddc_type": "",
        "deployment_type": "SingleAZ",
        "vxlan_subnet": "10.75.0.0/23"
    }
    
    r = requests.post(f'https://vmc.vmware.com/vmc/api/orgs/{orgID}/sddcs', headers = auth_header, json = strRequest)

    return r


def exec_menu(choice):
    ch = choice.lower()

    global auth_header
    global orgList
    global sddcList

    if ch == '':
        main()
    else:
        try:
            # Login
            if ch == '1':        
                auth_header = login()
                if auth_header !=None:
                    orgList = getOrgList(auth_header)
                    sddcList = getSddcList(auth_header, orgList)
            # Update VMC Data
            elif ch == '2':     
                if auth_header !=None:
                    orgList = getOrgList(auth_header)
                    sddcList = getSddcList(auth_header, orgList)
            # List Orgs
            elif ch == '3':     
                displayOrgList( orgList )
            # List SDDCs
            elif ch == '4':     
                displaySDDCList( sddcList )
            # Provision SDDC
            elif ch == '5':     
                #print ("Not yet implemented")
                r = addSDDC(auth_header, orgList)
                print (Fore.GREEN + "SDDC Creation in Progress - " + str(r.status_code) + Fore.RESET)
            # Delete SDDC
            elif ch == '6':
                sddcIndex = int(input(" Enter SDDC Index:  "))
                r = deleteSDDC(auth_header, orgList, sddcIndex)
                if r.status_code != 202:
                    print (Fore.RED + "Delete failed : " + str(r.status_code) + Fore.RESET)
                else:
                    print(Fore.GREEN + 'SDDC delete successful. ' + Fore.RESET)
            # Add ESX Host
            elif ch == '7':
                sddcID = input(" Enter SDDC ID:  ")
                r = addEsxHost(auth_header, orgList, sddcID)
                if r.status_code != 202:
                    print (Fore.RED + "Add host failed : " + str(r.status_code) + " - " + str(r.error_code) + Fore.RESET)
                else:
                    print(Fore.GREEN + 'Add host successful. ' + Fore.RESET)
            elif ch == '0':     
                print ("Thanks for using this service. Have a great day!")
                sys.exit(0)
            else:
                print (Fore.RED + "Invalid selection, please try again." + Fore.RESET)

        except KeyError:
            print (Fore.RED + "Invalid selection, please try again." + Fore.RESET)
    
    main()
    return
    


def main():
    init()
    print('\n')
    print (Fore.YELLOW + "VMC on AWS Demo Script." +Fore.RESET)
    print ("Please make a selection:")
    print ("1. Connect to VMC on AWS")
    print ("2. Update VMC Data")    
    print ("3. List VMC Organisations available")
    print ("4. List available SDDCs")
    print ("5. Provision new SDDC")
    print ("6. Delete existing SDDC")
    print ("7. Add ESX Host (not yet implemented)")
    print ("0. Exit")

    choice = input(" >> ")
    exec_menu (choice)

    return

global auth_header
global orgList
global sddcList

auth_header = None
orgList = None
sddcList = None




if __name__ == '__main__':
    main()
    