Esse projeto representa um dispositivo fictício de uma lâmpada inteligente, onde esse dispositivo pode ser ligado/desligado. Esse dispositivo fictício pode ser replicado, ou seja, pode-se conectar múltiplas lâmpadas no ambiente IoT do projeto, onde eles são conectados usando o **IoT Agent JSON** da plataforma FIWARE. Esse IoT Agent permite que as medições (tempo que a lâmpada está desligada) possam ser lidas e os comandos possam ser enviados usando solicitações NGSI-v2 ao **Orion Context Broker**, um outro componente da plataforma FIWARE, no caso o Broker.

Além do **FIWARE IoT Agent JSON** e do **FIWARE Orion Context Broker**, esse projeto também conta com o **FIWARE Cygnus**, um ativador genérico que é usado para persistir dados de contexto em bancos de dados terceiros. Esses dados podem ser recuperados e visualizados em um dashboard que foi desenvolvimento com a aplicação web de dashboard chamado Grafana.

## Requisitos

> [!WARNING] 
> Para rodar o projeto, é necessário cumprir os seguintes requisitos 
 
1. Instale o [Docker](https://docs.docker.com/get-docker/), [Docker Compose](https://docs.docker.com/compose/install/) e [Postman](https://www.postman.com/downloads/).
2. Clone esse repositório com `git clone https://github.com/caiovelp/smartpower.git`
3. Importe o [arquivo](documentation/smartpower.postman_collection.json) do postman que se encontra no repositório para o Postman.
4. Certifique-se que o Docker está rodando, caso esteja usando Windows basta abrir o Docker Desktop. Se estiver usando o Linux pode fazer o seguinte:
	1. `sudo systemctl status docker` - Isso mostrará o status atual do serviço Docker, caso o serviço não esteja rodando basta rodar o `sudo systemctl start docker`.
5. Abra a collection importada anteriormente para o Postman.

## Arquitetura

![arquitetura.png](images%2Farquitetura.png)

- Lâmpadas Inteligentes: Atualmente no projeto, esses dispositivos são simulados através de servidor da Web feito com FLASK. O Broker recebe através do IoT Agent a informação de que a lâmpada foi ligada/desligada. Se a lâmpada estiver ligada, a cada 5 segundos aproximadamente ela envia para o Broker, através do IoT Agent, o intervalo de 5 segundos que ela está ligada.
- FIWARE IoT Agent for JSON: Funciona como uma ponte de comunicação entre os dispositivos e o Context Broker. Utiliza um protocolo baseado em codificação JSON (pares atributo, valor). O Agent é utilizado para facilitar a interação dos dispositivos com o sistema de armazenamento. Ele converte as informações recebidas das lâmpadas (recebidas no formato JSON) em solicitações NGSI-v2, e as envia para o Broker.
- FIWARE Orion Context Broker: É o Broker da plataforma FIWARE. Ele fornece a funcionalidade de gerenciamento de informações de contexto. No caso, temos os publishers (geradores de dados) e consumers (usam os dados dos publishers para alguma finalidade), e os brokers em geral atuam como um mediador entre ambos. No caso da SmartPower, o publisher são as lâmpadas inteligentes e o consumer é o Dashboard, pois ele utiliza os dados provenientes das lâmpadas para montar a visualização de gráficos. Essas informações passam pelo IoT Agent que conversa em NGSI-v2 para o broker, e este utiliza o **MongoDB** para armazenar as informações de dados de contexto, como: entidades de dados, assinaturas e registros.
- FIWARE Cygnus: Esse componente é responsável pela persistência de dados. Com ele é possível realizar uma assinatura no contexto do broker, e essa assinatura faz a validação necessária para persistir os dados em banco de dados externo, no caso o **MySQL**.
- Grafana: É uma aplicação web que facilita a criação de visualização de dashboard. No caso, utilizados o grafana para possibilitar essa visualização de dados em desenvolvimento, na aplicação em produção esses dashboard seriam desenvolvidos pelo time do SmartPower, podendo ou não usar as visualizações do Grafana como inspiração. É interessante notar que o Grafana consulta apenas o banco de dados externo ao contexto da plataforma IoT, ou seja, ele consulta o banco de dados que a plataforma Cygnus está persistindo os dados.

## Comunicação entre dispositivos, IoT Agent, Orion Context Broker e Cygnus.
É importante entender que as mensagens trocadas entre cada um dos componentes possuem dois tipos principais de comunicação: Mensagem Norte (medições) e Mensagem sul (Comandos).

### Mensagem Sul (Comandos)
1. A mensagem é uma solicitação PATCH para o **Orion Context Broker**. Quando o broker recebe a mensagem de solicitação, ele encaminha a mensagem para o **IoT Agent** como uma solicitação POST.
2. Quando o **IoT Agent** recebe esta mensagem, ele envia uma resposta ao **Orion Context Broker** indicando que o comando está PENDENTE porque o **Agente IoT JSON** ainda não enviou uma mensagem ao dispositivo ou não encontrou um erro como, por exemplo, um dispositivo não está registrado.
3. No momento do cadastro do dispositivo, um dos parâmetros é o endpoint de comunicação que o **IoT Agent** irá utilizar para se comunicar com o dispositivo. Portanto, após a etapa 2, o agent envia uma solicitação POST para o dispositivo constando o comando que está sendo executado e o valor referente para esse comando. Por exemplo, para uma lâmpada temos o comando "switch" que indica que a lâmpada foi ligada ou desligada.
4. Quando o dispositivo recebe a mensagem anterior, ele deve manipular o comando. Esta lógica deve ser implementada no dispositivo. Quando o comando for concluído, o dispositivo deverá responder ao **Agente IoT JSON** com o código de status apropriado (200 se estiver ok, por exemplo) e um corpo de mensagem com o status do comando. 
5. Quando o **Agente IoT JSON** recebe a mensagem anterior, ele envia de volta ao **Orion Context Broker** para atualizar o atributo com as informações retornadas na mensagem anterior.
### Mensagem Norte (Medições)
1. O dispositivo envia uma medição para o **Agente IoT JSON** com os parâmetros `k` (chave secreta) e `i` (ID do dispositivo no **Agente IoT**) na URL. O corpo da mensagem é o valor das medidas com o nome no **Orion Context Broker** ou no **Agente IoT JSON**.
2. O **Agente IoT JSON** encaminha as medições para o **Orion Context Broker**. Essa mensagem é semelhante a uma solicitação PUT para atualizar o valor de atributos específicos no **Orion Context Broker**.
3. Em sequência, o broker checa as assinaturas feita pelo **Cygnus** e notifica esse componente caso essa assinatura seja validada, e a cada notificação enviada ao Cygnus, temos a persistência de dados acontecendo, ou seja, 1 linha com as informações desse dispositivo sendo inseridas no banco de dados.
## Rodando o projeto


1. Execute o docker.
2. Na pasta do projeto execute o seguinte comando: `docker compose up` - Esse comando deve ser executado no mesmo diretório do arquivo docker-compose.yml. 
> [!NOTE] 
> Todas as requisições estão configuradas no Postman. 
3. ***Execute a requisição "Criar um serviço"*** para criar um serviço no Orion, permitindo que dispositivos possam ser adicionados ao broker. 

  > [!IMPORTANT] 
> Se tudo estiver funcionando corretamente, essa requisição retornará como resposta o status *201 Created*. 

4. ***Execute a requisição "Provisionar um dispositivo"*** para provisionar um dispositivo no **IoT Agent**. Nessa requisição identificamos o dispositivo como uma entidade, por isso deve-se fornecer um id, nome (No caso, se chama Device:001) e tipo desse entidade. Além disso, também informamos para o **IoT Agent** o endpoint por qual esse dispositivo irá se comunicar e os atributos, que são leituras ativas do dispositivo (Ou seja, cada dispositivo irá enviar dados periodicamente para o **IoT Agent**). Nessa requisição também informamos ao agente de contexto os comandos referentes ao dispositivo provisionado e atributos estáticos, que como o nome sugere, são dados estáticos sobre o dispositivo (como relacionamentos) - Após o envio dessa requisição, o Agente IoT pode mapear os atributos antes de gerar uma solicitação com o **Orion Context Broker**. 

   > [!IMPORTANT] 
> Se tudo estiver funcionando corretamente, essa requisição retornará como resposta o status *201 Created*. 

5. Para ter certeza que o dispositivo foi provisionado corretamente para o IoT Agent, podemos mandar uma requisição para o broker pedindo as informações do dispositivo cadastro. ***Execute a requisição "Obter dispositivo - Device 001"*** para obter as informações do Dispositivo 1 registrado no **Orion Context Broker**.

> [!IMPORTANT] 
> Se tudo estiver funcionando corretamente, essa requisição retornará como resposta o status ***200 OK*** com o seguinte corpo na resposta:
> ``` 
> {
> 	"id": "urn:ngsi-ld:Device:001",
> 	"type": "Device",
> 	"switch": "",
> 	"interval": ""
> }
> ```
O corpo nos mostra da requisição nos dá 4 informações que foram cadastradas no momento que esse dispositivo foi provisionado: O id dessa entidade, o tipo dessa entidade e os comandos associados a ela nesse momento. Como no momento essa entidade apenas está cadastrada e nada foi feito referente a ela até esse momento, os valores referentes aos comandos estão nulos e os atributos dessa entidade sequer aparecem. 
Com isso, o **Orion Context Broker** foi informado que os comandos estão disponíveis, ou seja, o IoT Agent se registrou como um provedor de contexto para os atributos de comando. Uma vez cadastrados os comandos, será possível ativá-los enviando requisições ao broker, ao invés de enviar requisições JSON diretamente aos dispositivos IoT como fizemos anteriormente. 

6. ***Execute a requisição "Enviar comando via Orion Context Broker"***. Essa solicitação envia um comando ao Orion Context Broker, no caso o comando "switch". É como se fosse a requisição para a lâmpada ligar/desligar. O **Orion Context Broker** sabe que o device001 está registrado no **Agente IoT** e encaminha esta mensagem para ele. O **Agente IoT** sabe que o endpoint do dispositivo é capaz de lidar com esta mensagem, então ele envia uma solicitação POST com o comando, no caso o switch, no corpo da mensagem:
   ```
   {
	   "switch":""
   }
   ```
7. Assim que o contêiner que emula um dispositivo recebe essa mensagem, ele começa a enviar a cada 5s que a lâmpada está ligada para o agent (Se a lâmpada for desligada, esse processo é interrompido). Um outro comando possível é o interval, que pode alterar esse intervalo de tempo que as informações estão sendo enviadas. Para observer esse comportamento, ***Execute a requisição "Obter dispositivo - Device 001"*** . Você perceberá que a cada 5s o valor armazenado vai ser alterado, porém sempre será algo em torno de 5.00s.
   
> [!IMPORTANT] 
> Se tudo estiver funcionando corretamente, essa requisição retornará como resposta o status **200 OK** com o seguinte corpo na resposta:
> ```
> {
> 	"id": "urn:ngsi-ld:Device:001",
> 	"type": "Device",
> 	"TimeInstant": "2023-12-12T17:50:28.682Z",
> 	"refRoom": "urn:ngsi-ld:Room:001",
> 	"switch_info": "Lamp turned on",
> 	"switch_status": "OK",
> 	"time_on": 5.005209,
> 	"switch": "",
> 	"interval": ""
> }
> ```
> O corpo da resposta nos mostra mais informações agora, e no caso os valores para "switch_info" representa se a lâmpada está ligada ou desligada e o "time_on" é o intervalo de tempo entre uma mensagem e outra que aquela lâmpada estava ligada, nunca maior que 5 segundos (aproximadamente). 

8. É importante destacar que esses dados não estão sendo persistidos ainda, pois ainda não foi criado uma assinatura de contexto do **Orion Context Broker** para ele se comunicar com o Cygnus, para isso é necessário que uma assinatura seja criada. ***Executa a requisição "Criar uma assinatura"*** para tal finalidade. Essa assinatura, em específico, é para a persistência de dados do dispositivo 001 e isso é facilmente visualizado no corpo da requisição dessa assinatura. 
   
   > [!IMPORTANT] 
> Se tudo estiver funcionando corretamente, essa requisição retornará como resposta o status **200 OK**. 

9. ***Execute a requisição "Obter assinaturas"*** para verificar que a requisição foi criada com sucesso.
   Se tudo estiver funcionando corretamente, essa requisição retornará como resposta o status **200 OK**, além do corpo na resposta conter informações sobre essa assinatura como: status, entidades associadas, condições de validação, além de informações sobre a notificação, inclusive quantas vezes ela foi chamada.
10. Para verificar que a persistência de dados está ocorrendo, você pode executar o seguinte comando no terminal:
     `docker exec -it  db-mysql mysql -h mysql-db -P 3306  -u root -p123`
     Esse comando acessa o banco de dados que está sendo executado no container do docker. Dentro do banco de dados, execute:
	     1. `SHOW SCHEMAS;
	     2. `USE openiot;`
	     3. `SHOW tables FROM openiot;` - Deve aparecer a tabela com o nome do dispositivo - *urn_ngsi-ld_Device_001_Device*
	     4. `SELECT recvtime, attrName, attrValue FROM `urn_ngsi-ld_Device_001_Device` ORDER BY recvTime ASC;` 
	        
> [!IMPORTANT] 
> Se tudo estiver funcionando corretamente, o retorno dessa query será a tabela com todos os dados, e se você rodar essa consulta a cada 5 segundos, notará que 1 nova linha é adicionada. A consulta foi construída para que as últimas adições da tabela apareçam mais abaixo. 

11.  Acesse o grafana no `localhost:3000` para a visualização dos dashboard. Para fazer o login, basta entrar com admin e admin (usuário e senha), e não precisar alterar a senha como solicitado, basta clicar no  "skip". Na primeira execução do projeto, o container vai ser criado apenas com a conexão com os bancos, não vai existir nenhum dashboard criado, logo para visualizar o dashboard os passos são os seguintes:
	1. Menu no canto esquerdo superior (ao lado de 'Home').
	2. Dashboards.
	3. New, no canto direito superior > Import
	4. Seleciona o arquivo dummy.json na pasta do projeto, o caminho é provisioning/dashboards/dummy.json.
	5. Caso o dashboard for importado com sucesso, quando você abrir a visualização verá algo do tipo:
	   ![dashboard.png](images%2Fdashboard.png)
	

## Dashboards

Basicamente, foram construídos 2 visualizações: A primeira mostra um heatmap com informação de data e hora que lâmpada esteve ligada, e a segunda mostra uma tabela com informações agrupados por mês de tempo total de lâmpada ligada e o custo que isso representa na conta de luz. 

### Dashboard com dados Mockados
Para uma melhor visualização, criamos uma tabela com dados mockados, para visualizar esse dashboard basta importar o arquivo mock.json.

Para gerar esses dados, basta fazer o seguinte:
1) `python3 ./mock/populate_database.py > populate_database.sql` - Esse comando roda o script populate_database.py e salva a saída no arquivo populate_database.sql. No projeto, esse arquivo existe e já tem as linhas necessárias para popular a tabela com dados mockados.
2) Na instância do MySQL dentro do docker, basta executar os seguintes comandos:
	1. `create schema smartpower_mock;`
	2. `use schema smartpower_mock;`
	3. `create table lamp01;`
	4. Copiar e colar todo o conteúdo do arquivo populate_database.sql.


