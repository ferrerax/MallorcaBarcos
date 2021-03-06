# -*- coding: utf-8 -*-


import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import time
import re

#url="https://www.marinetraffic.com/en/data/?asset_type=vessels&columns=flag,shipname,photo,recognized_next_port,reported_eta,reported_destination,current_port,imo,ship_type,show_on_live_map,time_of_latest_position,lat_of_latest_position,lon_of_latest_position,notes&current_port_in|begins|ROSES|current_port_in=19814"

url="https://www.marinetraffic.com/en/data/?asset_type=vessels&columns=flag,shipname,photo,recognized_next_port,reported_eta,reported_destination,current_port,imo,ship_type,show_on_live_map,time_of_latest_position,lat_of_latest_position,lon_of_latest_position,notes&current_port_in|begins|PALMA%20DE%20MALLORCA|current_port_in=75"

driver = webdriver.Chrome()
driver.implicitly_wait(4)
first = True

def formataSortida(noms,imos,llarg):
	a = []
	for (n,i,l) in zip(noms, imos, llarg):
		link ="https://www.google.com/search?q=intext:\""+str(n)+"\" intext:"+str(i) 
		a.append({"Nom":n, "IMO":i, "Llargada en metres": l, "Link Info": link})
	return a

def obtepags():
	num = 0
	driver.get(url)
	# Acceptar les cookies
	elem = driver.find_elements_by_class_name("qc-cmp-button")
	time.sleep(2)
	for e in elem:
		if e.text == "I ACCEPT":
			#print("[X]	Acceptant Cookies...")
			e.click()
	time.sleep(4)
	elems = driver.find_elements_by_tag_name("p")
	for e in elems:
		if "of" in e.text:
			num = int(e.text.split()[1])
			print ("Tenim " + str(num*20) + " vaixells al port de Palma")
	return num

num_pag=obtepags()
num_vaixells=num_pag*20
nbarco=0
it = 0
noms=[]
imos=[]
llarg=[]
print("[+] BUSCADOR DE VAIXELLS AL PORT DE PALMA DE MALLORCA")
for p in range(0,num_pag): #Tenim obtepags numero de pagines
	driver.get(url)
	
# Acceptar les cookies
	time.sleep(2)
	elem = driver.find_elements_by_class_name("qc-cmp-button")
	for e in elem:
		if e.text == "I ACCEPT":
		#	print("[X]	Acceptant Cookies...")
			e.click()
#Itero tots els botons fins que trobo el de canviar la pàgina. No ho faig a la primera pagina
	elem = driver.find_elements_by_tag_name("button")
	#print(str(len(elem)))
	for e in elem:
	#	print(e)
		#if not first and "Next page" in e.get_attribute("title"):
		#	print("[X]	Canviant la pagina...")
		#	e.click()
		#	first=False
		#print (e.get_attribute("title"))	
		if "Next page" in e.get_attribute("title"):
			#print("[X]	Canviant a la  pagina... " + str(p+1))
			for i in range(0,p):	
				e.click()
				time.sleep(2)
				#print("Estic a la pàgina " + str(p+1))



	dlinks=[] #Links de la pagina
	elem = driver.find_elements_by_class_name("ag-cell-content-link") #Agafo els links dels noms dels barcos
	
	#print("He obtingut " + str(len(elem)) + " elements en aquesta pàgina") #Mostro la quantitat de barcos que tinc
	for e in elem:
		if "Show Details For:" in e.get_attribute("title"):
			noms.append(e.text) #Em quedo el nom del barco
			dlinks.append(e.get_attribute("href")) #Em quedo el link del barco
			#print(e.text)		# Mostro el nom del barco
	
	#print("[X]	"+str(len(dlinks))+" vaixells trobats")#Mostro el numero de barcos q he trobat
	for l in dlinks:  # per cada link que he trobat a la pàgina
		try:
			print("Processant vaixell " + str(nbarco+1) + " de " + str(num_vaixells))
			print("Nom del vaixell: " + noms[it])
			it += 1
			nbarco += 1
	#	print("Investigo " + l)
			driver.get(l)
			elem = driver.find_elements_by_class_name("qc-cmp-button")
			for e in elem:
				if e != None and e.text == "I ACCEPT":
					#print("[X]	Acceptant Cookies...")
					e.click()
			h = driver.find_element_by_tag_name("body") 
			for i in range(0,10):	# Faig scroll molt cutre
				h.send_keys(Keys.SPACE)
		
	#Intento obtenir l'IMO i llargada
			try:
				time.sleep(1)
				info = driver.find_element_by_id("imo")
				m = re.search(r'(?<=: )[0-9\-]+', info.text)
				imo = m.group(0)
				#print("			IMO: " + str(imo))
				imos.append(imo)
				info = driver.find_element_by_id("lengthOverallBreadthExtreme")
				m = re.search(r'(?<=: )[0-9\.]*', info.text)
				llargi = m.group(0)
				#print("			Llarg: " + str(llargi))
				llarg.append(llargi)
			except NoSuchElementException:
				imos.append(None)
				llarg.append(None)
				print("No info del barco")
		except e:
			break
				
print("[+] FORMATANT LA SOTIDA")
with open("./stalin.csv","w+") as fd:
	#print(fd)
	csv_columns = ["Nom","IMO","Llargada en metres","Link Info"]
	barcos = formataSortida(noms,imos,llarg)
	writer = csv.DictWriter(fd,fieldnames=csv_columns)
	writer.writeheader()
	for data in barcos:
		writer.writerow(data)
#	for l in llarg:
	#	print(noms[i]+";"+l+";https://www.google.com/search?q=intext:\""+noms[i]+"\" intext:"+imos[i])
#		fd.write(noms[i]+";"+l+";https://www.google.com/search?q=intext:\""+noms[i]+"\" intext:"+imos[i])
#		i+=1
driver.close()
#print("[+] Acabat")
