from bs4 import BeautifulSoup
import urllib2
import requests
from xml.dom.minidom import parseString
import re
import difflib
import json
import logging
import SaveLabels
import pymongo
import harvester_final
import AddNoLabelToJson
import AddLabelToJson
import AddLinkToJson
import hashlib
import AddToCkan
import time
import datetime
import uuid
import configparser

##read from development.ini file all the required parameters
config = configparser.ConfigParser()
config.read('/var/local/ckan/default/pyenv/src/ckan/development.ini')
html_harvester_log_file_path=config['ckan:odm_extensions']['html_harvester_log_file_path']
backup_file_path=config['ckan:odm_extensions']['backup_file_path']
mongoclient=config['ckan:odm_extensions']['mongoclient']
mongoport=config['ckan:odm_extensions']['mongoport']


def ProcedureWithNext(soup1,dataset_keyword,dataset_keyword1,mainurl,text_file,ckanjason,commands,ckannotes,ckanlicense,ckanresource,ckantags,ckanauthor_email,ckanauthor,j,label,k,a_link,
			  links,type1,jason,db1,endpoint,url,i,afterid,step,ckantitle,ckandate_updated,ckanExtrasCategory,ckanExtrasFrequency,ckanExtrasLanguage,ckanMaintainer,ckandate_released
			  ,ckancountry,ckantemporalcoverage,ckanorganization,ckanmaintainer_email,ckanstate,ckancity,ids):
  soup1=endpoint
  xtras=[]
  xtras1=[]
  LinkCounter=0
  LastLinkCounter=0
## endpoint check
  #soupmatching=""
  harvested_pages=[]
  harvested_urls=[]
  counter=0
  while endpoint in soup1:

	  try:
		  url1=str(url)+str(i)+str(afterid)
		 
		  print(url1)
		  r  = requests.get(url1)

		  data = r.text
		  soup = BeautifulSoup(data)
		  soup1=str(soup)
		  
		  
		  h=0
		  found=False
		  while h<len(harvested_pages):
			 string_matching=difflib.SequenceMatcher(None,soup1,str(harvested_pages[h])).ratio()
			 #print("--------------------------->"+str(string_matching)+'\n')
			 print("string_matching: "+str(string_matching))
		 	 if string_matching>=0.994 and i>1:
				print('Harvest procedure finished..')
				text_file1 = open(str(backup_file_path),"w")
				text_file1.write("")
				text_file1.close()
				found=True
				
			 h+=1
		  if found==True:break
		 # soupmatching=soup1
		  harvested_pages.append(soup1)

		  if len(harvested_pages)>2:
			harvested_pages.pop(1)

		  for link in soup.find_all('a'):

			  
