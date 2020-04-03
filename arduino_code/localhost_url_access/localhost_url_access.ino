#include <WiFi.h>
#include <ArduinoJson.h>

const char* ssid     = "Whizz";           // SSID of local network
const char* password = "2billion";        // Password on network
const char* ipv4_address = "192.168.1.82"; // IPv4 address obtained from cmd --> ipconfig
const char* host_name = "Host: 192.168.1.82"; // hostname for localhost

WiFiClient client;
const char* servername=ipv4_address;
String result;


void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);


  // CONNECTING TO WIFI NETWORK
  Serial.println("------------Beginning WiFi setup------------");
  Serial.println("Connecting to WiFi");
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.println("Connecting to WiFi...");
    delay(500);
  }
  
  Serial.println("Connected to WiFi");
  delay(1000);
  Serial.println("------------Finish WiFi setup------------");
}


void loop() {
  // put your main code here, to run repeatedly:

  // // for sending BLE data
  // Serial.println("Sending data");
  // sendData();
  // delay(1000);

  // for getting instructions for arduino
  Serial.println("Getting instructions");
  getInstructions();
  delay(1000);
}



void sendData()
{
  if (client.connect(servername, 80)) {  //starts client connection, checks for connection
    client.println("GET /sendData?beaconID=beacon01&rssiValue=456");
    client.println(host_name);
    client.println("User-Agent: Naviband");
    client.println("Connection: close");
    client.println();
  } 
  else {
    Serial.println("connection failed"); //error message if no client connect
    Serial.println();
  }

  while(client.connected() && !client.available()) delay(1); //waits for data
  while (client.connected() || client.available()) { //connected or data available
    char c = client.read(); //gets byte from ethernet buffer
    result = result+c;
  } 

  client.stop(); //stop client
  result.replace('[', ' ');
  result.replace(']', ' ');
  Serial.println(result);
}




// used by arduino to receive instructions from the server
void getInstructions()
{
  if (client.connect(servername, 80)) {  //starts client connection, checks for connection
    client.println("GET /getInstructions");
    client.println(host_name);
    client.println("User-Agent: Naviband");
    client.println("Connection: close");
    client.println();
  } 
  else {
    Serial.println("connection failed"); //error message if no client connect
    Serial.println();
  }

  while(client.connected() && !client.available()) delay(1); //waits for data
  while (client.connected() || client.available()) 
  { //connected or data available
    char c = client.read(); //gets byte from ethernet buffer
    result = result+c;
  } 

  client.stop(); //stop client
  result.replace('[', ' ');
  result.replace(']', ' ');
  Serial.println(result);

  
  char jsonArray [result.length()+1];
  result.toCharArray(jsonArray,sizeof(jsonArray));
  jsonArray[result.length() + 1] = '\0';
  
  StaticJsonDocument<1024> doc;
  DeserializationError error = deserializeJson(doc, jsonArray);
  if (error)
  {
    Serial.println("deserializeJson() failed with code");
    Serial.println(error.c_str());
  }
  
  String appointmentVenue = doc["appointmentVenue"];
  Serial.println("LOOK HERE" + appointmentVenue);
}
