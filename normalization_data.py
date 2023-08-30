import math
from core import *

combine_data = read_write_file_json('20230821.json', 'r', None, None)
token_img_url = []
protocol_img_url = []
blank_address = []
wallets_address = []
count = 0
for item in combine_data:
    count += 1
    user_address = item['user_address']
    networth = item["networth"]
    top_tokens = item["top_tokens"]
    top_protocols = item["top_protocols"]

    if user_address:
        wallets_address.append(user_address)
    else:
        new_item = {
            'rank': count,
            'page': math.floor(count/20),
            'row': count % 20

        }
        blank_address.append(new_item)
    
    if top_tokens:
        tokenImgUrl = [el["token_img_url"] for el in top_tokens]
        token_img_url.extend(tokenImgUrl)

    if top_protocols:
        protocolImgUrl = [el['protocol_img_url'] for el in top_protocols]
        protocol_img_url.extend(protocolImgUrl)

set_wallets_address = set((wallets_address))
list_wallets_address = list((set_wallets_address))

set_protocol_img_url = set((protocol_img_url))
list_protocol_img_url = list((set_protocol_img_url))

set_token_img_url = set((token_img_url))
list_token_img_url = list((set_token_img_url))

transform_and_save_json_file(None, 'WalletsAddress.json', 'w', list_wallets_address, None)
transform_and_save_json_file(None, 'BlankAddress.json', 'w', blank_address, None)
transform_and_save_json_file(None, 'ProtocolsImgUrl.json', 'w', list_protocol_img_url, None)
transform_and_save_json_file(None, 'TokensImgUrl.json', 'w', list_token_img_url, None)

print(f'List Address: {len(list_wallets_address)}')
print(f'List Blank Address: {len(blank_address)}')
print(f' List Tokens Image Url: {len(list_token_img_url)}')
print(f'List Protocols Image Url: {len(list_protocol_img_url)}')





