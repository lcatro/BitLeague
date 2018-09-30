
import json
import time

import bs4
import requests


btc_host = 'https://blockchain.info/rawaddr/'
eth_host = 'https://etherscan.io/txs?a='


def get_eth_transation(eth_address) :
    responed = requests.get(eth_host + eth_address)
    
    if not 200 == responed.status_code :
        return False
    
    resolver = bs4.BeautifulSoup(responed.text,'lxml')
    tree_object = resolver.find('tbody')
    record_list = tree_object.find_all('tr')
    result = []
    
    if 2 == len(record_list) :
        if 'There are no matching entries' in record_list[0].get_text().strip() :
            return []
    
    for record_index in record_list :
        data_list = record_index.find_all('td')
        tx_hash = data_list[0].find('a').get_text().strip()
        block_height = int(data_list[1].find('a').get_text().strip())
        from_address = data_list[3].find('a').get_text().strip()
        to_address = data_list[5].find('span').get_text().strip()
        value = float(data_list[6].get_text().split(' ')[0].strip())
        timetick = data_list[2].find('span').attrs['title']
        timetick = timetick[ : timetick.rfind(' ') ]
        timetick = time.strptime(timetick,'%b-%d-20%y %H:%M:%S')
        timetick = int(time.mktime(timetick))
        
        result.append({
            'tx_hash' : tx_hash ,
            'block_height' : block_height ,
            'from_address' : from_address ,
            'to_address' : to_address ,
            'value' : value ,
            'timetick' : timetick ,
        })
        
    return result

def get_btc_transation(btc_address) :
    responed = requests.get(btc_host + btc_address)
    
    if not 200 == responed.status_code :
        return False
    
    resolver = json.loads(responed.text)
    tx_list = resolver['txs']
    result = []
    
    for tx_index in tx_list :
        inputs_list = tx_index['inputs']
        
        for input_index in inputs_list :
            tx_hash = input_index['prev_out']['tx_index']
            block_height = int(tx_index['block_height'])
            from_address = input_index['prev_out']['addr']
            to_address = btc_address
            value = float(input_index['prev_out']['value']) / 10 ** 8
            timetick = int(tx_index['time'])
            
            result.append({
                'tx_hash' : tx_hash ,
                'block_height' : block_height ,
                'from_address' : from_address ,
                'to_address' : to_address ,
                'value' : value ,
                'timetick' : timetick
            })
    
    return result


if __name__ == '__main__' :
    print get_eth_transation('0x957cD4Ff9b3894FC78b5134A8DC72b032fFbC464')
    #print get_eth_transation('0x453343839526ff5156ea3bd1debf6cecbd196b87')
    #print get_btc_transation('1EzwoHtiXB4iFwedPr49iywjZn2nnekhoj')
    
