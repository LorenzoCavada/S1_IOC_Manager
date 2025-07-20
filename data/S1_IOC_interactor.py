import requests

from datetime import datetime, timedelta

from config.config_loader import config
from utils.log_handler import logger
from .db_handler import IOC_DB


def __get_s1_ioc():

    # This function is used to refresh the DB. Emptying it before starting

    IOC_DB.delete_all()

    # Preparing the headers for the GET request
    headers = {'Authorization': f'ApiToken {config.s1_token}'}   
    logger.print_log("[INFO] Sending the get request to SentinelOne.")

    ioc_list = []
    try:
        res = requests.get(f"{config.s1_api}threat-intelligence/iocs", headers=headers)
    except:
        logger.print_log(f"[ERROR] Exception while trying to donwload the IOC list.")    

    if res.status_code == 200:
        res_data = (res.json())["data"]
        logger.print_log(f"[SUCCESS] Status code [200] received. {len(res_data)} IOCs found.")

        if(len(res_data) > 0):
            logger.print_log("[INFO] At least one IOC found. Populating the database with the IOCs.")
            try:
                for ioc in res_data:
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
        ioc_list = IOC_DB.fetch_filtered(value, filter_type)

        logger.print_log(f"[SUCCESS] IOC retrieved from the database. {len(ioc_list)} IOCs Found")

        if (len(ioc_list) > 0):
            return [dict(ioc) for ioc in ioc_list]
        else:
            logger.print_log(f"[WARNING] Zero IOC retrieved. Creating an empty IOC to allow table generation.")
    except:
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
            return res_data[0]
        elif(len(res_data) > 1):
            logger.print_log(f"[WARNING] Found multiple entry for value [{value}]. Received [{len(res_data)}] IOCs. Returning only the first one.")
            return res_data[0]
        else:
            logger.print_log(f"[INFO] IOC [{value}] Not found. Returning None.")
            return None
    else:
        logger.print_log(f"[ERROR] Error while trying to donwload the IOC list. Received status code [{res.status_code}]. Returning None.")    
        return None

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

def upload_ioc_to_s1(ioc_value, ioc_type, retention_days, name, description):
    return __post_s1_upload_ioc( ioc_type, retention_days, name, description)