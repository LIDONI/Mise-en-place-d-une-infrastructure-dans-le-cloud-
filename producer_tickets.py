from confluent_kafka import Producer
import json, random, time, datetime

p = Producer({'bootstrap.servers': 'localhost:19092'})

TYPES = ['incident', 'demande_info', 'maintenance']
PRIORITES = ['basse', 'moyenne', 'haute']

def generate_ticket():
    return {
        "ticket_id": random.randint(1000, 9999),
        "client_id": random.randint(1, 50),
        "datetime": datetime.datetime.now().isoformat(),
        "demande": random.choice(["Support", "Erreur", "Mise à jour"]),
        "type_demande": random.choice(TYPES),
        "priorite": random.choice(PRIORITES)
    }

while True:
    ticket = generate_ticket()
    p.produce("client_tickets", json.dumps(ticket).encode('utf-8'))
    p.flush()
    print("Envoyé :", ticket)
    time.sleep(1)
