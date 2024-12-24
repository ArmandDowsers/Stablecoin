#%% Import des lib 
from web3 import Web3

#%% Paramètres
token_cible = "0x553303d460EE0afB37EdFf9bE42922D8FF63220e"  # UNI/USD
token_stablecoin = "0x3E7d1eAB13ad0104d2750B8863b489D65364e32D"  # USDT/USD
infura_url = "https://mainnet.infura.io/v3/f9f37ed1971d4f218ec8757e119da6cc"
bloc_debut = 21470000
bloc_fin = 21471671
intervalle_de_confiance = 0.05  # ±5%

#%% Connexion au réseau Ethereum
web3 = Web3(Web3.HTTPProvider(infura_url))
if not web3.is_connected():
    raise ConnectionError("Impossible de se connecter au réseau Ethereum.")

#%% ABI pour Chainlink
abi_chainlink_feed = [
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "latestRoundData",
        "outputs": [
            {"internalType": "uint80", "name": "roundId", "type": "uint80"},
            {"internalType": "int256", "name": "answer", "type": "int256"},
            {"internalType": "uint256", "name": "startedAt", "type": "uint256"},
            {"internalType": "uint256", "name": "updatedAt", "type": "uint256"},
            {"internalType": "uint80", "name": "answeredInRound", "type": "uint80"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
]

#%% Contrats
stablecoin_contract = web3.eth.contract(
    address=Web3.to_checksum_address(token_stablecoin), 
    abi=abi_chainlink_feed
)
token_cible_contract = web3.eth.contract(
    address=Web3.to_checksum_address(token_cible), 
    abi=abi_chainlink_feed
)

#%% On récupère les prix pour chaque bloc (dict vide)
stablecoin_prices_by_block = {}
token_prices_by_block = {}

for bloc in range(bloc_debut, bloc_fin + 1):
    # pour le stablecoin USDT
    try:
        dec_s = stablecoin_contract.functions.decimals().call(block_identifier=bloc)
        data_s = stablecoin_contract.functions.latestRoundData().call(block_identifier=bloc)
        price_s = data_s[1] / (10**dec_s)
        stablecoin_prices_by_block[bloc] = price_s
        print(f"[Bloc {bloc}] Prix stablecoin = {price_s} $")
    except Exception:
        print(f"[Bloc {bloc}] Aucun prix stablecoin (erreur : {Exception})")

    # pour le token
    try:
        dec_t = token_cible_contract.functions.decimals().call(block_identifier=bloc)
        data_t = token_cible_contract.functions.latestRoundData().call(block_identifier=bloc)
        price_t = data_t[1] / (10**dec_t)
        token_prices_by_block[bloc] = price_t
        print(f"[Bloc {bloc}] Prix token = {price_t} $")
    except Exception:
        print(f"[Bloc {bloc}] Aucun prix token (erreur : {Exception})")

#%% On calcul le ratio par rapport à chaque bloc
ratios = []

for bloc in range(bloc_debut, bloc_fin + 1):
    if bloc in stablecoin_prices_by_block and bloc in token_prices_by_block:
        stable_price = stablecoin_prices_by_block[bloc]
        token_price = token_prices_by_block[bloc]
        ratio = token_price / stable_price
        ratios.append(ratio)
        print(f"[Bloc {bloc}] Ratio = {ratio}")
    else:
        print(f"[Bloc {bloc}] Ratio non calculable")

#%% On fait avg des ratios
if ratios:
    moyenne_ratio = sum(ratios) / len(ratios)
    print(f"\nMoyenne des ratios (Token/USDT) = {moyenne_ratio:.4f}")

    if (1 - intervalle_de_confiance) <= moyenne_ratio <= (1 + intervalle_de_confiance):
        print("Le token est un stablecoin !!")
    else:
        print("Le token n'est pas un stablecoin !!")
else:
    print("Impossible de calculer le ratio")
