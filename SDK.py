#!/usr/bin/env python


#import argparse
#import atexit
import os
import requests
#from random import randrange
from tabulate import tabulate

# colorama for text colouring - required colorama python package (pip install colorama)
from colorama import init
from colorama import Fore, Back, Style

from com.vmware.vmc.model_client import AwsSddcConfig, AccountLinkSddcConfig, EsxConfig, ErrorResponse
from com.vmware.vapi.std.errors_client import InvalidRequest
from vmware.vapi.vmc.client import create_vmc_client

#VMC Variables
refreshtoken = "SetRefreshtokenHere"

# Open http Session
session = requests.Session()

#
# Helper functions - can move these to a libary later
#

def test():
    print ("test")
    return

def login(refreshtoken):
    vmc_client = create_vmc_client(refreshtoken,session)
    return vmc_client

def display_org_list(org_list):
    table = []
    i = 0
    for org in org_list:
        table.append([i, org.id, org.display_name])
        #print (str(i) + ": " + org.display_name + " - " + org.id)
        i += 1
    print(tabulate(table, ['No.','ID', 'Name' ]))

def display_sddc_list(vmc_org_id):
            #sddcs = vmc_client.orgs.Sddcs.list(vmc_org.id)
            #display_sddc_list(sddcs)
    #print ("\nvmc_org " + str(vmc_org.id)) 
    sddcs = vmc_client.orgs.Sddcs.list(vmc_org_id)
    #display_sddc_list(sddcs)
    
    table = []
    i=0
    for sddc in sddcs:
        table.append([i,sddc.id, sddc.name, sddc.resource_config.region])
        i += 1
    print(tabulate(table, ['No.','ID', 'Name', 'AWS Region'])) 

def add_host( org_id, sddc_id ):
    try:
        esx_config = EsxConfig(1)
        task = vmc_client.orgs.sddcs.Esxs.create(org=org_id,
                                                          sddc=sddc_id,
                                                          esx_config=esx_config)
    except InvalidRequest as e:
        # Convert InvalidRequest to ErrorResponse to get error message
        error_response = e.data.convert_to(ErrorResponse)
        raise Exception(error_response.error_messages)

    #wait_for_task(task_client=self.vmc_client.orgs.Tasks,
    #          org_id=self.org_id,
    #          task_id=task.id,
    #          interval_sec=self.interval_sec)

def remove_host( org_id, sddc_id ):
    try:
        esx_config = EsxConfig(1)
        task = vmc_client.orgs.sddcs.Esxs.create(org=org_id,
                                                          sddc=sddc_id,
                                                          esx_config=esx_config,
                                                          action='remove')
    except InvalidRequest as e:
        # Convert InvalidRequest to ErrorResponse to get error message
        error_response = e.data.convert_to(ErrorResponse)
        raise Exception(error_response.error_messages)

    #wait_for_task(task_client=self.vmc_client.orgs.Tasks,
    #          org_id=self.org_id,
    #          task_id=task.id,
    #          interval_sec=self.interval_sec)

def delete_sddc(org_id, sddc_id):

        try:
            task = vmc_client.orgs.Sddcs.delete(org=org_id, sddc=sddc_id)
        except InvalidRequest as e:
            # Convert InvalidRequest to ErrorResponse to get error message
            error_response = e.data.convert_to(ErrorResponse)
            raise Exception(error_response.error_messages)

        #wait_for_task(task_client=self.vmc_client.orgs.Tasks,
        #              org_id=self.org_id,
        #              task_id=task.id,
        #              interval_sec=self.interval_sec)


#
# Present the menu to the user
#

# Variables for the main script
choice = None
vmc_client = None
vmc_orglist = []
vmc_org = None


