// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// valeur true ou false et set valeur avec sepolia

contract contrat{

  bool valeur;

  constructor (){
    valeur = true;
  }

  function setValeur(bool valeur2) public{
    valeur = valeur2;
    
  }

    function getValeur() view public returns(bool){
      return valeur;
    
  }

}