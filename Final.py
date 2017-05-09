import paho.mqtt.client as paho
from time import gmtime, strftime
import paho.mqtt.client as mqtt
import mraa
import time
import sys

LED_GPIO = 5                   
blinkLed = mraa.Gpio(LED_GPIO) 
blinkLed.dir(mraa.DIR_OUT)    
ledState = False              
blinkLed.write(0)
aux = False

def rc_answers_to_strings(argument):
    switcher = {
        0: "Connection successful",
        1: "Connection refused - incorrect protocol version",
        2: "Connection refused - invalid client identifier",
        3: "Connection refused - server unavailable",
        4: "Connection refused - bad username or password",
        5: "Connection refused - not authorised",
        6-255: "Currently unused",
    }
    return switcher.get(argument, "nothing")

def OnConnectHandler(client, userdata, flags, rc):
        print(rc_answers_to_strings(rc))
        
        topic="lab_oit"
        qos = 1
        
        print("Subscribing to the topic %s with QoS %d" %(topic,qos))
        client.subscribe(topic, qos)

def OnDisconnecthandler(client, userdata, rc): 
    print("Disconnection returned" + str(rc))

def OnMessageHandler(client, userdata, message): 
    print("###################################")
    print("New message received:")
    print("Topic: " + str(message.topic))
    print("QoS: " + str(message.qos))
    print("Payload: " + str(message.payload))
    print("###################################")

def OnPublishHandler(client, userdata, mid): 
    print("Publish approved!")

def OnSubscribeHandler(client, userdata, mid, granted_qos): 
    print("Subscribe successful with QoS: " + str(granted_qos))

def OnUnsubscribeHandler(client, userdata, mid): 
    print("Unsubscription returned ")

def OnLogHandler(client, userdata, level, buf): 
    print("Log: " + str(buf))
   									
def on_connect(client, userdata, flags, rc):
    #print("[STATUS] Conectado ao Broker. Resultado de conexao: "+str(rc))
    #faz subscribe automatico no topico
    client.subscribe(topic)
 
#Callback - mensagem recebida do broker

def on_message(client, userdata, msg):

	MensagemRecebida = str(msg.payload)
	if MensagemRecebida == "on":
		blinkLed.write(1) 
		global ledState 
		ledState = True   
		
	if MensagemRecebida == "off":
		blinkLed.write(0) 
		global ledState 
		ledState = False 
	if MensagemRecebida == "state":
		global aux
		aux	= True
	print("[MSG RECEBIDA] Topico: "+msg.topic+" / Mensagem: "+MensagemRecebida)
 
 
#programa principal:
try:
	print("[STATUS] Inicializando MQTT...")
	#inicializa MQTT:
	client = mqtt.Client()
        
except KeyboardInterrupt:
    print "\nCtrl+C pressionado, encerrando aplicacao e saindo..."
    sys.exit(0)
			
Broker = "iot.eclipse.org"
PortaBroker = 1883
KeepAliveBroker = 60                        
topic = "galileo_mqtt"
qos = 1
retain = False	

if __name__ == '__main__':

    publish_delay = 10
    bind_address=""	
    client = paho.Client()
	
    client.on_connect = OnConnectHandler
    client.on_disconnect = OnDisconnecthandler
    client.on_message = OnMessageHandler
    client.on_subscribe = OnSubscribeHandler
    client.on_publish = OnPublishHandler
    
    client.connect(Broker, PortaBroker, KeepAliveBroker, bind_address)
    
    run = True
    while run:
        client.loop()
        
        if(publish_delay < 1):
            client.on_connect = on_connect
            client.on_message = on_message
            client.connect(Broker, PortaBroker, KeepAliveBroker)
		
            if aux == True:
		payload = ledState
		client.publish(topic, payload, qos, retain)
		aux = False
	    publish_delay=10
        else:    
            publish_delay=publish_delay-1
