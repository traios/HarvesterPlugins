import urllib2

from ckan.lib.base import c
from ckan import model
from ckan.model import Session, Package
from ckan.logic import ValidationError, NotFound, get_action
from ckan.lib.helpers import json

from ckanext.harvest.model import HarvestJob, HarvestObject, HarvestGatherError, \
                                    HarvestObjectError
import pymongo
import logging
import configparser
import harvester_final
log = logging.getLogger(__name__)
from base import HarvesterBase

##read from development.ini file all the required parameters
config = configparser.ConfigParser()
config.read('/var/local/ckan/default/pyenv/src/ckan/development.ini')
html_harvester_log_file_path=config['ckan:odm_extensions']['html_harvester_log_file_path']
backup_file_path=config['ckan:odm_extensions']['backup_file_path']
mongoclient=config['ckan:odm_extensions']['mongoclient']
mongoport=config['ckan:odm_extensions']['mongoport']

text_file = open(str(html_harvester_log_file_path), "a")
client = pymongo.MongoClient(str(mongoclient), int(mongoport))

class HTMLHarvester(HarvesterBase):
    '''
    A Harvester for HTML-based instances
    '''
    config = None

    api_version = 2

    def _get_rest_api_offset(self):
        return '/api/%d/rest' % self.api_version

    def _get_search_api_offset(self):
        return '/api/%d/search' % self.api_version

    def _get_content(self, url):
        http_request = urllib2.Request(
            url = url,
        )

        api_key = self.config.get('api_key',None)
        if api_key:
            http_request.add_header('Authorization',api_key)
        http_response = urllib2.urlopen(http_request)

        return http_response.read()

    def _get_group(self, base_url, group_name):
        url = base_url + self._get_rest_api_offset() + '/group/' + group_name
        try:
            content = self._get_content(url)
            return json.loads(content)
        except Exception, e:
            raise e

    def _set_config(self,config_str):
        if config_str:
            self.config = json.loads(config_str)
            if 'api_version' in self.config:
                self.api_version = int(self.config['api_version'])

            log.debug('Using config: %r', self.config)
        else:
            self.config = {}

    def info(self):
        return {
            'name': 'html',
            'title': 'HTML',
            'description': 'Harvests remote HTML instances',
            'form_config_interface':'Text'
        }

    def validate_config(self,config):
        if not config:
            return config

        try:
            config_obj = json.loads(config)

            if 'api_version' in config_obj:
                try:
                    int(config_obj['api_version'])
                except ValueError:
                    raise ValueError('api_version must be an integer')

            if 'default_tags' in config_obj:
                if not isinstance(config_obj['default_tags'],list):
                    raise ValueError('default_tags must be a list')

            if 'default_groups' in config_obj:
                if not isinstance(config_obj['default_groups'],list):
                    raise ValueError('default_groups must be a list')

                # Check if default groups exist
                context = {'model':model,'user':c.user}
                for group_name in config_obj['default_groups']:
                    try:
                        group = get_action('group_show')(context,{'id':group_name})
                    except NotFound,e:
                        raise ValueError('Default group not found')

            if 'default_extras' in config_obj:
                if not isinstance(config_obj['default_extras'],dict):
                    raise ValueError('default_extras must be a dictionary')

            if 'user' in config_obj:
                # Check if user exists
                context = {'model':model,'user':c.user}
                try:
                    user = get_action('user_show')(context,{'id':config_obj.get('user')})
                except NotFound,e:
                    raise ValueError('User not found')

            for key in ('read_only','force_all'):
                if key in config_obj:
                    if not isinstance(config_obj[key],bool):
                        raise ValueError('%s must be boolean' % key)

        except ValueError,e:
            raise e

        return config


    def gather_stage(self,harvest_job):
		db2 = client.odm
		collection=db2.html_jobs
		backupi=0
        ## Get source URL
		text_file1 = open(str(backup_file_path), "r")
		backup=text_file1.readlines()

		#if len(backup)==2:
			#backupurl=str(backup[0].replace("\n",""))
			#backupi=int(backup[1])
			#document=collection.find_one({"cat_url":backupurl})
			#id1=document['_id']
			#harvester_final.read_data(id1,backupi)

		backupi=0
		source_url = harvest_job.source.url
		## mongoDb connection
		document=collection.find_one({"cat_url":source_url})
		id1=document['_id']
		harvester_final.read_data(id1,backupi)



    #def import_stage(self,harvest_object):
	 # text_file.write('hi')
        #log.debug('In CKANHarvester import_stage')
        #if not harvest_object:
            #log.error('No harvest object received')
            #return False

        #if harvest_object.content is None:
            #self._save_object_error('Empty content for object %s' % harvest_object.id,
                    #harvest_object, 'Import')
            #return False

        #self._set_config(harvest_object.job.source.config)

        #try:
            #package_dict = json.loads(harvest_object.content)

            #if package_dict.get('type') == 'harvest':
                #log.warn('Remote dataset is a harvest source, ignoring...')
                #return True

            ## Set default tags if needed
            #default_tags = self.config.get('default_tags',[])
            #if default_tags:
                #if not 'tags' in package_dict:
                    #package_dict['tags'] = []
                #package_dict['tags'].extend([t for t in default_tags if t not in package_dict['tags']])

            #remote_groups = self.config.get('remote_groups', None)
            #if not remote_groups in ('only_local', 'create'):
                ## Ignore remote groups
                #package_dict.pop('groups', None)
            #else:
                #if not 'groups' in package_dict:
                    #package_dict['groups'] = []

                ## check if remote groups exist locally, otherwise remove
                #validated_groups = []
                #context = {'model': model, 'session': Session, 'user': 'harvest'}

                #for group_name in package_dict['groups']:
                    #try:
                        #data_dict = {'id': group_name}
                        #group = get_action('group_show')(context, data_dict)
                        #if self.api_version == 1:
                            #validated_groups.append(group['name'])
                        #else:
                            #validated_groups.append(group['id'])
                    #except NotFound, e:
                        #log.info('Group %s is not available' % group_name)
                        #if remote_groups == 'create':
                            #try:
                                #group = self._get_group(harvest_object.source.url, group_name)
                            #except:
                                #log.error('Could not get remote group %s' % group_name)
                                #continue

                            #for key in ['packages', 'created', 'users', 'groups', 'tags', 'extras', 'display_name']:
                                #group.pop(key, None)
                            #get_action('group_create')(context, group)
                            #log.info('Group %s has been newly created' % group_name)
                            #if self.api_version == 1:
                                #validated_groups.append(group['name'])
                            #else:
                                #validated_groups.append(group['id'])

                #package_dict['groups'] = validated_groups

            #context = {'model': model, 'session': Session, 'user': 'harvest'}

            ## Local harvest source organization
            #source_dataset = get_action('package_show')(context, {'id': harvest_object.source.id})
            #local_org = source_dataset.get('owner_org')

            #remote_orgs = self.config.get('remote_orgs', None)

            #if not remote_orgs in ('only_local', 'create'):
                ## Assign dataset to the source organization
                #package_dict['owner_org'] = local_org
            #else:
                #if not 'owner_org' in package_dict:
                    #package_dict['owner_org'] = None

                ## check if remote org exist locally, otherwise remove
                #validated_org = None
                #remote_org = package_dict['owner_org']

                #if remote_org:
                    #try:
                        #data_dict = {'id': remote_org}
                        #org = get_action('organization_show')(context, data_dict)
                        #validated_org = org['id']
                    #except NotFound, e:
                        #log.info('Organization %s is not available' % remote_org)
                        #if remote_orgs == 'create':
                            #try:
                                #org = self._get_group(harvest_object.source.url, remote_org)
                                #for key in ['packages', 'created', 'users', 'groups', 'tags', 'extras', 'display_name', 'type']:
                                    #org.pop(key, None)
                                #get_action('organization_create')(context, org)
                                #log.info('Organization %s has been newly created' % remote_org)
                                #validated_org = org['id']
                            #except:
                                #log.error('Could not get remote org %s' % remote_org)

                #package_dict['owner_org'] = validated_org or local_org

            ## Set default groups if needed
            #default_groups = self.config.get('default_groups', [])
            #if default_groups:
                #if not 'groups' in package_dict:
                    #package_dict['groups'] = []
                #package_dict['groups'].extend([g for g in default_groups if g not in package_dict['groups']])

            ## Find any extras whose values are not strings and try to convert
            ## them to strings, as non-string extras are not allowed anymore in
            ## CKAN 2.0.
            #for key in package_dict['extras'].keys():
                #if not isinstance(package_dict['extras'][key], basestring):
                    #try:
                        #package_dict['extras'][key] = json.dumps(
                                #package_dict['extras'][key])
                    #except TypeError:
                        ## If converting to a string fails, just delete it.
                        #del package_dict['extras'][key]

            ## Set default extras if needed
            #default_extras = self.config.get('default_extras',{})
            #if default_extras:
                #override_extras = self.config.get('override_extras',False)
                #if not 'extras' in package_dict:
                    #package_dict['extras'] = {}
                #for key,value in default_extras.iteritems():
                    #if not key in package_dict['extras'] or override_extras:
                        ## Look for replacement strings
                        #if isinstance(value,basestring):
                            #value = value.format(harvest_source_id=harvest_object.job.source.id,
                                     #harvest_source_url=harvest_object.job.source.url.strip('/'),
                                     #harvest_source_title=harvest_object.job.source.title,
                                     #harvest_job_id=harvest_object.job.id,
                                     #harvest_object_id=harvest_object.id,
                                     #dataset_id=package_dict['id'])

                        #package_dict['extras'][key] = value

            ## Clear remote url_type for resources (eg datastore, upload) as we
            ## are only creating normal resources with links to the remote ones
            #for resource in package_dict.get('resources', []):
                #resource.pop('url_type', None)

            #result = self._create_or_update_package(package_dict,harvest_object)

            #if result and self.config.get('read_only',False) == True:

                #package = model.Package.get(package_dict['id'])

                ## Clear default permissions
                #model.clear_user_roles(package)

                ## Setup harvest user as admin
                #user_name = self.config.get('user',u'harvest')
                #user = model.User.get(user_name)
                #pkg_role = model.PackageRole(package=package, user=user, role=model.Role.ADMIN)

                ## Other users can only read
                #for user_name in (u'visitor',u'logged_in'):
                    #user = model.User.get(user_name)
                    #pkg_role = model.PackageRole(package=package, user=user, role=model.Role.READER)


            #return True
        #except ValidationError,e:
            #self._save_object_error('Invalid package with GUID %s: %r' % (harvest_object.guid, e.error_dict),
                    #harvest_object, 'Import')
        #except Exception, e:
            #self._save_object_error('%r'%e,harvest_object,'Import')

