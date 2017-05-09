# Hardware_Galileo-gen-1
## Comando e Monitoramento do Galileo usando MQTTLens
### Caracteristicas do Galileo
- Processador Intel Quark SoC X1000 32-bit 400MHz
- Alimentação 5V
- Memória 256MB
- Sistema Operacional Linux (Yocto Project based Linux)
- Slot para cartão Micro SD

* [1º Passo: Instalar o Kit IoT Developer - Yocto](#passo1)
* [2º Passo: Conectar Galileo Gen 1 a uma rede Ethernet](#passo2)
* [3º Passo: Executar programas pelo Putty](#passo3)
* [4º Passo: Conexão com o MQTTLens](#passo4)

<a name="passo1"></a>
## 1º Passo: Instalar o Kit IoT Developer - Yocto:

Para Instalar o Sistema Oprecional Linux na placa é necessario um Micro SD vazio, e de no mínimo  4GB e no máximo 32GB. Faça o download da Imagem do Sistema Operacional na pagina de downloads da Intel® [Kit IoT Developer](https://software.intel.com/en-us/iot/hardware/galileo/downloads) ou vá direto para o download no [link](https://software.intel.com/galileo-image/latest). Após baixar o arquivo faça o download do [7-Zip](http://www.7-zip.org/) e extraia a imagem em uma pasta do computador. 

Atenção: Mude a data para o dia atual renomeando o arquivo da imagem Ex: iot-devkit-prof-dev-image-galileo-20171704.direct no formato iot-devkit-prof-dev-image-galileo-AAAADDMM.direct. Baixe e instale o gravador de cartão SD [Win32_Disk_Imager](http://sourceforge.net/projects/win32diskimager). Selecione onde esta o seu micro SD e click em "Write".

![atulaizar a data](https://cloud.githubusercontent.com/assets/17688443/25824618/718cdf44-3416-11e7-9963-569d5faf189c.png)
 
 Coloque o sd  no slot no Galileo.
 
![sd](https://cloud.githubusercontent.com/assets/17688443/25824783/e9e28dfe-3416-11e7-809e-418264fc7331.png)

<a name="passo2"></a>
## 2º Passo: Conectar Galileo Gen 1 a uma rede Ethernet:

É necessário que a placa esteja na mesma rede ethernet que o seu computador, pois faremos uma conexão via SSH. Conecte o cabo de rede na placa através da porta. Para acessar o Linux da placa precisamos antes descobrir o ip. Abra a IDE do Arduino e execute o seguinte programa:

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
Obeservação: É necessário a versão 1.6.0 da IDE. Caso não tenha a IDE do Arduino 1.6.0 baixe [aqui](https://software.intel.com/en-us/iot/hardware/galileo/dev-kit).

Abra o monitor serial no canto superior direito e aperte 'a' para mostrar o ip da placa.

![ip](https://cloud.githubusercontent.com/assets/17688443/25825135/29f54660-3418-11e7-8056-863d2a8f0807.png)

Para conectar com o terminal do Yocto vamos utilizar o programa [putty](http://www.putty.org/). Baixe e instale. 

Usando o SSH insira o endereço IP da placa e clique no botão 'Open'.  

![putty](https://cloud.githubusercontent.com/assets/17688443/25827234/89740222-3420-11e7-8cb0-38af568f6742.png)

Será aberta uma janela terminal do Yocto solicitando um login. Na primeira conexão aparecerá uma mensagem perguntando se você deseja armazenar as chaves de acesso dessa conexão. Clique em Yes. O login inicial da placa é o root. Portanto digite root e pressione a tecla enter. 

![sim](https://cloud.githubusercontent.com/assets/17688443/25825171/5481514e-3418-11e7-96af-a54cf298f493.png)

<a name="passo3"></a>
## 3º Passo: Executar programas pelo Putty:
Crie um arquivo chamado Final.py (tudo em minúsculas) ou baixe o código disponível neste mesmo repositório, e mova para o SD da placa. Conforme imagem:

![salvamento](https://cloud.githubusercontent.com/assets/17688443/25827558/3045f6d6-3422-11e7-9a12-1daec19dab54.png)

Pode ser utilizado qualquer editor, mas é muito importante manter a formatação, já que estamos lidando com códigos em Python:

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
``` 
Digite os seguintes comandos, no Putty para clonar o repositório do Paho-MQTT para python:

	git clone https://github.com/eclipse/paho.mqtt.python
	cd paho.mqtt.python
	python setup.py install 

Nesse programa em Python que vai acionar e monitorar a porta 5 do Galileo. O circuito é composto por 1 led e 1 resistores de 330 ohms, faça montagem conforme imagem abaixo:

![2](https://cloud.githubusercontent.com/assets/17688443/25826250/83551baa-341c-11e7-9322-1581b8be44d4.png)

Os arquivos salvos no SD são acessados no endereço em /media/card navegue pelo Linux usando os comandos:

- cd .. ``sair da pasta ``
- cd nome_da_pasta ``entrar na pasta ``
- ls ``ver o que tem na pasta``
- pwn ``ver em qual pasta está``

Navegue até encontrar o arquivo salvo o Final.py e execute usando o comando ``python Final.py`` 

![final](https://cloud.githubusercontent.com/assets/17688443/25825195/7ac410e4-3418-11e7-8d16-8025092bb820.png)

Se tudo estiver certo irá aparecer essas mensagens de conexão bem sucedida no prompt:

![sucesso](https://cloud.githubusercontent.com/assets/17688443/25826623/e06b29fa-341d-11e7-9627-da27cfd764ae.png)

Deixe o código executando enquanto realiza o proximo passo. 

<a name="passo4"></a>
## 4º Passo: Conexão com o MQTTLens:
O controle de estados do led será feito através de mesagens enviadas e recebidas do broker MQTTLens. Primeiramente adicione a extensão MQTTLens ao seu navegador Chrome pelo link: https://chrome.google.com/webstore/detail/mqttlens/hemojaaeigabkbcookmlgmdigohjobjm clique em "+ usar no chrome". Após instalado abra e adicione uma nova conexão no "+":

![mais](https://cloud.githubusercontent.com/assets/17688443/25826876/edb3e740-341e-11e7-95bf-e9a99df3c7a9.png)

Faça as sequintes modificações, e salve: 

![mqttcdfgv](https://cloud.githubusercontent.com/assets/17688443/25826947/43a6d3f6-341f-11e7-9b57-15f510280604.png)

Agora falta apenas configurar o tópico para o mesmo que o Galileo está mandando as mensagens:

![de](https://cloud.githubusercontent.com/assets/17688443/25827124/08cf6b70-3420-11e7-85e7-d30625fe988f.png)

E pronto, o broker está pronto para receber suas mensagens!! 
Você pode ligar o led digitando "on", desligar com "off" e saber seu estado atual com "state". Use a imaginação, aprimore o código e divirtar-se!
Caso o led não acenda verifique se sua polaridade está correta. Para parar a execução do código aperte ctrl+c no prompt.
