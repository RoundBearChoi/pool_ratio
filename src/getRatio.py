# getRatio.py

import requests
import json
import os


def get_pool_ratio(pool_address: str, network: str = 'base'):
    pool_address = pool_address.lower()
    url = f'https://api.geckoterminal.com/api/v2/networks/{network}/pools/{pool_address}'
    
    headers = {
        'accept': 'application/json'
    }

    print('')
    print('connecting to geckoterminal..')

    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f'Error fetching data: HTTP {response.status_code}')
        print(response.text)
        return
    
    json_data = response.json()
   
    print('connected..')
    print('')

    print(f' --- getting data on {pool_address} --- ')

    try:
        attributes = json_data['data']['attributes']
        
        # extract pool name (clean version without fee)
        pool_name = attributes['pool_name']
        tokens = pool_name.split(' / ')
        base_token = tokens[0].strip()
        quote_token = tokens[1].strip()
       
        # get tvl and daily volume
        tvl_usd = float(attributes['reserve_in_usd'])
        volume_24h_usd = float(attributes['volume_usd']['h24'])
        
        print('')
        print(f'tvl ≈ ${tvl_usd:,.2f} USD')
        print(f'24h trading volume ≈ ${volume_24h_usd:,.2f} USD')

        # prices (returned as strings, convert to float)
        base_in_quote = float(attributes['base_token_price_quote_token'])
        quote_in_base = float(attributes['quote_token_price_base_token'])
        
        print('') 
        print(f'pool: {base_token}/{quote_token} on {network.upper()}')
        print(f'inverse: 1 {quote_token} = {quote_in_base:.12f} {base_token}')
        print(f'ratio ({base_token} : {quote_token}) = 1 : {base_in_quote:.12f}')
        print(f'ratio ({quote_token} : {base_token}) = {quote_in_base:.12f} : 1')
        
        # usd prices
        base_usd = float(attributes['base_token_price_usd'])
        quote_usd = float(attributes['quote_token_price_usd'])
        print('')
        print(f'1 {base_token} ≈ ${base_usd:.2f}')
        print(f'1 {quote_token} ≈ ${quote_usd:.2f}')
        
        # save data to json
        data_to_save = {
            "pool_address": pool_address,
            "network": network,
            "pool_name": pool_name,
            "base_token": base_token,
            "quote_token": quote_token,
            "tvl_usd": tvl_usd,
            "volume_24h_usd": volume_24h_usd,
            "base_token_price_quote_token": base_in_quote,  # how many quote tokens per 1 base token
            "quote_token_price_base_token": quote_in_base,  # how many base tokens per 1 quote token
            "base_token_price_usd": base_usd,
            "quote_token_price_usd": quote_usd
        }
        
        # filename based on pool address
        fileName = f'{pool_address}_{base_token}_{quote_token}_data.json'
        fileName = fileName.lower()
        scriptDir = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(scriptDir, fileName)

        with open(filePath, 'w') as f:
            json.dump(data_to_save, f, indent=4)
        
        print('')
        print(f'data saved to {filePath}')


    except KeyError as e:
        print('unexpected API response structure. KeyError:', e)
        print('raw data:')
        print(json_data)
    except Exception as e:
        print(f'error: {e}')


if __name__ == '__main__':
    pool_address = '0xC211e1f853A898Bd1302385CCdE55f33a8c4B3f3'
    get_pool_ratio(pool_address)
