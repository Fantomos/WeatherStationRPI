from i2c import I2C

## Classe Mkrfox. 
#  Cette classe permet la communication avec le microcontrolleur Arduino MKRFOX 1200.
class Mkrfox:

    ## Constructeur.
    # @param pi Instance de pigpio.
    # @param logger Logger principal.
    # @param i2c_address Adresse I2C du MKRFOX 1200.
    # @param nb_try Nombres d'essais maximum de l'initialisation du bus I2C. La valeur par défaut est 5.
    def __init__(self, pi, i2c_address, logger, nb_try):
         ## Objet I2C initialisé.
        self.i2c_bus = I2C(pi, i2c_address, logger, nb_try)
        ## Logger principal.
        self.logger = logger

    
    ## Liste des nom des registres associés à leurs adresses et nombres d'octects.
    register =	{
            "time" : (0x00,4),
            "state" : (0x01,1),
            "error" : (0x02,1),
            "sleep" : (0x03,1),
            "wakeup" : (0x04,1),
            "sensorsData" : (0x05,12),
            "battery" : (0x06,4),
            "battery_threshold" :(0x07,4)
    }
   

    ## Opération de lecture d'un registre du MKRFOX.
    # @param regName Nom du registre à lire.
    # @param length Le nombre d'octet à lire.
    # @return Retourne la valeur du registre.
    def read(self, regName):
        return self.i2c_bus.readReg(self.register[regName][0], self.register[regName][1])
    
    ## Opération d'écriture d'un registre du MKRFOX.
    # @param regName Nom du registre à écrire.
    # @param data Les données à écrire.
    # @param length Le nombre d'octet à écrire.
    def write(self, regName, data):
        self.i2c_bus.writeReg(self.register[regName][0], data, self.register[regName][1])

    ## Formate les données des capteurs sous forme d'un tableau d'octet.
    # @param sensorsData Les données des capteurs.
    # @return Retourne un tableau d'octet.
    def formatData(self, sensorsData):
        try:
            data = []
            temperature = round(sensorsData['Temperature']) if float(sensorsData['Temperature']) < 100 and float(sensorsData['Temperature']) > -50 else 0
            vitesse_moy = round(sensorsData['Speed']) if float(sensorsData['Speed']) < 255 and float(sensorsData['Speed']) >= 0 else 0
            vitesse_max = round(sensorsData['Speed_max']) if float(sensorsData['Speed_max']) < 255 and float(sensorsData['Speed_max']) >= 0 else 0
            direction_moy = round(sensorsData['Direction'])  if float(sensorsData['Direction']) < 360 and float(sensorsData['Direction']) >= 0 else 0
            direction_max = round(sensorsData['Direction_max']) if float(sensorsData['Direction_max']) < 360 and float(sensorsData['Direction_max']) >= 0 else 0
            pression = round(sensorsData['Pressure']) if int(sensorsData['Pressure']) > 400 and int(sensorsData['Pressure']) < 1500 else 0
            humidite = round(sensorsData['Humidity']) if int(sensorsData['Humidity']) <= 100 and int(sensorsData['Humidity']) >= 0 else 0
            voltage = round(1000 * sensorsData['Battery'])
            
            #Vitesse du vent
            #On envoie la vitesse du vent de l'intervalle [0 ; 255] en un octet
            data.append(vitesse_moy)
            data.append(vitesse_max)

            #Direction du vent
            #On envoie la direction entre [0 ; 360] en deux octects
            data.append(direction_moy // 256)
            data.append(direction_moy % 256)
            data.append(direction_max // 256)
            data.append(direction_max % 256)

            #Humidité
            #On envoie l'humidité directement car elle est comprise entre 0 et 100
            data.append(humidite)

            #Température
            #On passe la température de l'intervalle [-50; 205] à l'intervalle entier [0 ; 255] qu'on envoie en un octet
            data.append(temperature.to_bytes(1, 'big', signed=True))

            #Pression
            #On envoie la pression de l'intervalle [800 ; 1453] en deux octects
            data.append(pression // 256)
            data.append(pression % 256)     

            #Tension de la batterie
            #On convertie la tension en mV sur l'intervalle [0; 65536] en deux octets
            data.append(voltage // 256)
            data.append(voltage % 256)

            return data 
        except:
            self.logger.error("Erreur lors du traitement des données pour l'envoi au réseau Sigfox.")
            
        
    ## Transmet les données des capteurs au MKRFOX.
    # @param sensorsData Les données des capteurs.
    def sendData(self, sensorsData):
        data = self.formatData(sensorsData)
        try:
            self.write("sensorsData", data)
        except:
            self.logger.error("Impossible d'envoyer des données au réseau Sigfox")
        else:
            self.logger.success("Envoie reussi au réseau Sigfox")
        