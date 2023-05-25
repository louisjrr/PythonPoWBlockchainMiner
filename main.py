# -*- coding: utf-8 -*-
import string
import random
import hashlib
import time
import pickle
#import zmq
import json
import socket

#context = zmq.Context()
#socket = context.socket(zmq.PUB)
#socket.bind("tcp://*:5555")

# Configuration du serveur
host = 'localhost'
port = 5000

# Création du socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(1)

# Attente de la connexion
client_socket, address = server_socket.accept()
print("Instance 1: Connexion établie avec", address)


class Block:
    def __init__(self, transactions, previous_hash):
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        data = str(self.timestamp) + str(self.transactions) + str(self.previous_hash) + str(self.nonce)
        return hashlib.sha256(data.encode()).hexdigest()

    def mine_block(self, difficulty):
        target = '0' * difficulty
        start_time = time.time()
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        end_time = time.time()
        mining_time = end_time - start_time
        print("Le bloc a été miné en", mining_time, "secondes.")


class Blockchain:
    def __init__(self):
        self.chain = self.load_blockchain()
        self.difficulty = 6
        self.pending_transactions = []
    
    def load_blockchain(self):
        try:
            with open('blockchain.pkl', 'rb') as file:
                return pickle.load(file)
        except FileNotFoundError:
            return [self.create_genesis_block()]

    def save_blockchain(self):
        with open('blockchain.pkl', 'wb') as file:
            pickle.dump(self.chain, file)

    def create_genesis_block(self):
        return Block([], "0")

    def get_last_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)

    def mine_pending_transactions(self):
        new_block = Block(self.pending_transactions, self.get_last_block().hash)
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        self.pending_transactions = []

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            if current_block.hash != current_block.calculate_hash():
                return False
            
            if current_block.previous_hash != previous_block.hash:
                return False
            
        return True
    
    def get_pending_transactions(self):
        return sorted(self.pending_transactions, key=lambda transaction: transaction['amount'], reverse=True)


# Création de la blockchain
blockchain = Blockchain()

#Génération d'addresse
def generate_random_address(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


# Boucle pour simuler un nœud sur chaque terminal de commande
while True:
    print("\n==== Menu ====")
    print("1. Ajouter une transaction")
    print("2. Miner les transactions en attente")
    print("3. Afficher la liste des transactions en attentes")
    print("4. Afficher la blockchain")
    print("5. Quitter")
    choice = input("Choisissez une option (1-4): ")
    #message = socket.recv_string()

    client_socket.settimeout(10)
    try:
        message = client_socket.recv(1024).decode()
 
        blockchain.pending_transactions = json.loads(message)
        print("Transactions en attentes :", blockchain.get_pending_transactions())

    except socket.timeout:
        
        if choice == '1':
            sender = generate_random_address(10)
            recipient = generate_random_address(10)
            amount = float(input("Montant de la transaction: "))
            transaction = {"sender": sender, "recipient": recipient, "amount": amount}
            blockchain.add_transaction(transaction)
            print("La transaction a été ajoutée avec succès.")
            message = json.dumps(blockchain.get_pending_transactions())
            #socket.send_string(message)
            client_socket.send(message.encode())
        elif choice == '2':
            blockchain.mine_pending_transactions()
            blockchain.save_blockchain()
            print("Les transactions en attente ont été minées avec succès.")
            message = json.dumps(blockchain.get_pending_transactions())
            #socket.send_string(message)
            client_socket.send(message.encode())
        elif choice == '3':
            for transaction in blockchain.get_pending_transactions():
                print("Sender:", transaction['sender'])
                print("Recipient:", transaction['recipient'])
                print("Amount:", transaction['amount'])
                print("-------------------")
        elif choice == '4':
            print("\n==== Blockchain ====")
            for block in blockchain.chain:
                print("|Hash:", block.hash)
                print("|Timestamp:", block.timestamp)
                print("|Transactions:", block.transactions)
                print("|Nonce:", block.nonce)
                print("|Previous Hash:", block.previous_hash)
                print("--------------------------------------")
        elif choice == '5':
            blockchain.save_blockchain()
            break
        
        else:
            print("Option invalide: Veuillez réessayer.")
        print("Le client n'a pas envoyé de message.")
