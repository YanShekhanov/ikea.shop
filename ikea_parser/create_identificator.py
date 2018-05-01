import string
import random
#Создание идентификатора по длинне
def create_identificator(len):
    identificator_join = ''
    identificator_dict = []
    for sym in range(len):
        identificator_sym = random.choice(string.ascii_letters + string.ascii_lowercase + string.ascii_uppercase)
        identificator_dict.append(identificator_sym)
    identificator = identificator_join.join(identificator_dict)
    return identificator

def create_num_identificator(len):
    identificator_join = ''
    identificator_dict = []
    for sym in range(len):
        identificator_dict.append(random.choice(['1', '2', '3', '4', '5', '6', '7', '8', '9']))
    return identificator_join.join(identificator_dict)