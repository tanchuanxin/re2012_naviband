#include <WiFi.h>
#include <stdio.h>
#include <string>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice - Copy.h>
#include <typeinfo>

//BLE stuff
int scanTime = 5; //In seconds
BLEScan* pBLEScan;
int rssi01;
int rssi02;
int rssi03;

class MyAdvertisedDeviceCallbacks: public BLEAdvertisedDeviceCallbacks {
   void onResult(BLEAdvertisedDevice advertisedDevice) {
     Serial.printf("Advertised Device: %s", advertisedDevice.toString().c_str());
     Serial.print(" RSSI: ");
     Serial.println(advertisedDevice.getRSSI());
   }
};
   
//Wifi Stuff
const char* ssid     = "AndroidAP";           // SSID of local network
const char* password = "matthewljk";        // Password on network
const char* ipv4_address = "192.168.43.101"; // IPv4 address obtained from cmd --> ipconfig
const char* host_name = "Host: 192.168.43.101"; // hostname for localhost

WiFiClient client;
const char* servername=ipv4_address;
String result;


void setup() {
  // put your setup code here, to run once:
  //Wifi
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

  //BLE

  Serial.begin(115200);
  Serial.println("BLE Scanning...");

  BLEDevice::init("");
  pBLEScan = BLEDevice::getScan(); //create new scan
  pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
  pBLEScan->setActiveScan(true); //active scan uses more power, but get results faster
  pBLEScan->setInterval(100);
  pBLEScan->setWindow(99);  // less or equal setInterval value

}

void loop() {
  // put your main code here, to run repeatedly:
  //BLE
  BLEScanResults foundDevices = pBLEScan->start(scanTime, false);
  Serial.print("Devices found: ");
  int deviceCount = foundDevices.getCount();
  Serial.println(deviceCount);
  for (int i = 0; i < deviceCount; i++) {
    BLEAdvertisedDevice device = foundDevices.getDevice(i);
    if (device.haveName ()){
      Serial.print(F("Name -> "));
      Serial.println(device.getName().c_str());
      String string1 = "beacon1";
      String string2 = "beacon2";
      String string3 = "beacon3";
      String string4 = "Beacon04";
      if (strcmp(device.getName().c_str(), string1.c_str()) == 0){
        int rssi01 = device.getRSSI();
        Serial.println("Sending data");
        sendData(rssi01,01);
        Serial.println(rssi01);
      }
      else if(strcmp(device.getName().c_str(), string2.c_str()) == 0){
        int rssi02 = device.getRSSI();
        Serial.println("Sending data");
        sendData(rssi02,02);
        Serial.println(rssi02);
      }
      else if(strcmp(device.getName().c_str(), string3.c_str()) == 0){
        int rssi03 = device.getRSSI();
        Serial.println("Sending data");
        sendData(rssi03,03);
        Serial.println(rssi03);
      }
      else if(strcmp(device.getName().c_str(), string4.c_str()) == 0){
        int rssi04 = device.getRSSI();
      }
    }
  }
  // Wifi for sending BLE data
        delay(3000);
}

void sendData(int rssival,int BID)
{
  if (client.connect(servername, 80)) {  //starts client connection, checks for connection
    client.print("GET /sendData?beaconID=beacon");
    client.print(BID);
    client.print("&rssiValue=");
    client.print(rssival);
//    client.print("&beaconID=beacon02&rssiValue=");
//    client.print(rssi02);
    client.println("");
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