import requests

def get_spokentutorials_foss():
    spokentutorials = requests.get('http://localhost:8000/api/script/foss_lang/')
    spokentutorials = spokentutorials.json()['spokentutorials']
    return spokentutorials

def get_healthnuritions_foss():
    healthnuritions = requests.get('https://beta.health.spoken-tutorial.org/HealthNutrition/getCatAndLan')
    healthnuritions = healthnuritions.json()['healthnutrition']
    return healthnuritions

def get_spokentutorials_tutorials(fid, lid):
    url = "http://localhost:8000/api/script/tutorials/"+str(fid)+"/"+str(lid)+"/"
    spokentutorials = requests.get(url)
    spokentutorials = spokentutorials.json()['spokentutorials']
    return spokentutorials

def get_healthnuritions_tutorials(fid, lid):
    url = "https://beta.health.spoken-tutorial.org/HealthNutrition/getTopicOnCatAndLan/"+str(fid)+"/"+str(lid)
    healthnuritions = requests.get(url)
    healthnuritions = healthnuritions.json()['healthnutrition']
    return healthnuritions

def get_spokentutorials_tutorials_details(fid, lid, tid):
    pass

def get_healthnutrition_tutorials_details(fid, lid, tid):
    pass

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
    tdetails = None
    if domain == "spokentutorials":
        tdetails = get_spokentutorials_tutorials_details(fid, lid, tid)
    elif domain == "healthnutrition":
        tdetails = get_healthnutrition_tutorials_details(fid, lid, tid)
    return tdetails


def get_spoken_roles(fid, lid, username):
    url = "http://localhost:8000/api/script/roles/"+str(fid)+"/"+str(lid)+"/"+username+"/"
    spoken_roles = requests.get(url)
    spoken_roles = spoken_roles.json()['spokentutorials']
    return spoken_roles['roles']

def get_health_roles(fid, lid, username):
    url = "http://localhost:8000/api/script/roles/"+str(fid)+"/"+str(lid)+"/"+username+"/"
    health_roles = requests.get(url)
    health_roles = health_roles.json()['healthnutrition']
    return health_roles

def get_roles(domain, fid, lid, username):
    roles = None
    if domain == "spokentutorials":
        roles = get_spoken_roles(fid, lid, username)
    elif domain == "healthnutrition":
        roles = get_health_roles(fid, lid, username)
    return roles