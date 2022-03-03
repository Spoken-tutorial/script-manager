import json
import requests
from script.config import spoken_Url, health_url
def get_spokentutorials_foss():
    try:
        url = spoken_Url + 'api/script/foss_lang/'
        spokentutorials = requests.get(url)
        spokentutorials = spokentutorials.json()['spokentutorials']
        return spokentutorials
    except:
        return None

def get_healthnuritions_foss():
    try:
        # url = health_url + "HealthNutrition/getCatAndLan"
        url = health_url + "getCatAndLan"
        healthnuritions = requests.get(url)
        healthnuritions = healthnuritions.json()['healthnutrition']
        return healthnuritions
    except:
        return None

def get_spokentutorials_tutorials(fid, lid):
    url = spoken_Url + "api/script/tutorials/"+str(fid)+"/"+str(lid)+"/"
    spokentutorials = requests.get(url)
    spokentutorials = spokentutorials.json()['spokentutorials']
    return spokentutorials

def get_healthnuritions_tutorials(fid, lid):
    url = health_url + "getTopicOnCatAndLan/"+str(fid)+"/"+str(lid)
    healthnuritions = requests.get(url)
    healthnuritions = healthnuritions.json()['healthnutrition']
    return healthnuritions

def get_spokentutorials_tutorials_details(fid, lid, tid):
    url = spoken_Url+"api/script/tutorial_detail/"+str(fid)+"/"+str(lid)+"/"+str(tid)+"/"
    spokentutorials = requests.get(url)
    spokentutorials = spokentutorials.json()['spokentutorials']
    return spokentutorials

def get_healthnutrition_tutorials_details(fid, lid, tid):
    # url = health_url+"HealthNutrition/getTutorial/" + str(tid)
    url = health_url+"getTutorial/" + str(tid)
    healthnuritions = requests.get(url)
    print(f"healthnuritions --- {healthnuritions}")
    # healthnuritions = healthnuritions.json()['healthnutrition']
    healthnuritions_all = healthnuritions.json()
    print(f"healthnuritions_all 2******** {healthnuritions_all}")
    healthnuritions = healthnuritions_all['healthnutrition']
    
    encodedUnicode = json.dumps(healthnuritions_all, ensure_ascii=False)
    decoded = json.loads(encodedUnicode)
    healthnuritions = decoded['healthnutrition']
    print
    data = {
        'foss': healthnuritions['tutorial'][0]['foss'], 
        'language':healthnuritions['tutorial'][0]['language'], 
        'tutorial': {'tutorial': healthnuritions['tutorial'][0]['tutorial'], 'outline': healthnuritions['tutorial'][0]['outline']}
        }
    print(f"\n\n*****************************************************************")
    print(f"\n\n*****************************************************************")
    print(f"data ******************************************************************{data}")
    
    return data

def get_all_foss_languages():
    spokentutorials = get_spokentutorials_foss()
    healthnuritions = get_healthnuritions_foss()
    return {'spokentutorials':spokentutorials, 'healthnutrition':healthnuritions}

def get_all_tutorials(domain, fid, lid):
    tutorials = None
    if domain == "spokentutorials":
        tutorials = get_spokentutorials_tutorials(fid, lid)
    elif domain == "healthnutrition":
        tutorials = get_healthnuritions_tutorials(fid, lid)
    return tutorials

def get_tutorial_details(domain, fid, lid, tid):
    print(f"2.1 domain - {domain}, fid - {fid}, lid - {lid}, tid - {tid}")
    tdetails = None
    if domain == "spokentutorials":
        tdetails = get_spokentutorials_tutorials_details(fid, lid, tid)
    elif domain == "healthnutrition":
        print(f"2.2 domain is healthnutrition")
        tdetails = get_healthnutrition_tutorials_details(fid, lid, tid)
    print(f"tdetails --- {tdetails}")
    return tdetails


#fetch roles 

def get_spoken_roles(fid, lid, username):
    url = spoken_Url+"api/script/roles/"+str(fid)+"/"+str(lid)+"/"+username+"/"
    spoken_roles = requests.get(url)
    spoken_roles = spoken_roles.json()['spokentutorials']
    return spoken_roles['roles']

def get_health_roles(fid, lid, username):
    # url = health_url+"HealthNutrition/getRolesOnCatLanUser/" +str(fid)+"/"+str(lid)+"/"+username
    print(" TEST *********  14 get_health_roles")
    url = health_url+"getRolesOnCatLanUser/" +str(fid)+"/"+str(lid)+"/"+username
    health_roles = requests.get(url)
    health_roles = health_roles.json()['healthnutrition']
    print(" TEST *********  15 health_roles : {}".format(health_roles))
    return health_roles['roles']

def get_roles(domain, fid, lid, username):
    print(" TEST *********  13 get_roles")
    roles = None
    if domain == "spokentutorials":
        roles = get_spoken_roles(fid, lid, username)
    elif domain == "healthnutrition":
        roles = get_health_roles(fid, lid, username)
    return roles