import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np

import subprocess

class Scraping:
    def __init__(self,pathname: str):
        self.colnames = ['Name','Smiles','Inchi','CasRN','MeltingPoint',
                         'BoilingPoint','WaterSolubility_mg_mL','LogP','Ref',
                         'ppm_exp','n_peaks_exp','multiplicity_exp','n_Hs_exp','atom_number_exp','peak_centers_exp','ExperimentalConditions',
                         'ppm_pred','n_peaks_pred','multiplicity_pred','n_Hs_pred','atom_number_pred','peak_centers_pred','predCondition']
        self.df = pd.DataFrame(columns=self.colnames)
        self.pathname = pathname
        self.txtfile = self.df.to_csv(index=False, sep=';',header=True).strip()
        
        subprocess.run(f'echo "{self.txtfile}" >> {self.pathname}', shell=True)
    
    def fit(self, initialID:int = 0, finalID:int = 2, time2wait:int = 4):
        links = self._generateListOfLinks(initialID,finalID)
        for link in links:     
            #print(link)
            html = requests.get(link)
            soupcontent = BeautifulSoup(html.content, 'html.parser')
            
            # Se der erro aqui é pq a pagina nao tem informação
            try:
                #Scraping do nome,smiles,inchi e casrn
                name,smiles,inchi,casrn = self._getSmilesAndInchi(souphtml=soupcontent)
            except:
                continue
            
            ### Pegando as propriedades fisicoquimicas
            mp,bp,solub,logp = self._getPQpropierties(souphtml=soupcontent)
            
            ### Pegando a lista de ppm e multiplicidades
            linksnmr = self.__getNMRInfo(souphtml=soupcontent)
            #print(linksnmr)
            nmrdatas = self._getNMRdata(infolink=linksnmr, time2wait = time2wait)
            #print(nmrdatas['ExperimentalNMRDATA'],nmrdatas)
            #experimental nmr
            if nmrdatas['ExperimentalNMRDATA'] == None:
                ppm_exp = np.nan
                n_peaks_exp = np.nan
                multiplicity_exp = np.nan
                n_Hs_exp = np.nan
                atom_number_exp = np.nan
                peak_centers_exp = np.nan
                exp_condition = np.nan
            else:                    
                ppm_exp = nmrdatas['ExperimentalNMRDATA'][0][0]
                n_peaks_exp = nmrdatas['ExperimentalNMRDATA'][0][1]
                multiplicity_exp = nmrdatas['ExperimentalNMRDATA'][0][2]
                n_Hs_exp = nmrdatas['ExperimentalNMRDATA'][0][3]
                atom_number_exp = nmrdatas['ExperimentalNMRDATA'][0][4]
                peak_centers_exp = nmrdatas['ExperimentalNMRDATA'][0][5]
                exp_condition = nmrdatas['ExperimentalNMRDATA'][1]
                
            #predicted nmr
            if nmrdatas['PredictedNMRDATA'] == None:
                ppm_pred = np.nan
                n_peaks_pred = np.nan
                multiplicity_pred = np.nan
                n_Hs_pred = np.nan
                atom_number_pred = np.nan
                peak_centers_pred = np.nan
                pred_condition = np.nan
            else:    
                ppm_pred = nmrdatas['PredictedNMRDATA'][0][0]
                n_peaks_pred = nmrdatas['PredictedNMRDATA'][0][1]
                multiplicity_pred = nmrdatas['PredictedNMRDATA'][0][2]
                n_Hs_pred = nmrdatas['PredictedNMRDATA'][0][3]
                atom_number_pred = nmrdatas['PredictedNMRDATA'][0][4]
                peak_centers_pred = nmrdatas['PredictedNMRDATA'][0][5]
                pred_condition = nmrdatas['PredictedNMRDATA'][1]
            
            #Criando o dataframe final
            listOfData = [name,smiles,inchi,casrn,mp,bp,solub,logp,link,
                          ppm_exp,n_peaks_exp,multiplicity_exp,n_Hs_exp,atom_number_exp,peak_centers_exp,exp_condition,
                          ppm_pred,n_peaks_pred,multiplicity_pred,n_Hs_pred,atom_number_pred,peak_centers_pred,pred_condition] #lista de todos os dados extraídos
            
            newdf = pd.DataFrame([listOfData],columns=self.colnames)
            self.df = pd.concat([self.df,newdf],axis=0).reset_index(drop=True)
            
            txtdata2file = newdf.to_csv(index=False, sep=';',header=False).strip()        
            subprocess.run(f'echo "{txtdata2file}" >> {self.pathname}', shell=True)
            
        return self.df            
            
    def _getPQpropierties(self,souphtml: BeautifulSoup):
        # Pegando propriedades fisico quimicas
        pqprop_tags = souphtml.find('tr', id="physical_properties").find_next_sibling("tr").find_next_sibling("tr")
        values = pqprop_tags.find_all('tbody')[0].find_all("tr")
        allprops = [tr.find("td").find_next_sibling("td").get_text() for tr in values]
        
        #Melting point, Boiling Point, Water Solubility, LogP
        return allprops[0],allprops[1],allprops[2],allprops[3]
    
    def _getSmilesAndInchi(self,souphtml: BeautifulSoup):
        #Getting name, smiles and inchi

        table = souphtml.find("table", class_="content-table table table-condensed table-bordered").find_all("tbody")[0]

        smiles = []
        inchi = []
        name = []
        casrn = []
        for row in table('tr'):
            th = row.find('th')

            if th and th.text == 'SMILES':
                smi = row.find_all("div")[0].contents[0]
                smiles.append(smi)
            if th and th.text == 'InChI Identifier':
                inchik = row.find_all("div")[0].contents[0]
                inchi.append(inchik)
            if th and th.text == 'Common Name':
                molname = row.find_all("td")[0].get_text()
                name.append(molname)
            if th and th.text == 'CAS Registry Number':
                molcasrn = row.find_all("td")[0].get_text()
                casrn.append(molcasrn)

        return name[0],smiles[0],inchi[0],casrn[0]   
        
    def _generateListOfLinks(self,initialID:int, finalID:int):
        links = []
        for id_ in range(initialID, finalID):
            
            qtd_zeros2complete = 7-len(str(id_))
            hmdb_id = 'HMDB'+'0'*qtd_zeros2complete+str(id_)
            link = 'https://hmdb.ca/metabolites/'+hmdb_id
            links.append(link)
        return links
    
    def _getNMRdata(self, infolink:list, time2wait:int = 4):

        dataextracted = {'ExperimentalNMRDATA':None, 'PredictedNMRDATA':None}

        if infolink['ExperimentalNMR'] != None:
            try:
                link_ = list(infolink['ExperimentalNMR'])[0]

                options = webdriver.ChromeOptions()
                options.add_argument("javascript.enabled=true")
                options.add_argument('--headless')  # Executar em modo headless (sem interface gráfica)
                with webdriver.Chrome(options=options) as driver:
                    driver.get(link_)
                    # Aguarde o carregamento da página (ajuste o tempo se necessário)
                    #WebDriverWait(driver, 30).until(EC.url_contains((link_)))
                    #driver.implicitly_wait(60) 
                    time.sleep(time2wait)
                    #table = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "specdb-nmr-one-d-c  show-a")))
                    # Obtenha o HTML da página após o JavaScript ter sido executado
                    soup = BeautifulSoup(driver.page_source, 'html.parser')

                table = soup.find("table", class_="jsv-assignment-table").find("tbody")

                # Inicializar listas vazias para cada coluna
                cluster_midpoints = []
                no_peaks = []
                coupling_types = []
                no_hs = []
                atom_nos = []
                peak_centers = []

                # Iterar sobre cada linha <tr> na tabela
                for tr in table.select('tbody tr'):
                    tds = tr.find_all('td')

                    # Adicionar conteúdo das células às listas
                    cluster_midpoints.append(float(tds[1].text.strip()))
                    no_peaks.append(int(tds[2].text.strip()))
                    coupling_types.append(tds[3].text.strip())
                    no_hs.append(int(tds[4].text.strip()))

                    # Para os números dos átomos e os centros de pico, temos que lidar com múltiplas entradas dentro de uma única célula
                    atom_nos.append([int(div.text) for div in tds[5].find_all('div', class_='jsv-badge')])
                    peak_centers.append([float(span.text) for span in tds[7].find_all('span', class_='jsv-badge')])

                dataextracted['ExperimentalNMRDATA'] = [[cluster_midpoints,no_peaks,coupling_types,no_hs,atom_nos,peak_centers],list(infolink['ExperimentalNMR'])[1]]
            except:        
                pass

        if infolink['PredictedNMR_500Hz'] != None:
            try:
                link_ = list(infolink['PredictedNMR_500Hz'])[0]
                options = webdriver.ChromeOptions()
                options.add_argument("javascript.enabled=true")
                options.add_argument('--headless')  # Executar em modo headless (sem interface gráfica)
                with webdriver.Chrome(options=options) as driver:
                    driver.get(link_)
                    # Aguarde o carregamento da página (ajuste o tempo se necessário)
                    #WebDriverWait(driver, 30).until(EC.url_contains((link_)))
                    #driver.implicitly_wait(60) 
                    time.sleep(time2wait)
                    #table = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "specdb-nmr-one-d-c  show-a")))
                    # Obtenha o HTML da página após o JavaScript ter sido executado
                    soup = BeautifulSoup(driver.page_source, 'html.parser')

                table = soup.find("table", class_="jsv-assignment-table").find("tbody")

                # Inicializar listas vazias para cada coluna
                cluster_midpoints = []
                no_peaks = []
                coupling_types = []
                no_hs = []
                atom_nos = []
                peak_centers = []

                # Iterar sobre cada linha <tr> na tabela
                for tr in table.select('tbody tr'):
                    tds = tr.find_all('td')

                    # Adicionar conteúdo das células às listas
                    cluster_midpoints.append(float(tds[1].text.strip()))
                    no_peaks.append(int(tds[2].text.strip()))
                    coupling_types.append(tds[3].text.strip())
                    no_hs.append(int(tds[4].text.strip()))

                    # Para os números dos átomos e os centros de pico, temos que lidar com múltiplas entradas dentro de uma única célula
                    atom_nos.append([int(div.text) for div in tds[5].find_all('div', class_='jsv-badge')])
                    peak_centers.append([float(span.text) for span in tds[7].find_all('span', class_='jsv-badge')])

                dataextracted['PredictedNMRDATA'] = [[cluster_midpoints,no_peaks,coupling_types,no_hs,atom_nos,peak_centers],list(infolink['PredictedNMR_500Hz'])[1]]
            except:
                pass

        return dataextracted    
    
    def __getNMRInfo(self,souphtml: BeautifulSoup):
        #pegando espectros

        tableinformation = souphtml.find_all('table', class_="table-inner nmr-table")
        #hasExperimental = tableinformation[0].find_all(string='Experimental 1D NMR')
        #hasPredicted = tableinformation[0].find_all(string=re.compile(r'^H.*?1D, 500 MHz, D$'))
        label_link = {'ExperimentalNMR':None,'PredictedNMR_500Hz':None}

        try:
            allspectra_tags = tableinformation[0].find_all("tbody")[0].find_all("tr")

            for tr in allspectra_tags:
                #if tr.find('td').get_text() == 'Experimental 1D NMR': #pega o ultimo dado experimental, 13C sempre fica deopis do 1H
                if tr.find('td').get_text() == 'Experimental 1D NMR' and '1H NMR Spectrum' in [tds.get_text() for tds in tr.find_all('td')][1]:
                    label_experimental = [tds.get_text() for tds in tr.find_all('td')][1]

                    linktagEXP = tr.find('td').find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').find('a')['href']
                    link2nmrEXP = 'https://hmdb.ca'+linktagEXP

                    label_link['ExperimentalNMR'] = [link2nmrEXP,label_experimental]

                if '1H NMR Spectrum (1D, 500 MHz' in tr.find('td').find_next_sibling("td").get_text() and 'predicted)' in tr.find('td').find_next_sibling("td").get_text():

                    label_predicted = tr.find('td').find_next_sibling("td").get_text()

                    linktagPRED = tr.find('td').find_next_sibling("td").find_next_sibling("td").find_next_sibling("td").find_next_sibling("td").find('a')['href']
                    link2nmrPRED = 'https://hmdb.ca'+linktagPRED

                    label_link['PredictedNMR_500Hz'] = [link2nmrPRED,label_predicted]
        except:
            pass

        return label_link

            
