#include <string>        

const int zpin = A0;                        //analog pin

int st_podatkov = 50;                       //number of data in a packet

long t_0;
long t_1;
long t_2;
long z;
long f_s = 100;                             //sampling frequency [Hz]
long delta_t = (1e6/f_s);    

//*******************************************************

//Configure WIFI:
#include <ESP8266WiFi.h>                    //Wifi-library

//WLAN-Config
const char* ssid     = "your_ssid";         //name of the network      
const char* password = "your_password";     //password of the network     

//Host&Client
WiFiClient client;                             
const char* host = "111.111.111.1";         //computer IP address  
const int httpPort = 5021;                  //selected port number               

void setup() {

  Serial.begin(115200);                     //baud rate

  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
 
  Serial.println("");
  Serial.println("WiFi connected");  
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}
 

void loop() {
  if (!client.connected())
  {
    if (!client.connect(host, httpPort))
    {
      Serial.println("Connection failed!");
      delay(1000);
    }
  } 
   else {
      String a = String();
    
      
            for(int i = 0; i < st_podatkov; i++)
            {
              t_0 = micros();
              z = analogRead(zpin)/4;       
              a.concat(z);                   
              a.concat("\t");                      
              a.concat(t_0);                       
              a.concat("\n");                       
              
                if (i == st_podatkov-1)
                    {
                        client.print(a);      
                        //yield();
                    }

                    
              yield();                        
              t_1 = micros();
              t_2 = (delta_t - (t_1 - t_0));
              Serial.println(t_2);

              if (t_2 < 0)
                 {
                  t_2 = 0;
                  a.concat("-1");
                  }     
                         
              delayMicroseconds(t_2);             
            }   //for
       }  //else     
  }  //loop 
  
    
