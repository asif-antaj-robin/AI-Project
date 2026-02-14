import requests
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_doctors_from_api(city: str, specialty: str):

    url = "https://doctorsapi.com/api/doctors"
    api_key = os.getenv("DOCTORS_API_KEY", "").strip()
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    params = {"location": city, "specialty": specialty, "limit": 10}

    try:
        print(f"Connecting to DoctorsAPI for {specialty} in {city}...")
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 401:
            print("DoctorsAPI Key not warking। Automatic backup Database (NPI Registry) using")
            return fetch_from_backup_npi(city, specialty)
            
        response.raise_for_status()
        data = response.json()
        return format_doctor_data(data.get('data', []), specialty)

    except Exception as e:
        print(f"DoctorsAPI is Problem: {e}. Check backup NPI Registry.")
        return fetch_from_backup_npi(city, specialty)

def fetch_from_backup_npi(city: str, specialty: str):
   
    npi_url = "https://npiregistry.cms.hhs.gov/api/"
    params = {
        "version": "2.1",
        "city": city,
        "taxonomy_description": specialty,
        "limit": 10
    }
    
    try:
        res = requests.get(npi_url, params=params, timeout=10)
        data = res.json()
        return format_doctor_data(data.get('results', []), specialty, is_npi=True)
    except:
        return []

def format_doctor_data(raw_data, specialty, is_npi=False):

    formatted = []
    for doc in raw_data:
    
        basic = doc.get('basic', {}) if is_npi else doc
        addr_raw = doc.get('addresses', [{}])[0] if is_npi else doc.get('address', {})
        
        address_obj = {
            "firstLine": addr_raw.get('address_1') if is_npi else addr_raw.get('firstLine', ''),
            "secondLine": addr_raw.get('address_2') if is_npi else addr_raw.get('secondLine', None),
            "city": addr_raw.get('city', ''),
            "state": addr_raw.get('state', ''),
            "countryCode": addr_raw.get('country_code') if is_npi else addr_raw.get('countryCode', 'US'),
            "postalCode": addr_raw.get('postal_code') if is_npi else addr_raw.get('postalCode', ''),
            "coords": [] if is_npi else addr_raw.get('coords', [])
        }

        formatted.append({
            "id": str(doc.get('number')) if is_npi else doc.get('id'), # MongoDB ObjectId
            "npi": doc.get('number') if is_npi else doc.get('npi'),
            "name": f"Dr. {basic.get('first_name', '')} {basic.get('last_name', '')}" if is_npi else doc.get('name'),
            "gender": basic.get('gender', 'N/A') if is_npi else doc.get('gender', 'M/F'),
            "phone": addr_raw.get('telephone_number', 'N/A') if is_npi else doc.get('phone', 'N/A'),
            "fax": addr_raw.get('fax_number', 'N/A') if is_npi else doc.get('fax', 'N/A'),
            "address": address_obj,
            "credentials": basic.get('credential', 'MD') if is_npi else doc.get('credentials', 'MD'),
            "specialties": [specialty],
            "organizationIds": []
        })
    return formatted