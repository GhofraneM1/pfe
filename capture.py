import serial
import csv
import time

# Configuration du port série
serial_port = 'COM3'  # Remplacez par le port série correct
baud_rate = 115200
timeout = 1  # Timeout en secondes

# Nom du fichier CSV pour enregistrer les données
csv_filename = 'ecg_data.csv'

# Fonction pour lire et enregistrer les données
def capture_data(serial_port, baud_rate, timeout, csv_filename):
    # Ouvrir le port série
    ser = serial.Serial(serial_port, baud_rate, timeout=timeout)
    time.sleep(5)  # Attendre 5 secondes pour annuler les artefacts

    with open(csv_filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['timestamp', 'ecg_value'])  # Écrire l'en-tête du CSV

        start_time = time.time()
        end_time = start_time + 60  # Capturer les données pendant une minute

        while time.time() < end_time:
            line = ser.readline().decode('utf-8').strip()
            if line:
                try:
                    ecg_value = float(line)  # Vérifie si la valeur peut être convertie en flottant
                    timestamp = time.time() - start_time
                    csv_writer.writerow([timestamp, ecg_value])
                except ValueError:
                    # Ignore la ligne si elle ne peut pas être convertie en flottant
                    continue

    ser.close()
    print(f'Données capturées et enregistrées dans {csv_filename}')

if __name__ == "__main__":
    # Capturer les données
    capture_data(serial_port, baud_rate, timeout, csv_filename)
