#include <ESP8266WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>

// --- GANTI DENGAN DATA ANDA ---
const char* ssid = "NAMA_WIFI";
const char* password = "PASSWORD_WIFI";

const char* mqtt_server = "4fcb16d24e1d40a98656703baa5331ea.s1.eu.hivemq.cloud";
const int mqtt_port = 8883; // Port TLS
const char* mqtt_user = "smart_cctv_mqtt";
const char* mqtt_pass = "Admin123";
const char* mqtt_topic = "perintah/aktuator";
// --------------------------------

// Buat client secure dan MQTT
WiFiClientSecure espClient;
PubSubClient client(espClient);

// Callback ketika pesan masuk
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("📩 Pesan masuk di topik: ");
  Serial.println(topic);

  Serial.print("Isi pesan: ");
  String message;
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println(message);

  // Tambahan: contoh jika ingin tindakan otomatis
  if (message == "BUKA") {
    Serial.println("🚪 Perintah diterima: BUKA pintu!");
  } else if (message == "TUTUP") {
    Serial.println("🚪 Perintah diterima: TUTUP pintu!");
  }
}

// Koneksi ke WiFi
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("🔌 Menghubungkan ke WiFi: ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n✅ WiFi terhubung!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

// Reconnect MQTT jika terputus
void reconnect() {
  while (!client.connected()) {
    Serial.print("🔄 Mencoba koneksi ke MQTT...");
    String clientId = "esp8266-subscriber-";
    clientId += String(random(0xffff), HEX);

    // Coba koneksi ke broker dengan kredensial
    if (client.connect(clientId.c_str(), mqtt_user, mqtt_pass)) {
      Serial.println("✅ Terhubung ke broker MQTT!");
      client.subscribe(mqtt_topic);
      Serial.print("📡 Subscribed ke topik: ");
      Serial.println(mqtt_topic);
    } else {
      Serial.print("❌ Gagal (rc=");
      Serial.print(client.state());
      Serial.println("). Coba lagi 5 detik...");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  setup_wifi();

  // Abaikan sertifikat TLS (opsi aman diaktifkan)
  espClient.setInsecure();

  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}
