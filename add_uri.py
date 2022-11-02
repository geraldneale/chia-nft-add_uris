import requests
import urllib3
import json
import time
import datetime
import subprocess
urllib3.disable_warnings()

#node connection and wallet settings
cert = ('/home/gneale/.chia/mainnet/config/ssl/wallet/private_wallet.crt', '/home/gneale/.chia/mainnet/config/ssl/wallet/private_wallet.key')
headers = {'Content-Type': 'application/json'}
fprint = "4270401300"
wallet_id = "9"

#using RPC count the number of nfts in this fingerprint and wallet id, and then make a key->value pair from the nftid->coin_id
def create_nfts_dict():    
    url = "https://localhost:9256/nft_get_nfts"
    data = {"wallet_id" : wallet_id}    
    response = json.loads(requests.post(url, json=data, headers=headers, cert=cert, verify=False).text)
    json_str = json.dumps(response, indent=4, sort_keys=True)
    nfts = json.loads(json_str)
    upper_limit = len(nfts['nft_list'])
    nfts_dict = {}
    for nft_number in range(1,upper_limit):
        #print(nft_number)
        nft_url, nft_coinid = nfts['nft_list'][nft_number]['data_uris'][0],nfts['nft_list'][nft_number]['nft_coin_id']
        nfts_dict[nft_url]=nft_coinid

    return nfts_dict

nft_dicts = create_nfts_dict()
print(nft_dicts)


license_uri = "https://bafybeifwxbe7ckkmjm5rxbimmnjkqyaxo7fx2ntvyvmgi3ge6wx7hd2b3a.ipfs.nftstorage.link/MojoPuzzlerChiaNFTAgreement-v1.pdf"
#collection uris are broken down into releases of increasing qty to keep mistakes minimized.
first_hundred = "https://bafybeidgh4ved45xgevocqajl5rbzwvkjvv3bnumcuxhjbldigenmb2qma.ipfs.nftstorage.link/" #2 nfts total
second_hundred = "https://nftstorage.link/ipfs/bafybeicymmc2wggxfelyo7i6twai3ux24aiz3gpwijlfjlzspiexjva2nu/" #7 nfts
life_seeking_darkness = "https://nftstorage.link/ipfs/bafybeicytpu62leaggpamu2s5vpvwcdr2h34hkjkcsy7ys7ztpl3f637f4/" #90 nfts total
brand_new_day = "https://nftstorage.link/ipfs/bafybeihbtgcf5kex3nps7y2ulmpahg5ulo3fi7mhyui6qqakophmfzdzpe/" #100 nfts total
upper_haight = "https://nftstorage.link/ipfs/bafybeiccxbmp3bhzcazfy3vvcciy5mfpzrappuodvtds63zqtbaukaiy6i/" #100 nfts total
buds = "https://nftstorage.link/ipfs/bafybeia4fnc623wkwl7kmyhy6p2m5k7za446zpbqrchfbo5f6nkodu6hoe/" #100 nfts total
blooms = "https://nftstorage.link/ipfs/bafybeifrgkslolh7xvduuv4dgtptyvvat6fv6fhdcbm3fks2rnd7tglzfq/" #100 nfts total
steve_nfts = "https://nftstorage.link/ipfs/bafybeiehjq5xvhqz2jlonlxjasool256uldyfptqy3ygcdgie4qsk7toke/" #27 nfts total

lower_limit, upper_limit = 200, 300
now = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
for nft_number in range(lower_limit,upper_limit):
    #toggle between these three depending on the type of uri update(license|metadata|data)
    #always start with those other than the data uri and finish with the data uri
    #because the key->value pair key is standardized on the original data uri
    #nft_uri, uri_type = license_uri, "-lu"                                                             #license uri
    #nft_uri, uri_type = first_hundred + "gneale-san_francisco{}.json".format(nft_number), "-mu         #metadata uri
    nft_uri, uri_type = life_seeking_darkness + "gneale-san_francisco{}.png".format(nft_number), "-u"   #data uri
    
    nft_key = "https://mojopuzzler.org/nft/gnsf/gneale-san_francisco{}.png".format(nft_number)
    #adjust fee for a high priority. pending transactions cause problems.
    fee = "0.00000001"
    #delay is necessary to let each transaction settle onchain before starting a new one
    delay = 400 #time between txs in seconds

    #get the old nft data uri(key) find the current coin_id which is necessary to update any uri
    #using CLI update the uri. reason for CLI here instead of RPC like previous function is because RPC was 100x slower to transact (300 minutes vs 3 minutes).
    try: 
        nft_coin_id = nft_dicts[nft_key]
        #nft_coin_id, wallet_id = "0x145ee77c2e8c7ec7c1d3073ca8f229f8b8d5c7475018d19994a9a15c380d70d5","8" #throw away nft for testing
        result = subprocess.run(["chia", "wallet", "nft", "add_uri",
        "-f", fprint,
        "-i", wallet_id,
        "-ni", nft_coin_id,
        uri_type, nft_uri,
        "-m", fee 
        ])
        time.sleep(delay)
    #skip missing NFTs; sold, transferred, whatever    
    except KeyError:
        print("There is no {}".format(nft_key))
        #write to log file for reference
        log_file = "add_url-log{}.txt".format(now)  
        with open(log_file, 'a') as outfile:
            outfile.write("{} not in this list.\n".format(nft_key))
