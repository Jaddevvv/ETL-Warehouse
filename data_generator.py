import sys
import rapidjson as json
import optional_faker as _
import uuid
import random

from dotenv import load_dotenv
from faker import Faker
from datetime import date, datetime

load_dotenv()
fake = Faker()
inventory = [
    "Peugeot 208", "Peugeot 3008", "Citroen C3", "Renault Megane",
    "Fiat 500e", "Maserati Grecale Folgore", "Renault Mégane E-Tech",
    "Peugeot e-208", "Peugeot e-3008", "Citroen ë-C4", "Citroen Ami",
    "DS 3 E-Tense", "DS 4 E-Tense", "DS 7 E-Tense", "DS 9 E-Tense",
    "Fiat 600e", "Jeep Avenger EV", "Opel Mokka-e", "Opel Corsa-e",
    "Opel Astra Electric", "Peugeot e-2008", "Citroen ë-Berlingo",
    "Fiat E-Ulysse", "Peugeot e-Rifter", "Jeep Recon EV", "Jeep Wagoneer S",
    "Maserati GranTurismo Folgore", "Maserati MC20 Folgore", "Opel Zafira-e Life"
]



def print_client_support():
    global inventory, fake
    state = fake.state_abbr()
    client_support = {'txid': str(uuid.uuid4()),
                      'rfid': hex(random.getrandbits(96)),
                      'item': fake.random_element(elements=inventory),
                      'purchase_time': datetime.utcnow().isoformat(),
                      'expiration_time': date(2023, 6, 1).isoformat(),
                      'days': fake.random_int(min=1, max=7),
                      'name': fake.name(),
                      'address': fake.none_or({'street_address': fake.street_address(), 
                                                'city': fake.city(), 'state': state, 
                                                'postalcode': fake.postalcode_in_state(state)}),
                      'phone': fake.none_or(fake.phone_number()),
                      'email': fake.none_or(fake.email()),
                      'emergency_contact' : fake.none_or({'name': fake.name(), 'phone': fake.phone_number()}),
    }
    d = json.dumps(client_support) + '\n'
    sys.stdout.write(d)


if __name__ == "__main__":
    args = sys.argv[1:]
    total_count = int(args[0])
    for _ in range(total_count):
        print_client_support()
    print('')