#--list of non label data
			  try:
				  ahref=str(link.get('href').encode('utf-8'))

			  except :
				
				text_file.write('  UnicodeError in link  ')
				print(ahref)
				ahref=str(link.get('href'))

			  Pointer=0

			  if ("www" in ahref) or ("http" in ahref):
				if (dataset_keyword in ahref )or((dataset_keyword1 in ahref )):
					Pointer=1
			  else:
				if (ahref.startswith(dataset_keyword) )or(ahref.startswith(dataset_keyword1)):
					Pointer=1
			  if Pointer==1:
				  LastLinkCounter=1
				 

				
				  if 'http' not in str(ahref):
					if mainurl[-1]=='/' or dataset_keyword[0]=='/':
						url2=mainurl+ahref
					else:
						url2=mainurl+'/'+ahref
				  else: url2=ahref

				  if url2 not in harvested_urls:

					  text_file.write('\n'+'try to open:  '+str(url2)+'\n')
					  
					  print(str(url2))
					  harvested_urls.append(url2)
					  text_file.write('\n')
					  text_file.write("ahref: "+str(url2))

					  ckanjason=ckanjason+"'url':"+"'"+str(url2)+"'"+","
					  text_file.write('\n')
					  text_file.write('\n')

					  try:
					  	r2  = requests.get(url2)
						data2 = r2.text
					  except: data2=''
					  


					  soup2 = BeautifulSoup(data2)

					  counterl=0

				  #--#--- for non label data
					  ckanjason,xtras1=AddNoLabelToJson.AddToJson(commands,counterl,ckannotes,ckanlicense,ckanresource,ckantags,ckanauthor_email,ckanauthor,soup2,text_file,ckanjason,ckantitle,ckandate_updated
					  ,ckanExtrasCategory,ckanExtrasFrequency,ckanExtrasLanguage,ckanMaintainer,ckandate_released,ckancountry,ckantemporalcoverage,ckanorganization,ckanmaintainer_email,
ckanstate,ckancity)

					  counterl=0
					  title=soup2.find_all('title')
					  text_file.write(str(title))
					  title2=str(title)
					  text_file.write(str("Title: "+title2.replace('[<title>','').replace(']','').replace("'","").replace('"','').replace('</title>','').strip()))
	    			  
					  if ckantitle=="":

						title2=title2[0:title2.find('|')]
						ckanjason=ckanjason+"'title':"+'"'+str(title2.replace('[<title>','').replace(']','').replace('|','').replace('</title>','').replace("'","").replace('"','').strip())+'"'+","
						ckanjason=ckanjason+"'name':"+"'"+str(hashlib.md5(title2.replace('[<title>','').replace(']','').replace('|','').replace('</title>','')).hexdigest())+"'"+","

					  ckanjason=ckanjason+"'metadata_created':"+"'"+str(datetime.datetime.now())+"',"+"'catalogue_url':"+"'"+str(mainurl)+"',"+"'platform':'html',"
				  #--- for label data:

					  soup3=soup2.findAll(text=True)
					 # print(label)
					  #while j<len(label):
					#	  while k<len(soup3):
					#		  if label[j] in soup3[k]:
					#			  ##added 18/7/2014
					#			  string_matching=difflib.SequenceMatcher(None, label[j].encode('utf-8'),soup3[k].encode('utf-8')).ratio()
					#			  if string_matching>0.8:
					#				label[j]=soup3[k].encode('utf-8')
					#		  k=k+1
					#	  k=0
					#	  j=j+1
					 # j=0
					 # print("--DDDD_____>>>>>>"+str(label))

				  #for label data

					  ckanjason=AddLabelToJson.AddToJson(soup3,label,j,ckannotes,ckanlicense,ckanresource,ckantags,ckanauthor_email,ckanauthor,text_file,ckanjason,a_link,ckandate_updated,ckanExtrasCategory
					  ,ckanExtrasFrequency,ckanExtrasLanguage,ckanMaintainer,ckandate_released,xtras1,ckancountry,ckantemporalcoverage,ckanorganization,ckanmaintainer_email,
ckanstate,ckancity)

					  j=0


					  #--- links searching

					  while j<len(links):
						  while k<len(soup3):
							  if links[j] in soup3[k]:

								  links[j]=soup3[k]
							  k=k+1
						  k=0
						  j=j+1
					  j=0

				  # Add links to json

					  ckanjason=AddLinkToJson.AddToJson(links,soup3,ckannotes,ckanlicense,ckanresource,ckantags,ckanauthor_email,ckanauthor,text_file,ckanjason,j,type1,mainurl)

					  j=0

					  #-- store metadata to database

					 
					  text_file.write('\n'+'\n'+'ckanjason: '+str(ckanjason.rstrip(','))+'}')
					  print(('\n'+'\n'+'ckanjason: '+str(ckanjason.rstrip(','))+'}'))
					  json2=jason.rstrip(',')+'}'
					  ckanjson3=ckanjason.rstrip(',')+'}'

					  ckanjsonWithoutTags=ckanjson3.replace(ckanjson3[ckanjson3.find("'tags':[{")-1:ckanjson3.find("}]")+2],'')


					  

					  ckanjson1='ckanjson2='+str(ckanjson3)

					  ckanjsonWithoutTags1='ckanjsonWithoutTags2='+str(ckanjsonWithoutTags)
					  
					  try:

						exec(ckanjson1)					
						if 'author' in ckanjson2.keys() or 'notes' in ckanjson2.keys() or 'license_id' in ckanjson2.keys() or 'tags' in ckanjson2.keys() or 'author_email' in ckanjson2.keys() or 'maintainer_email' in ckanjson2.keys():
							try:
							  AddToCkan.AddtoCkan(ckanjson2)
							  temp_id=str(uuid.uuid3(uuid.NAMESPACE_OID, str(url2)))
							  ckanjson2.update({'id':str(temp_id)})
							  counter+=1
							  ## check if dataset exists in mongodb
							  if temp_id not in ids:
							  	db1.save(ckanjson2)
							  time.sleep(0)
							  print("counter----> "+str(counter))

						  #jason="{"
							except urllib2.HTTPError, e:
							  text_file.write("DB_ERROR")

							  try:
								# if tags are a mess try to store the json without tags!!
								try:
									exec(ckanjsonWithoutTags1)
								except:
									ckanjsonWithoutTags2=""
								try:

								  AddToCkan.AddtoCkan(ckanjsonWithoutTags2)
								  temp_id=str(uuid.uuid3(uuid.NAMESPACE_OID, str(url2)))
								  ckanjsonWithoutTags2.update({'id':str(temp_id)})

								  ## check if dataset exists in mongodb
								  if temp_id not in ids:
								  	db1.save(ckanjsonWithoutTags2)
								 
							
						
								except urllib2.HTTPError, e:
								  j+=1
								  text_file.write("DB_FATAL_ERROR")

							  except SyntaxError:
								  j+=1
								  text_file.write("SYNTAX_ERROR1")
					  except SyntaxError:
						
						k+=1
						text_file.write("SYNTAX_ERROR")

					  ckanjason="{"
					 # text_file1.write('\n'+str(i))
					  text_file1 = open(str(backup_file_path), "w")
					  text_file1.write(str(url)+'\n'+str(i))
					  text_file1.close()
	  except urllib2.HTTPError, e:
		  
		  text_file.write("404 ERROR")
		  #jason="{"
		  print('i: ='+str(+i))
	  if LastLinkCounter==1:
		i=i+step
		LastLinkCounter=0
		
		LinkCounter=0
	  else:
		if LinkCounter<=3:
		  LastLinkCounter=0
		  i=i+step
		  LinkCounter+=1
		else:
		  text_file1 = open(str(backup_file_path), "w")
		  text_file1.write("")
		  text_file1.close()
		  break
  
  harvested_pages[:]=[]
  harvested_urls[:]=[]
  
