import requests
from bs4 import BeautifulSoup
import urllib
import os, http.cookiejar, urllib.request
from urllib.request import urlopen
import re
import zipfile
from pathlib import Path
import os
import csv
from io import TextIOWrapper
import numpy as np
import pickle
import gzip


class DataDownloader:
    """Zajistuje stahovani dat o nehodach z  https://ehw.fit.vutbr.cz/izv/"""
    URL = None
    folder = 'data'
    cache_filename="data_{}.pkl.gz"
    list_of_links =list()
    downloaded = False
    data = tuple((list(['region', 'p1', 'p36', 'p37', 'p2a', 'weekday(p2a)', 'p2b', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11', 'p12', 'p13a', 'p13b', 'p13c', 'p14', 'p15', 'p16', 'p17', 'p18', 'p19', 'p20', 'p21', 'p22', 'p23', 'p24', 'p27', 'p28', 'p34', 'p35', 'p39', 'p44', 'p45a', 'p47', 'p48a', 'p49', 'p50a', 'p50b', 'p51', 'p52', 'p53', 'p55a', 'p57', 'p58', 'a', 'b', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'n', 'o', 'p', 'q', 'r', 's', 't', 'p5a', 'p20', 'p30', 'p31', 'p32']),\
     list()))
    regions_in_memory = dict()

    codes_for_regions = {'00':'PHA', '01':'STC', '02':'JHC', '03':'PLK', '04':'ULK', '05':'HKK', '06':'JHM', '07':'MSK', '14':'OLK', '15':'ZLK', '16':'VYS', '17':'PAK', '18':'LBK', '19':'KVK'}#chybi chodci



    def __init__(self, url='https://ehw.fit.vutbr.cz/izv/', folder='data', cache_filename="data_{}.pkl.gz"):
        """Nastavi atributy tridy a z url ziska odkazy na zadane predmety
        
        Keyword arguments:
        url -- web pro ziskani dat  (default https://ehw.fit.vutbr.cz/izv/)
        folder -- slozka kam se stahnou zipy z webu a ulozi cache
        cache_filename -- format nazvu cache souboru
        """
        #list_of_np_arrays = list(np.array(dtype = np.int64))
        #self.data = tuple((list_of_strings, list_of_np_arrays))
        self.URL = url
        self.folder = folder
        self.cache_filename = cache_filename
        with requests.Session() as s:
            headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"}
            page = s.get(url, headers=headers)
            soup = BeautifulSoup(page.text, 'html.parser')

            #ziskani odkazu na posledni zip soubor z kazdeho roku
            last_link = None
            year_before = "0"
            current_link = "none"
            last_link = None
            for link in soup.find_all('a', text='ZIP'):
                year_now = re.split(r'\.|-|[a-z]', link['href'])[-5]
                
                if year_now != year_before:
                    if last_link != None:
                        self.list_of_links.append(last_link)
                
                    year_before = year_now
                
                last_link = link['href']
            self.list_of_links.append(last_link)

    def regionCodesToFileName(self, region):
        """prevede kod regionu na jmeno souboru, ve kterem jsou data pro dany region"""
        return list(self.codes_for_regions.keys())[list(self.codes_for_regions.values()).index(region)]
        


    def listToArray(self, list_of_lists):
        """ Procisti data a prevede je do listu np array spravnych dtype"""
        dtypes_var = np.asarray(('U3','u8','u8','U10','M','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','u8','f8','f8','f8','f8','f8','f8','f8','U16','U50','U50','U16','U18','U16','U20', 'U16','U25','U17','U16','U23','u8'))
        list_of_np_arrays = list()
        for data, dtype in zip(list_of_lists, dtypes_var):
            if dtype in ('u8', 'f8'):
                if dtype in ('f8'):
                        data[ii] = data[ii].replace(',','.')
                for ii in range(len(data)):
                    if data[ii] == '':
                        data[ii] = '-1'
                    elif not data[ii].isnumeric():
                        data[ii] = '-1'

            list_of_np_arrays.append(np.asarray(data, dtype = dtype))
        return list_of_np_arrays
        


    def download_data(self):
        """ Stahne zip soubory z linku ziskanych v konstruktoru a ulozi je do folder"""
        Path(self.folder).mkdir(parents=True, exist_ok=True)
        
        with requests.Session() as s:
            headers = headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"}
            s.get(self.URL, headers=headers)
        
            for link in self.list_of_links:
                #stazeni jednoho zipu
                r = s.get(self.URL+link, allow_redirects=True)
                fileName = re.split(r'\.|-|[a-z]', link)[-5]
                open(self.folder +'/' + fileName + '.zip', 'wb').write(r.content)
                print(fileName +'.zip' + ' downloaded')

                        
    def parse_region_data(self, region):
        """zpracuje data (pro dany region) ze zazipovanych csv do listu np array spravneho dtype, ulozi je do atributu regions_in_memory, do cache souboru a vrati jej """
        temp_list_of_data = [[] for i in range(65)]
        try:
            for link in self.list_of_links:
                fileName = re.split(r'\.|-|[a-z]', link)[-5] #zip soubor (bez pripony a bez cesty k souboru)
                region_csv_file = self.regionCodesToFileName(region)
                #rozzipovani a vlozeni dat do pythonich listu
                with zipfile.ZipFile(self.folder +'/' + fileName + '.zip', 'r') as zf:
                    with zf.open(region_csv_file + '.csv','r',) as f: #otevreni konkretniho csv
                        f = TextIOWrapper(f, 'windows-1250')
                        dialect = csv.Sniffer().sniff(f.read(1024))
                        f.seek(0)
                        for row in csv.reader(f, dialect):
                            temp_list_of_data[0].append(region)
                            for index, data in enumerate(row):
                                temp_list_of_data[index + 1].append(data)

            #pretypovani dat a ulozeni do listu z numpy array
            np_arrays_for_region = self.listToArray(temp_list_of_data)


            #ulozeni a vraceni listu np arraye vsude kde je potreba
            self.regions_in_memory.update({region:np_arrays_for_region})
            
            with gzip.open(self.folder + '/' + self.cache_filename.format(region), 'wb') as f:
                pickle.dump(np_arrays_for_region, f)
            return np_arrays_for_region

        except FileNotFoundError:
            self.download_data()
            return self.parse_region_data(region)

    def get_list(self, regions = None):
        """Zavola parse_region_data pro kazdy z regionu v argumentu, neni-li zadan zadny region zpracuji se vsechny, vraci tuple(list[str], list[np.ndarray])"""
        if regions == None:
            regions = list(self.codes_for_regions.values())

        list_of_lists_of_np_arrays = list()
        for region in regions:
            if region in list(self.regions_in_memory.keys()):
                list_of_lists_of_np_arrays.append(self.regions_in_memory[region])

            elif os.path.exists(self.folder + '/' + self.cache_filename.format(region)):
                with gzip.open(self.folder + '/' + self.cache_filename.format(region), 'rb') as f:
                    list_of_lists_of_np_arrays.append(pickle.load(f))

            else:
                list_of_lists_of_np_arrays.append(self.parse_region_data(region))

        #spojeni jednotlivych regionu
        temp_list_of_data = [[] for i in range(65)]
        for list_of_np_arrays in list_of_lists_of_np_arrays:
            for index, np_array in enumerate(list_of_np_arrays):
                temp_list_of_data[index].append(np_array)

        data = list()

        for index, temp in enumerate(temp_list_of_data):
            data.append(np.concatenate(temp))
        
        return tuple((list(['region', 'p1', 'p36', 'p37', 'p2a', 'weekday(p2a)', 'p2b', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11', 'p12', 'p13a', 'p13b', 'p13c', 'p14', 'p15', 'p16', 'p17', 'p18', 'p19', 'p20', 'p21', 'p22', 'p23', 'p24', 'p27', 'p28', 'p34', 'p35', 'p39', 'p44', 'p45a', 'p47', 'p48a', 'p49', 'p50a', 'p50b', 'p51', 'p52', 'p53', 'p55a', 'p57', 'p58', 'a', 'b', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'n', 'o', 'p', 'q', 'r', 's', 't', 'p5a', 'p20', 'p30', 'p31', 'p32']),\
     data))


if __name__ == "__main__":
    downloader = DataDownloader()
    data = downloader.get_list(regions=['PHA', 'STC', 'JHC'])
    print('Kraje: ', ['PHA', 'STC', 'JHC'], '\nPocet sloupcu: ', len(data[1]), '\nPocet zaznamu: ', len(data[1][0]))