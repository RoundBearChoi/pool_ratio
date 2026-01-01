# getResults.py

import json
import os
from pathlib import Path
from typing import Dict, Any


def get_results(pool_address: str = '0xc211e1f853a898bd1302385ccde55f33a8c4b3f3'):
    print(' --- getting results --- ')
    
    pool_json = get_pool_data(pool_address)

    print('')
    print('getting pool data..')
    print(json.dumps(pool_json, indent=4))


def get_pool_data(pool_address: str) -> Dict[str, Any]:
    scriptDir = os.path.dirname(os.path.abspath(__file__))
    path = Path(scriptDir)
    jsonFiles = list(path.glob("*.json"))

    for file in jsonFiles:
        if pool_address in file.name:
            with open(file, 'r') as f:
                return json.load(f)

    raise ValueError(f'json not found: {pool_address}')


if __name__ == '__main__':
    get_results()
