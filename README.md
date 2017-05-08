# Hardware_Galileo-gen-1
## Conectando Galileo ao MQTTLens
### Caracteristicas do Galileo
- Processador Intel Quark SoC X1000 32-bit 400MHz
- Alimentação 5V
- Memória 256MB
- Sistema Operacional Linux (Yocto Project based Linux)
- Slot para cartão Micro SD

* [1º Passo: Instalar o Kit IoT Developer - Yocto](#passo1)
* [2º Passo: Conectar Galileo Gen 1 a uma rede Ethernet](#passo2)
* [3º Passo: Executar programas pelo Putty](#passo3)
* [4º Passo: Montagem do Hardware](#passo4)
* [5º Passo: Conexão com o MQTTLens](#passo4)

<a name="passo1"></a>
## 1º Passo: Instalar o Kit IoT Developer - Yocto:

Para Instalar o Sistema Oprecional Linux na placa é necessario um Micro SD vazio, e de no minimo  4GB e no maximo 32GB. Faça o download da Imagem do Sistema Operacional na pagina de downloads da Intel® (https://software.intel.com/en-us/iot/hardware/galileo/downloads) ou vá direto para o download no link: https://software.intel.com/galileo-image/latest. Após baixar o arquivo faça o download do 7-Zip 
(http://www.7-zip.org/) e extraia a imagem em uma pasta do computador. 

Atenção: Mude a data para o dia atual renomeando o arquivo da imagem Ex: iot-devkit-prof-dev-image-galileo-20171704.direct no formato iot-devkit-prof-dev-image-galileo-AAAADDMM.direct. baixe e instale o gravador de cartão SD em: http://sourceforge.net/projects/win32diskimager. Selecione onde esta o seu micro SD e click em "Write".

![atulaizar a data](https://cloud.githubusercontent.com/assets/17688443/25824618/718cdf44-3416-11e7-9963-569d5faf189c.png)
 
 Coloque o sd  no slot no Galileo.
 
![sd](https://cloud.githubusercontent.com/assets/17688443/25824783/e9e28dfe-3416-11e7-809e-418264fc7331.png)

<a name="passo2"></a>
## 2º Passo: Conectar Galileo Gen 1 a uma rede Ethernete:

É necessario que a placa esteja na mesma rede ethernete que o seu computador, pois faremos uma conexão via SSH. Conecte o cabo de rede na placa atraves da porta. Para acessar o Linux da placa precisamos antes descobrir o ip. Abra a IDE do Arduino e execute o seguinte programa:

```bash
void setup() {
  Serial.begin(9600);
  //aperte 'a' para mostrar o ip
  while(Serial.read()!='a'){
    Serial.println("hello");
    delay(1000);
  }
  //ifconfig para serial monitor
  system("ifconfig > /dev/ttyGS0");
}
 
void loop() {
 
}
```
Obeservação: É necessario a versão 1.6.0 da IDE. Caso não tenha a IDE do Arduino 1.6.0 baixe aqui.
Caso nao tenha instalado a IDE baixe em: https://software.intel.com/en-us/iot/hardware/galileo/dev-kit e instale.

Abra o monitor serial no canto superior direito e aperte 'a' para mostrar o ip da placa.

![ip](https://cloud.githubusercontent.com/assets/17688443/25825135/29f54660-3418-11e7-8056-863d2a8f0807.png)

Para conectar com o terminal do Yocto vamos utilizar o programa putty. Baixe em http://www.putty.org/ e instale. Usando o SSH insira o endereço IP da placa e clique no botão 'Open'.  

![putty](https://cloud.githubusercontent.com/assets/17688443/25825161/4908213a-3418-11e7-8a06-93a0716e5189.png)

Será aberta uma janela terminal do Yocto solicitando um login. Na primeira conexão aparecerá uma mensagem perguntando se você deseja armazenar as chaves de acesso dessa conexão. Clique em Yes. O login inicial da placa é o root. Portanto digite root e pressione a tecla enter. 

![sim](https://cloud.githubusercontent.com/assets/17688443/25825171/5481514e-3418-11e7-96af-a54cf298f493.png)

<a name="passo3"></a>
## 3º Passo: Executar programas pelo Putty:
Crie na raiz do cartão SD um arquivo chamado Final.py (tudo em minúsculas) e coloque dentro dele o código abaixo. Recomendamos utilizar o programa Notepad++, selecionando o caracter de fim de linha UNIX/OSX no menu EDIT => EOL Conversion:

```bash
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
        
        topic="icc_nmc"
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
```      
Os arquivos salvo no SD são acessados no endereco de /media/card navegue pelo Linux usando os comandos:

- cd .. //sair da pasta
- cd nome_da_pasta //entrar na pasta 
- ls //ver o que tem na pasta
- pwn //ver em qual pasta está

navegue ate encontrar o aquivo salvo o Final.py e execute usando o comando python Final.py 

![final](https://cloud.githubusercontent.com/assets/17688443/25825195/7ac410e4-3418-11e7-8d16-8025092bb820.png)

<a name="passo4"></a>
## 4º Passo: Montagem do Hardware:

