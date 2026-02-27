import json, urllib.request, urllib.error, sys

payload = {
    'age': 25,
    'height': 175,
    'weight': 70,
    'gender': 'male',
    'activity_level': 'moderate',
    'fitness_goal': 'weight loss',
    'workout_time': 45,
    'sleep_duration': 7,
    'stress_level': 'medium',
    'diet_preference': 'vegetarian',
    'living_condition': 'hostel',
    'budget': 'medium',
    'medical_conditions': 'none',
    'cooking_equipment': 'none',
    'context': 'normal'
}

data = json.dumps(payload).encode()
req = urllib.request.Request('http://127.0.0.1:5000/predict', data=data, headers={'Content-Type': 'application/json'})

try:
    resp = urllib.request.urlopen(req, timeout=10).read().decode()
    print(resp)
except urllib.error.HTTPError as e:
    print('HTTP', e.code)
    try:
        body = e.read().decode()
        print(body)
    except Exception as ex:
        print('No body:', ex)
except Exception as ex:
    print('Error:', ex)
