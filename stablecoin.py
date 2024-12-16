from web3 import Web3

#%% Paramètres
token_cible = "0x553303d460EE0afB37EdFf9bE42922D8FF63220e" # UNI/USD
token_stablecoin = "0x3E7d1eAB13ad0104d2750B8863b489D65364e32D"  # USDT/USD
infura_url = "https://mainnet.infura.io/v3/f9f37ed1971d4f218ec8757e119da6cc"
bloc_debut = 21371420
bloc_fin = 21371430
intervalle_de_confiance = 0.05  # ±5%

#%% Connexion au réseau Ethereum
web3 = Web3(Web3.HTTPProvider(infura_url))
if not web3.is_connected():
    raise ConnectionError("Impossible de se connecter au réseau Ethereum.")

#%% ABI pour Chainlink
abi_chainlink_feed = [
    {"inputs": [], "name": "decimals", "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "latestRoundData", "outputs": [
        {"internalType": "uint80", "name": "roundId", "type": "uint80"},
        {"internalType": "int256", "name": "answer", "type": "int256"},
        {"internalType": "uint256", "name": "startedAt", "type": "uint256"},
        {"internalType": "uint256", "name": "updatedAt", "type": "uint256"},
        {"internalType": "uint80", "name": "answeredInRound", "type": "uint80"}], "stateMutability": "view", "type": "function"}
]

#%% contrat chainlink pour stablecoin et token
stablecoin_contract = web3.eth.contract(address=Web3.to_checksum_address(token_stablecoin), abi=abi_chainlink_feed)
token_cible_contract = web3.eth.contract(address=Web3.to_checksum_address(token_cible), abi=abi_chainlink_feed)

#%% fonction qui recup le prix avec chainlink sur un bloc spécifique (feed_contract c'est le contrat qui est utilisé pour recup le prix et block_number c'est pour le numéro de bloc eth)
def get_token_cible_price(feed_contract, block_number):
    decimals = feed_contract.functions.decimals().call()
    price_data = feed_contract.functions.latestRoundData().call() #fonction du contrat chainlink que l'on appel(latestRoundData)
    price = price_data[1] 
    return price / (10 ** decimals)

# liste vide pour les ratio qu'on va add (append)
ratios = []

#%% boucle for sur les blocs
for bloc in range(bloc_debut, bloc_fin + 1):
    try:
        # on récup le prix pour le bloc
        price_stablecoin = get_token_cible_price(stablecoin_contract, bloc)
        token_cible_price = get_token_cible_price(token_cible_contract, bloc)

        # on calcul le ratio
        ratio = token_cible_price / price_stablecoin
        ratios.append(ratio)
    except Exception:
        print(f"Erreur au bloc {bloc} : {Exception}")

#%% avg des ratios
if ratios:
    moyenne_ratio = sum(ratios) / len(ratios)
    print(f"Moyenne des ratios (Token/USDT) : {moyenne_ratio:.4f}")

    # condtions qui détermine si le token est un stablecoin ou nn
    if (1 - intervalle_de_confiance) <= moyenne_ratio <= (1 + intervalle_de_confiance):
        print("Le token est un stablecoin.")
    else:
        print("Le token n'est pas un stablecoin.")
else:
    print("impossible de savoir si le token est un stablecoin ou nn")
