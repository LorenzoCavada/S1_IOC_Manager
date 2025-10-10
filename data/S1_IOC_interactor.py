import requests, traceback

from datetime import datetime, timedelta

from config.config_loader import config
from utils.log_handler import logger
from .db_handler import IOC_DB


def __get_s1_ioc():

    # This function is used to refresh the DB. Emptying it before starting

    #IOC_DB.delete_all()

    # Preparing the headers for the GET request
    headers = {'Authorization': f'ApiToken {config.s1_token}'}   
    logger.print_log("[INFO] Sending the get request to SentinelOne.")

    ioc_list = []
    try:
        params = {
            "limit": 1000,
            "creationTime__gt": (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        }
        res = requests.get(f"{config.s1_api}threat-intelligence/iocs?limit=1000", headers=headers, params=params)
        res_data = []

        i = 1
        while True:
            data = res.json()
            res_data.extend(data.get("data", []))  
            next_cursor = data.get("pagination", {}).get("nextCursor")

            if not next_cursor:
                break

            logger.print_log(f"[INFO] More than 1000 IOCs received. Asking for next page. Page number: {i}.")
            
            res = requests.get(f"{config.s1_api}threat-intelligence/iocs?limit=1000", headers=headers, params={"cursor": next_cursor})

    except Exception:
        print(traceback.format_exc())  

    if res.status_code == 200:
        logger.print_log(f"[SUCCESS] Status code [200] received. {len(res_data)} IOCs found.")

        if(len(res_data) > 0):
            logger.print_log("[INFO] At least one IOC found. Populating the database with the IOCs.")
            try:
                for ioc in res_data:
                    if not IOC_DB.search_ioc(ioc['value']):
                        IOC_DB.insert_ioc(name = ioc['name'], 
                                        description = ioc['description'], 
                                        ioc_type = ioc['type'],
                                        value = ioc['value'],
                                        metadata = ioc['metadata'],
                                        source =  ioc['source'],
                                        creationTime = ioc['creationTime'],
                                        updatedAt = ioc['updatedAt'],
                                        validUntil = ioc['validUntil']
                    )
            except:
                logger.print_log(f"[ERROR] Exception while trying to populate the DB.")
            
            logger.print_log("[INFO] Database correctly populted. Exporting and converting it to a python dictionary.")

            return [dict(ioc) for ioc in IOC_DB.fetch_all()]
        else:
            logger.print_log("[WARNING] No IOC was found. Returning an empty IOC to allow table generation.")
    else:
        logger.print_log(f"[ERROR] Error while trying to donwload the IOC list. Received status code [{res.status_code}].")    

    logger.print_log("[WARNING] Something went wrong. Creating an empty IOC to allow table generation.")
    
    ioc = {
                        'num': 1,
                        'name': f"No IOC found",
                        'description': "",
                        'type': "",
                        'value': "",
                        'metadata': "",                
                        'source': "",                
                        'creationTime': "",
                        'updatedAt': "",
                        'validUntil': ""
                    }
                    
    ioc_list.append(ioc)

    return ioc_list

def __get_db_ioc_by_filter(value=None, filter_type="Value"):
    logger.print_log(f"[INFO] Sending the get request to the internal DB filtered for [{value}], filter type set to [{filter_type}].")
    ioc_list = []
    try:
        online_search = []
        ioc_list = IOC_DB.fetch_filtered(value, filter_type)
        if(len(ioc_list) > 0):
            logger.print_log(f"[SUCCESS] IOC retrieved from the database. {len(ioc_list)} IOCs Found")
        elif(filter_type == "Value"): # Value is supposed to be unique, so if we don't find it in the DB we try to get it from S1
            logger.print_log(f"[INFO] Zero IOC retrieved from the internal DB filtered for [{value}]. Trying to get it from SentinelOne.")
            online_search = __get_s1_ioc_by_value(value)
        
        if(filter_type =="Name"):
            logger.print_log(f"[INFO] Retrieving IOC from the internal DB filtered for name [{value}].")
            online_search = __get_s1_ioc_by_name(value)
        elif(filter_type == "Description"):
            logger.print_log(f"[INFO] Retrieving IOC from the internal DB filtered for description [{value}].")
            online_search = __get_s1_ioc_by_description(value)
        elif(filter_type == "User"):
            logger.print_log(f"[INFO] Retrieving IOC from the internal DB filtered for creator [{value}].")
            online_search = __get_s1_ioc_by_creator(value)
        elif(filter_type == "Source"):
            logger.print_log(f"[INFO] Retrieving IOC from the internal DB filtered for source [{value}].")
            online_search = __get_s1_ioc_by_source(value)

        for ioc in online_search:
            if IOC_DB.search_ioc(ioc['value']):
                logger.print_log(f"[INFO] IOC [{value}] already present in the internal DB. No need to insert it again.")
            else:
                logger.print_log(f"[INFO] IOC [{value}] not present in the internal DB. Inserting it.")
                IOC_DB.insert_ioc(name = ioc['name'], 
                                        description = ioc['description'], 
                                        ioc_type = ioc['type'],
                                        value = ioc['value'],
                                        metadata = ioc['metadata'],
                                        source =  ioc['source'],
                                        creationTime = ioc['creationTime'],
                                        updatedAt = ioc['updatedAt'],
                                        validUntil = ioc['validUntil']
                )

        # Fetch again the IOC from the DB to return it
        ioc_list = IOC_DB.fetch_filtered(value, filter_type)  
        
        if (len(ioc_list) > 0):
            return [dict(ioc) for ioc in ioc_list]
        else:
            logger.print_log(f"[WARNING] Zero IOC retrieved. Creating an empty IOC to allow table generation.")
    except Exception as e:
        logger.print_log(e)
        logger.print_log(f"[ERROR] Error while trying to get the IOC from the internal DB filtered for [{value}]. Creating an empty IOC to allow table generation.")

    ioc = {
        'num': 1,
        'name': f"No IOC found",
        'description': "",
        'type': "",
        'value': "",
        'metadata': "",                
        'source': "",                
        'creationTime': "",
        'updatedAt': "",
        'validUntil': ""
    }
                    
    ioc_list.append(ioc)
    return ioc_list    

def __get_s1_ioc_by_value(value):
    headers = {'Authorization': f'ApiToken {config.s1_token}'}   
    logger.print_log(f"[INFO] Sending the get request for value [{value}] to SentinelOne.")

    try:
        res = requests.get(f"{config.s1_api}threat-intelligence/iocs?value={value}", headers=headers)
    except:
        logger.print_log(f"[ERROR] Exception while trying to donwload the IOC list.")    

    if res.status_code == 200:
        res_data = (res.json())["data"]
        logger.print_log(f"[SUCCESS] Status code [200] received for IOC [{value}].")

        if(len(res_data) == 1):
            return res_data
        elif(len(res_data) > 1):
            logger.print_log(f"[WARNING] Found multiple entry for value [{value}]. Received [{len(res_data)}] IOCs. Returning only the first one.")
            return res_data
        else:
            logger.print_log(f"[INFO] IOC [{value}] Not found. Returning None.")
            return []
    else:
        logger.print_log(f"[ERROR] Error while trying to donwload the IOC list. Received status code [{res.status_code}]. Returning None.")    
        return []

def __get_s1_ioc_by_name(name):
    headers = {'Authorization': f'ApiToken {config.s1_token}'}   
    logger.print_log(f"[INFO] Sending the get request for name [{name}] to SentinelOne.")

    try:
        res = requests.get(f"{config.s1_api}threat-intelligence/iocs?name__contains={name}", headers=headers)
    except:
        logger.print_log(f"[ERROR] Exception while trying to donwload the IOC list.")    

    if res.status_code == 200:
        res_data = (res.json())["data"]
        logger.print_log(f"[SUCCESS] Status code [200] received for name [{name}].")

        if(len(res_data) == 1):
            return res_data
        elif(len(res_data) > 1):
            logger.print_log(f"[SUCCESS] Found multiple entry for name [{name}]. Received [{len(res_data)}] IOCs.")
            return res_data
        else:
            logger.print_log(f"[INFO] Name [{name}] Not found. Returning None.")
            return []
    else:
        logger.print_log(f"[ERROR] Error while trying to donwload the IOC list. Received status code [{res.status_code}]. Returning None.")    
        return []
    
def __get_s1_ioc_by_description(description):
    headers = {'Authorization': f'ApiToken {config.s1_token}'}   
    logger.print_log(f"[INFO] Sending the get request for description [{description}] to SentinelOne.")

    try:
        res = requests.get(f"{config.s1_api}threat-intelligence/iocs?description__contains={description}", headers=headers)
    except:
        logger.print_log(f"[ERROR] Exception while trying to donwload the IOC list.")    

    if res.status_code == 200:
        res_data = (res.json())["data"]
        logger.print_log(f"[SUCCESS] Status code [200] received for description [{description}].")

        if(len(res_data) == 1):
            return res_data
        elif(len(res_data) > 1):
            logger.print_log(f"[SUCCESS] Found multiple entry for description [{description}]. Received [{len(res_data)}] IOCs.")
            return res_data
        else:
            logger.print_log(f"[INFO] Description [{description}] Not found. Returning None.")
            return []
    else:
        logger.print_log(f"[ERROR] Error while trying to donwload the IOC list. Received status code [{res.status_code}]. Returning None.")    
        return []
    
def __get_s1_ioc_by_creator(creator):
    headers = {'Authorization': f'ApiToken {config.s1_token}'}   
    logger.print_log(f"[INFO] Sending the get request for creator [{creator}] to SentinelOne.")

    try:
        res = requests.get(f"{config.s1_api}threat-intelligence/iocs?creator__contains={creator}", headers=headers)
    except:
        logger.print_log(f"[ERROR] Exception while trying to donwload the IOC list.")    

    if res.status_code == 200:
        res_data = (res.json())["data"]
        logger.print_log(f"[SUCCESS] Status code [200] received for creator [{creator}].")

        if(len(res_data) == 1):
            return res_data
        elif(len(res_data) > 1):
            logger.print_log(f"[SUCCESS] Found multiple entry for creator [{creator}]. Received [{len(res_data)}] IOCs.")
            return res_data
        else:
            logger.print_log(f"[INFO] Creator [{creator}] Not found. Returning None.")
            return []
    else:
        logger.print_log(f"[ERROR] Error while trying to donwload the IOC list. Received status code [{res.status_code}]. Returning None.")    
        return []

def __get_s1_disabled_ioc():
    headers = {'Authorization': f'ApiToken {config.s1_token}'}   
    logger.print_log(f"[INFO] Sending the get request for user [{config.s1_account_id}] to SentinelOne to get disabled IoCs.")

    body = {
        "accountIds": "[{config.s1_account_id}]",
    }

    try:
        res = requests.get(f"{config.s1_api}threat-intelligence/user-config", headers=headers, json=body)
    except:
        logger.print_log(f"[ERROR] Exception while trying to donwload the IOC list.")    

    if res.status_code == 200:
        res_data = (res.json())["data"]

        disabled_ioc = []
        for data in res_data:
            for ioc in data["excludeTii"]:
                disabled_ioc.append(ioc)

        logger.print_log(f"[SUCCESS] Status code [200] received for user [{config.s1_account_id}].")

        if(len(disabled_ioc) == 1):
            return disabled_ioc
        elif(len(disabled_ioc) > 1):
            logger.print_log(f"[SUCCESS] Found multiple entry for user [{config.s1_account_id}]. Received [{len(disabled_ioc)}] IOCs.")
            return disabled_ioc
        else:
            logger.print_log(f"[INFO] User [{config.s1_account_id}] Not found. Returning None.")
            return []
    else:
        logger.print_log(f"[ERROR] Error while trying to donwload the IOC list. Received status code [{res.status_code}]. Returning None.")    
        return []

def __get_s1_ioc_by_source(source):
    headers = {'Authorization': f'ApiToken {config.s1_token}'}   
    logger.print_log(f"[INFO] Sending the get request for source [{source}] to SentinelOne.")

    try:
        res = requests.get(f"{config.s1_api}threat-intelligence/iocs?source__contains={source}", headers=headers)
    except:
        logger.print_log(f"[ERROR] Exception while trying to donwload the IOC list.")    

    if res.status_code == 200:
        res_data = (res.json())["data"]
        logger.print_log(f"[SUCCESS] Status code [200] received for source [{source}].")

        if(len(res_data) == 1):
            return res_data
        elif(len(res_data) > 1):
            logger.print_log(f"[SUCCESS] Found multiple entry for source [{source}]. Received [{len(res_data)}] IOCs.")
            return res_data
        else:
            logger.print_log(f"[INFO] Source [{source}] Not found. Returning None.")
            return []
    else:
        logger.print_log(f"[ERROR] Error while trying to donwload the IOC list. Received status code [{res.status_code}]. Returning None.")    
        return []

def __delete_s1_ioc_by_value(value):
    headers = {'Authorization': f'ApiToken {config.s1_token}'}   
    logger.print_log(f"[INFO] Sending the delete request for value [{value}] to SentinelOne.")

    body = {
        "filter": {
            "value": f"{value}"
        }
    }
    
    try:
        res = requests.delete(f"{config.s1_api}threat-intelligence/iocs", headers=headers, json=body)
    except:
        logger.print_log(f"[ERROR] Exception while trying to delete the IOC with value [{value}].")   
        return False
         
    if res.status_code == 200:
        logger.print_log(f"[SUCCESS] Status code [200] received for deleteing IOC [{value}].")
        res_data = (res.json())["data"]
        logger.print_log(f"[INFO] IOC [{value}] has been deleted. Number of affected element: {[{res_data['affected']}]}.")

        return True

    else:
        logger.print_log(f"[ERROR] Error while trying to delete the IOC [{value}]. Received status code [{res.status_code}].")    
        return False
    
def __disable_s1_ioc_by_value(value, description=""):
    headers = {'Authorization': f'ApiToken {config.s1_token}'}   
    logger.print_log(f"[INFO] Sending the disable request for value [{value}] to SentinelOne.")

    body = {
        "description": "{description}",
	    "disableRh": "",
		"disableThreat": "",
		"enableXdrMatching": "",
		"excludeTii": f"[{value}]",
		"scopeId": "{config.s1_account_id}",
		"scopeLevel": "account",
		"threatExcludeFields": "",
		"threatMinScore": ""
    }
    
    try:
        res = requests.delete(f"{config.s1_api}threat-intelligence/user-config", headers=headers, json=body)
    except:
        logger.print_log(f"[ERROR] Exception while trying to disable the IOC with value [{value}].")   
        return False
         
    if res.status_code == 200:
        logger.print_log(f"[SUCCESS] Status code [200] received for disabling IOC [{value}].")
        res_data = (res.json())["data"]
        logger.print_log(f"[INFO] IOC [{value}] has been disabled. Number of affected element: {[{res_data['affected']}]}.")

        return True

    else:
        logger.print_log(f"[ERROR] Error while trying to delete the IOC [{value}]. Received status code [{res.status_code}].")    
        return False

def __enable_s1_ioc_by_value(value):
    headers = {'Authorization': f'ApiToken {config.s1_token}'}   
    logger.print_log(f"[INFO] Sending the enable request for value [{value}] to SentinelOne.")

    body = {
	    "disableRh": "",
		"disableThreat": "",
		"enableXdrMatching": "",
		"excludeTii": f"[{value}]",
		"scopeId": "{config.s1_account_id}",
		"scopeLevel": "account",
		"threatExcludeFields": "",
		"threatMinScore": ""
    }
    
    try:
        res = requests.delete(f"{config.s1_api}threat-intelligence/user-config", headers=headers, json=body)
    except:
        logger.print_log(f"[ERROR] Exception while trying to enable the IOC with value [{value}].")   
        return False
         
    if res.status_code == 200:
        logger.print_log(f"[SUCCESS] Status code [200] received for enabling IOC [{value}].")
        res_data = (res.json())["data"]
        logger.print_log(f"[INFO] IOC [{value}] has been enabled. Number of affected element: {[{res_data['affected']}]}.")

        return True

    else:
        logger.print_log(f"[ERROR] Error while trying to enabling the IOC [{value}]. Received status code [{res.status_code}].")    
        return False


def __post_s1_upload_ioc(ioc_value, ioc_type, retention_days, name, description):
    headers = {'Authorization': f'ApiToken {config.s1_token}'}
    logger.print_log("[INFO] Sending POST request to the SentinelOne API.")

    s1_ti_body = {
        "filter": {
            "tenant": "False",
            "accountIds": [
                f"{config.s1_account_id}"
            ]
	    },
        "data": [
            {
            "value": ioc_value,
            "type": ioc_type,
            "metadata": config.creator_mail,
            "creator": config.creator_mail,
            "originalRiskScore": "100",
            "validUntil": str(datetime.now() + timedelta(days=retention_days)),
            "method": "EQUALS",
            "name": f"{config.ioc_tag} {name}",
            "description": f"{config.ioc_tag} {description}",
            "source": "Manual Upload",
            "creationTime": str(datetime.now())
            }
        ]
    }

    try:        
        res = requests.post(f"{config.s1_api}threat-intelligence/iocs", headers=headers, json=s1_ti_body)

        if res.status_code == 200:
            return res
        else:
            return res
    except:
        return None

def get_s1_ioc():
    return __get_s1_ioc()

def get_s1_filtered_ioc(value, filter_type):
    return __get_db_ioc_by_filter(value, filter_type)

def get_s1_ioc_by_value(value):
    return __get_s1_ioc_by_value(value)

def delete_s1_ioc_by_value(value):
    return __delete_s1_ioc_by_value(value)

def enable_s1_ioc_by_value(value):
    return __enable_s1_ioc_by_value(value)

def disable_s1_ioc_by_value(value, description=""):
    return __disable_s1_ioc_by_value(value, description)

def upload_ioc_to_s1(ioc_value, ioc_type, retention_days, name, description):
    return __post_s1_upload_ioc(ioc_value, ioc_type, retention_days, name, description)

def get_s1_disabled_ioc():
    return __get_s1_disabled_ioc()