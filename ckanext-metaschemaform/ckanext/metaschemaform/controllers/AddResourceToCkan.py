import urllib2
import urllib
import json

import pprint
import configparser

##read from development.ini file all the required parameters
config = configparser.ConfigParser()
config.read('/var/local/ckan/default/pyenv/src/ckan/development.ini')
admin_api_key=config['ckan:odm_extensions']['admin_api_key']

# Put the details of the dataset we're going to create into a dict.
dataset_dict={}



def AddResourceToCkan(dataset_dict):
	# Use the json module to dump the dictionary to a string for posting.

		
	try:
		data_string = urllib.quote(json.dumps(dataset_dict))

		# We'll use the package_create function to create a new dataset.

		request = urllib2.Request('http://83.212.122.164:15000/api/action/harvest_source_create')

		# Creating a dataset requires an authorization header.
		# Replace *** with your API key, from your user account on the CKAN site
		# that you're creating the dataset on.
		request.add_header('Authorization', str(admin_api_key))

		# Make the HTTP request.
		response = urllib2.urlopen(request, data_string)
		assert response.code == 200

		# Use the json module to load CKAN's response into a dictionary.
		response_dict = json.loads(response.read())
		assert response_dict['success'] is True

		# package_create returns the created package as its result.
		created_package = response_dict['result']
		pprint.pprint(created_package)

	except:
		print('Resource exists.. Updating Resource..')
		data_string = urllib.quote(json.dumps(dataset_dict))

		# We'll use the package_create function to create a new dataset.

		request = urllib2.Request(
                'http://83.212.122.164:15000/api/action/harvest_source_update')

		# Creating a dataset requires an authorization header.
		# Replace *** with your API key, from your user account on the CKAN site
		# that you're creating the dataset on.
		request.add_header('Authorization', str(admin_api_key))

		# Make the HTTP request.
		response = urllib2.urlopen(request, data_string)
		assert response.code == 200

		# Use the json module to load CKAN's response into a dictionary.
		response_dict = json.loads(response.read())
		assert response_dict['success'] is True

		# package_create returns the created package as its result.
		created_package = response_dict['result']
		pprint.pprint(created_package)
