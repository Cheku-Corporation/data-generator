# Gerador de dados

Este gerador de dados pretende simular os dados enviados por um carro inteligente enquanto este faz a sua viagem. São gerados dados como a velocidade a que o veiculo se encontra, a sua localização atual, a mudança em que se encontra, as RPMs atuais, as quantidades de combustivel, óleo e água que o veiculo tem, pressão dos pneus, temperatura dos pneus e temperatura do motor, estado das luzes. Também são gerados acontecimentos aleatórios, como avarias do motor, falta de combustivel, paragem para abastecimento, mudança do estado das luzes, etc.
</br>

# Pré-requisitos

Pré-requisitos:
- _rabbitmq_
- _python_
- _pip_
- _venv_

1. Instalar o _rabbitmq_:
> Para que a geração de dados seja feito com sucesso é necessária a instalação do _rabbitmq_, para isso basta seguir as instruções no site oficial: https://www.rabbitmq.com/download.html .<br>
A nossa recomendação é correr a aplicação num container do docker, para isso basta correr o seguinte comando:
```bash
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.11-management
```


> Em outro terminal:
2. Criar o *virtual enviroment*:
```bash
$ python3 -m venv venv
```
3. Ativar o *virtual enviroment*:
```bash
$ source venv/bin/activate
```
4. Instalar as *dependências:
```bash
$ pip install -r requirements.txt
```
> As dependências que estão no ficheiro `requirements.txt` são o pika, que serve para realizar a conexão com o RabbitMQ e o numpy que serve para gerar probabilidades aleatórias.

</br>

# Execução

Antes de correr a aplicação é necessário verificar que os pré-requisitos estão a correr e que a porta do RabbitMQ é a correta.<br>
De forma a conseguirmos visualizar que os dados estão realmente a ser enviados para o RabbitMQ, podemos utilizar o _RabbitMQ Management_ que é uma interface web que nos permite visualizar as filas e os dados que estão a ser enviados para elas, ou então utilizar o `data_receiver.py` que foi personalizado para receber os dados das filas específicas do gerador.<br>

Existem 2 maneiras de correr a aplicação:
1. Correr o ficheiro `sensor_data_generator.py`:
```bash
$ python3 sensor_data_generator.py
```

2. Correr o ficheiro `run.sh`:
```bash
$ ./run.sh
```
> Antes de correr o ficheiro `run.sh` é necessário dar permissões de execução ao ficheiro:
```bash
$ chmod +x run.sh
```

<br>

# Configuração

## Execução utilizando diretamente o ficheiro `sensor_data_generator.py`
Para configurar o gerador de dados é possível passar diversos parametros para o ficheiro `sensor_data_generator.py`:
- `-ho`, `--host`: Host do RabbitMQ
- `-id`, `--id`: ID do carro que está a enviar os dados
- `-f`, `--fuel`: Nível de combustível inicial do carro
- `-w`, `--water`: Nível de água inicial do carro
- `-o`, `--oil`: Nível de óleo inicial do carro
- `-tt`, `--time_trips`: Tempo entre cada viagem
- `-ts`, `--time_speed`: Velocidade das paragens do carro (Quanto maior o valor, o carro ficará parado durante menos tempo)

<br>

### Os tipos de dados dos argumentos são:
- `-ho`: `str`
- `-id`: `int` - sendo que o valor tem de ser maior ou igual a 0
- `-f`: `float` - sendo que o valor tem de ser maior ou igual a 0 e menor ou igual a 100
- `-w`: `float` - sendo que o valor tem de ser maior ou igual a 0 e menor ou igual a 100
- `-o`: `float` - sendo que o valor tem de ser maior ou igual a 0 e menor ou igual a 100
- `-tt`: `float` - sendo que o valor tem de ser maior ou igual a 0 e menor ou igual a 100
- `-ts`: `float` - sendo que o valor tem de ser maior ou igual a 0 e menor ou igual a 100

<br>

### Nenhum Argumento é obrigatório, sendo que os valores por defeito são:
- `-ho`: `localhost`
- `-id`: `0`
- `-f`: `100`
- `-w`: `100`
- `-o`: `100`
- `-tt`: `30*60`
- `-ts`: `1`

<br>

Exemplo:
```bash
$ python3 sensor_data_generator.py -ho localhost -id 1 -f 100 -w 100 -o 100 -tt 10 -ts 10
```

<br>

## Execução utilizando diretamente o script `run.sh`
Ao executar o script python através do ficheiro run.sh também é possível passar os mesmos argumentos que são passados para o ficheiro `sensor_data_generator.py`, apesar de os parametros serem ligeiramente diferente:
- `-h`: Host do RabbitMQ
- `-i`: ID do carro que está a enviar os dados
- `-f`: Nível de combustível inicial do carro
- `-w`: Nível de água inicial do carro
- `-o`: Nível de óleo inicial do carro
- `-t`: Tempo entre cada viagem
- `-s`: Velocidade das paragens do carro (Quanto maior o valor, o carro ficará parado durante menos tempo)

<br>

Exemplo:
```bash
$ ./run.sh -w 20 -f 20 -o 20 -s 10000 -t 1 -h localhost -i 0
```

<br>

## Viagens

As viagens são algo que teve de ser pré-definido e encontram-se nos ficheiros do diretório `trips`. As viagens são sempre escolhidas aleatóriamente.

<br>

# Logs
O gerador de dados conta com um sistema de logs que nos permite visualizar o que está a acontecer durante a execução do programa, ou seja, permite visualizar as tentativas de conexão com o RabbitMQ, todas as mensagens que são enviadas, e o dia e a hora de cada acontecimento.
Os logs são guardados no diretório `logs` que é criado, caso não exista, e esses ficheiros de logs são guardados com o nome no formato `logfile_YYYY-MM-DD.log` e são gerados a cada dia que o gerador é utilizado.
<br>