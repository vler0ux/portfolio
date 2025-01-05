#include <WiFi.h>
#include <HTTPClient.h>
 
const char* ssid = "Lili";

const char* url = "http://192.168.00.00:3000/cible/"; // Remplace par l'URL du serveur
 
volatile bool restartLoop = false;  // Variable pour gérer l'interruption
 
// Variables pour la gestion de la LED et du capteur de lumière
const int ledPin = 25;
const int C1 = 32;
 
int compteurC1 = 0;
bool c1activated = false;
 
// Fonction appelée quand l'interruption est déclenchée
void handleInterrupt() {
    restartLoop = true;  // Marque qu'une interruption a eu lieu
}
 
void setup() {
   pinMode(ledPin, OUTPUT);
    digitalWrite(ledPin, HIGH);  // Allumer la LED au démarrage
 
   Serial.begin(115200);
    delay(1000);
}
    // Configuration du Wi-Fi
   // WiFi.mode(WIFI_STA); // Mode station Wi-Fi
   // WiFi.begin(ssid, password);
   // Serial.println("\nConnecting");
//
   // while (WiFi.status() != WL_CONNECTED) {
   //     Serial.print(".");
   //     delay(100);
    }
 
   // Serial.println("\nConnected to the WiFi network");
   // Serial.print("Local ESP32 IP: ");
   // Serial.println(WiFi.localIP());
 
    // Configuration de l'interruption sur le pin 2
    //  attachInterrupt(digitalPinToInterrupt(2), handleInterrupt, CHANGE);
 // }
 
void loop() {
    // Si une interruption a été déclenchée, redémarrer la boucle
    if (restartLoop) {
        restartLoop = false;
        Serial.println("Interruption détectée, redémarrage de la boucle.");
        return;  /
    }
 
    // Lire la valeur du capteur de lumière
    int C1value = analogRead(C1);
    Serial.print("C1value = ");
    Serial.println(C1value);
 
    // Si connecté au Wi-Fi
   // if (WiFi.status() == WL_CONNECTED) {
    //    HTTPClient http;  // Créer un objet HTTPClient
   //      http.begin(url);  // Spécifier l'URL du serveur pour la requête GET
 
        // Envoyer la requête GET
     //     int httpResponseCode = http.GET();
 
        // Vérifier la réponse du serveur
        //  if (httpResponseCode > 0) {
         //     String payload = http.getString();  // Lire la réponse du serveur
         //     Serial.println(httpResponseCode);   // Afficher le code de la réponse (200, 404, etc.)
          //    Serial.println(payload);            // Afficher la réponse du serveur
     //     } else {
       //       Serial.print("Erreur lors de la requête GET, code : ");
        //      Serial.println(httpResponseCode);
       //   }
 
        // Fermer la connexion
        //  http.end();
     // } else {
      //    Serial.println("WiFi non connecté");
     // }
 
    // Logique pour contrôler la LED en fonction de la lumière captée
    
    if (C1value <= 150) {
        compteurC1++;  // Incrémenter le compteur si faible lumière
        Serial.println("Lumière faible détectée, compteur incrémenté.");
    } else {
        compteurC1 = 0;  // Réinitialiser le compteur si la lumière est forte
        Serial.println("Lumière suffisante, compteur réinitialisé.");
    }
 
    // Activer c1activated après 40 cycles avec faible lumière
    if (compteurC1 >= 40) {
        c1activated = true;
        Serial.println("c1activated est maintenant activé !");
    }
 
    // Contrôler la LED en fonction de c1activated
    if (c1activated) {
        digitalWrite(ledPin, LOW);  
        Serial.println("LED éteinte (Laser capté ou faible lumière prolongée).");
    } else {
        digitalWrite(ledPin, HIGH);  
        Serial.println("LED allumée (Lumière normale).");
    }
 
    delay(100);  /
 
    Serial.println("Cycle terminé.");
}