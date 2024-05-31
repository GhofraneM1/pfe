#include <WiFi.h>

// Définir la broche de lecture du signal ECG
const int ecgPin = 34; // GPIO34 (A2)

// Variables pour stocker les valeurs lues
int ecgValue = 0;

// Variables pour le filtre passe-bas de deuxième ordre (Butterworth)
float filteredValue1 = 0;
float filteredValue2 = 0;
const float a0 = 0.067455;
const float a1 = 0.134911;
const float a2 = 0.067455;
const float b1 = -1.142980;
const float b2 = 0.412802;

// Variables pour stocker les valeurs précédentes
float input_1 = 0, input_2 = 0;
float output_1 = 0, output_2 = 0;

void setup() {
  // Initialiser le terminal série
  Serial.begin(115200);
  delay(1000); // Attendre un peu pour que tout soit bien initialisé
}

void loop() {
  // Lire la valeur brute du signal ECG
  ecgValue = analogRead(ecgPin);

  // Appliquer le filtre passe-bas de deuxième ordre (Butterworth)
  filteredValue2 = a0 * ecgValue + a1 * input_1 + a2 * input_2 - b1 * output_1 - b2 * output_2;

  // Mettre à jour les valeurs précédentes
  input_2 = input_1;
  input_1 = ecgValue;
  output_2 = output_1;
  output_1 = filteredValue2;

  // Envoyer la valeur filtrée via le port série
  Serial.println(filteredValue2);

  // Attendre un court instant avant de lire la prochaine valeur
  delay(10); // Ajustez le délai selon vos besoins
}
