import requests
import pprint

access_token = '0d0dabfd4a34ab4131ea955b1ad3bf64ae0b59a5f8629243012d113f6b0abcf9'
client_id = 'key-em-api-prod'
client_secret = 'secret-em-api-prod'

# Lists all machine data
# url = 'https://api.elementalmachines.io:443/api/machines.json?access_token=' + access_token

# Get probe data from a machine
udid = '5271b48f-b02a-40d0-9faf-ffe0340dab99'
limit = 5
url = 'https://api.elementalmachines.io:443/api/machines/' + udid + '/samples.json?access_token=' + access_token + '&order=asc&limit=' + str(limit)

response = requests.get(url)
pprint.pprint(response.json())