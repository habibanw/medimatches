import os
import requests

def get_nearby_zip_codes(zip):
    #trim the zipcode to the first five digits
    if len(zip) < 5:
       return ""

    z = zip[:5]
    zip_list = []

    ZIPCODE_API_KEY = os.getenv('ZIPCODE_API_KEY')
    url = 'https://www.zipcodeapi.com/rest/' + ZIPCODE_API_KEY + '/radius.json/' + str(z) + '/15/mile'
   
    response = requests.get(url)

    if response.status_code == 200:
        zip_dict = response.json()

        for zip in zip_dict.get('zip_codes'):
            zip_list.append(zip.get("zip_code"))
            
        return zip_list
    
    else:
       zip_list.append(zip)
       return zip_list
    

def get_zipcodes_from_city_state(city, state):
    
    ZIPCODE_API_KEY = os.getenv('ZIPCODE_API_KEY')
    url = 'https://www.zipcodeapi.com/rest/' + ZIPCODE_API_KEY +'/city-zips.json/' + city + '/' + state
   
    response = requests.get(url)

    if response.status_code == 200:
        zip_dict = response.json()
        return zip_dict.get('zip_codes')
    
    else:
       return ""
    


