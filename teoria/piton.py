import threading
import time
import random
from pymongo import MongoClient

# Conexão com o banco de dados MongoDB
client = MongoClient('localhost', 27017)
db = client.bancoiot
sensores_collection = db.sensores

# Classe para representar um sensor
class SensorThread(threading.Thread):
    def __init__(self, nome):
        threading.Thread.__init__(self)
        self.nome = nome
        self.sensor_alarmado = False

    def run(self):
        while True: 
            if not self.sensor_alarmado:
                temperatura = random.uniform(30, 40)
                print(f"Sensor {self.nome}: Temperatura: {temperatura:.2f} C°")
                # Atualizar o documento no banco de dados
                self.atualizar_bd(temperatura)
                # Verificar se o sensor deve ser alarmado
                if not self.sensor_alarmado and temperatura > 38:
                    self.sensor_alarmado = True
                    self.atualizar_alarme()
                    print(f"Atenção! Temperatura muito alta! Verificar Sensor {self.nome}!")

            else:
                print(f"Atenção! Sensor {self.nome} alarmado. Verificar temperatura.")        
            time.sleep(5)  # Tempo de atualização do sensor

    def atualizar_bd(self, temperatura):
        # Atualizar o documento do sensor no banco de dados
        sensores_collection.update_one(
            {"nomeSensor": self.nome},
            {"$set": {"valorSensor": temperatura, "sensorAlarmado": self.sensor_alarmado}}
        )
    def atualizar_alarme(self):
        # Atualizar o documento do sensor no banco de dados
        sensores_collection.update_one(
            {"nomeSensor": self.nome},
            {"$set": {"sensorAlarmado": True}}
        )

# Função para criar os documentos dos sensores no banco de dados
def cria_documentos():
    # Criar documentos para os sensores se ainda não existirem
    for nome in ["Temp1", "Temp2", "Temp3"]:
        if not sensores_collection.find_one({"nomeSensor": nome}):
            sensores_collection.insert_one({
                "nomeSensor": nome,
                "valorSensor": 0,
                "unidadeMedida": "C°",
                "sensorAlarmado": False
            })

# Criar os documentos dos sensores no banco de dados
cria_documentos()

# Iniciar as threads dos sensores
sensores = []
for nome in ["Temp1", "Temp2", "Temp3"]:
    sensor = SensorThread(nome)
    sensor.start()
    sensores.append(sensor)

# Esperar indefinidamente (as threads rodarão em background)
for sensor in sensores:
    sensor.join()