while choice != "0":
    init()                      # initalise colorama
    print('\n')
    print (Fore.YELLOW + "VMC on AWS Demo Script." +Fore.RESET)
    print ("Please make a selection:")
    print ("1. Connect to VMC on AWS")
    print ("2. Change Org to work with")    
    print ("3. List deployed SDDCs")
    print ("4. Provision new SDDC  X")
    print ("5. Add ESX Host")
    print ("6. Remove ESX Host")
    print ("7. Delete existing SDDC")
    print ("0. Exit")

    choice = input(" >> ")      # get user input
    ch = choice.lower()

    # Execute menu choice
    try:
        print("\n\n")
        if ch == '1':          # Connect to VMC on AWS
            vmc_client = login(refreshtoken)
            print (Fore.GREEN + "Login successful" + Fore.RESET)

            #Pick Org
            vmc_orglist = vmc_client.Orgs.list()
            print ("Available VMC Orgs:")
            display_org_list( vmc_orglist )
            print ("\nSelect Org to work with")
            choice = int( input(" >> ") )
            vmc_org = vmc_orglist[choice]
            print ("Now working in " + vmc_org.display_name)

        elif ch == '2':        # Change Org to work with
            if vmc_client == None:
                print(Fore.RED + "Not connected to VMC" + Fore.RESET)
            else:
                #vmc_orglist = vmc_client.Orgs.list()   # done during login

                print ("Available VMC Orgs:")
                display_org_list( vmc_orglist )
                print ("\nSelect Org to work with")
                choice = int( input(" >> ") )
                vmc_org = vmc_orglist[choice]
                print ("Now working in " + vmc_org.display_name)

        elif ch == '3':        # List deployed SDDCs
            display_sddc_list(vmc_org.id)
            
        elif ch == '4':        # Provision new SDDC  ##########################################
            provider = os.environ.get('VMC_PROVIDER', 'AWS')
            #sddc_config = AwsSddcConfig(region='US_WEST_2', num_hosts=4, name='JD-Test', provider=provider)
            #account_link_sddc_config = AccountLinkSddcConfig(customer_subnet_ids=["subnet-d9d9de94"], connected_account_id="fbf80adb-5c95-3cae-bfb4-4f6df3ccdb5c" )
            account_link_sddc_config = AccountLinkSddcConfig(customer_subnet_ids=["subnet-cb1bf0ae"], connected_account_id="bf9ebc6c-d4bb-37b9-9673-4c523f6478f2" )

            sddc_config = AwsSddcConfig(region='US_WEST_2', 
                                        num_hosts=4, 
                                        name='JD-Test', 
                                        provider=provider, 
                                        vpc_cidr="10.2.0.0/16", 
                                        account_link_sddc_config=[account_link_sddc_config])

            print ("AccountLinkSddcConfig :\n\n" + str(account_link_sddc_config) )
            print ("\nAwsSddcConfig :\n\n" + str(sddc_config) )
            print ("\norg id: " + str(vmc_org.id))

            try:
                task = vmc_client.orgs.Sddcs.create(org=vmc_org.id, sddc_config=sddc_config)
            except InvalidRequest as e:
                # Convert InvalidRequest to ErrorResponse to get error message
                error_response = e.data.convert_to(ErrorResponse)
                raise Exception(error_response.error_messages)

        elif ch == '5':        #Add ESX Host
            org_id = vmc_org.id
            sddcs = vmc_client.orgs.Sddcs.list(org_id)
            display_sddc_list(org_id)
            
            print ("\nSelect SDDC to expand")
            choice = int( input(" >> ") )
            
            sddc_id = sddcs[int(choice)].id
            add_host(org_id, sddc_id)

        elif ch == '6':        #Remove ESX Host
            org_id = vmc_org.id
            sddcs = vmc_client.orgs.Sddcs.list(org_id)
            
            display_sddc_list(org_id)
            print ("\nSelect SDDC to shrink")
            choice = int( input(" >> ") )
            
            sddc_id = sddcs[int(choice)].id
            remove_host(org_id, sddc_id)
            
        elif ch == '7':        #Delete existing SDDC
            org_id = vmc_org.id
            sddcs = vmc_client.orgs.Sddcs.list(org_id)
            
            display_sddc_list(org_id)
            print ("\nSelect SDDC to delete")
            choice = int( input(" >> ") )
            
            sddc_id = sddcs[int(choice)].id
            delete_sddc(org_id, sddc_id)


    except KeyError:
            print (Fore.RED + "Invalid selection, please try again." + Fore.RESET)
