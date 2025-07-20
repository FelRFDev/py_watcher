# 🔍 PyWatcher - Dashboard de Monitoramento do Sistema (Django + Redis + WSL)

Este é um projeto de dashboard de monitoramento do sistema, desenvolvido com Django, que exibe o uso de CPU, RAM, disco, **temperatura de componentes (GPU, CPU, placa-mãe)** e outras informações do sistema operacional em tempo real. Utiliza Redis para comunicação assíncrona entre os processos e coleta os dados diretamente do sistema operacional. Também permite o monitoramento de **containers Docker** com suporte básico.

---

## 📌 Funcionalidades

- Monitoramento em tempo real de:
  - Uso de CPU (por núcleo)
  - Memória RAM
  - Disco
  - Processos ativos
  - Temperatura da CPU, GPU e placa-mãe (via OpenHardwareMonitor no Windows)
  - IP local e uptime do sistema
  - Detecção e monitoramento de containers Docker
- Atualização automática dos dados na interface (sem recarregar a página)
- Funciona com WSL2 no Windows para coletar dados do Ubuntu
- Suporte tanto para Windows quanto para Linux

---

## ⚙️ Como funciona

- O backend coleta os dados usando a biblioteca `psutil` (e `OpenHardwareMonitor` no Windows para temperaturas)
- Um script separado coleta os dados e envia para o Redis
- A view principal consome os dados via API
- A interface exibe os dados usando JavaScript e Chart.js com requisições AJAX
- Para temperaturas no Windows, os dados são extraídos de arquivos CSV gerados automaticamente pelo OpenHardwareMonitor

---

Requisitos:

- Python 3.10+
- Redis instalado e rodando
- Ambiente com Ubuntu (via WSL ou nativo) **ou Windows**
- Django
- OpenHardwareMonitor (no Windows, executado como administrador) Download: ([Clique aqui](https://openhardwaremonitor.org/downloads/))
- Docker (opcional, se quiser monitorar containers)

## 🧩 ANTES DE TUDO LEIA COM ATENÇÃO!

- ATENÇÃO, este procedimento é obrigatório para que possa ser feito a coleta de dados como temperatura e etc.


- Após baixar o OpenHardware, extraia os arquivos e mova a pasta para dentro da pasta raiz do projeto. Em seguida, execute o programa como administrador.
- Feito isso, vá até options e marque as opções "start minimized" e "log sensors"
- Ao executar o OpenHardware, ele gera um arquivo xml com os dados coletados. No arquivo consumer.py na pasta dashboard, 
vá até o método get_temperature_data e insira em REL_PATH o caminho(path) para a pasta do OpenHardware que está na raiz do projeto, finalizando assim este procedimento. Para obter o path, caso esteja no VSCODE basta clicar com o botão direito na pasta e clicar em CopyRelativePath. 


## 🚀 Instalação

### 1. Clone o projeto

```bash
git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo
```

### 2. Crie o ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate  # ou .\venv\Scripts\activate no Windows
```

### 3. Instale as dependências

Para usar no windows use:
```bash
pip install -r requirements.txt
```
Para usar no Linux use:

```bash
pip install -r requirements-linux.txt
```

## 🧠 Executando o Projeto

### 1. Inicie o Redis

Se estiver usando o Ubunto/WSL:

```bash
sudo service redis-server start
```

Ou diretamente com:

```bash
redis-server
```

> ❗ O Redis **é obrigatório** para funcionar corretamente com o WSL e para o fluxo de dados entre o script e o Django.

---

- PARA RODAR NO LINUX:

### 2. Abra 2 terminais e execute os comandos abaixo separadamente:

```bash
python manage.py runworker system_monitor
```

```bash
python dashboard/broadcast.py
```

---

### 3. Inicie o servidor Django em outro terminal

```bash
python manage.py runserver
```

Abra no navegador: http://127.0.0.1:8000

---

- PARA RODAR NO WINDOWS:

### 1. Inicie o Redis

Se estiver usando o WSL:

```bash
sudo service redis-server start
```

### 2. Inicie o servidor Django

```bash
python manage.py runserver
```

Abra no navegador: http://127.0.0.1:8000




## 📁 Estrutura do Projeto

```
├── dashboard/               # App principal do Django
│   ├── views.py             # Lógica de exibição
│   └── templates/           # HTMLs e dashboard
│
├── scripts/
│   └── data_collector.py    # Script que coleta e envia dados para Redis
│
├── static/                  # Arquivos estáticos como JS, CSS, imagens
│
├── requirements.txt
├── manage.py
└── README.md
```

---

## ❓ Dúvidas Frequentes

### Posso rodar esse projeto no Windows sem WSL?
> Sim, mas você não terá acesso a todos os dados do sistema como no Ubuntu. Para uso completo, recomenda-se usar WSL2.

### Por que preciso do Redis?
> O Redis serve como intermediário para armazenar os dados do sistema que estão sendo atualizados em tempo real. Sem ele, o Django não consegue acessar os dados atualizados pelo script externo.

### O projeto coleta dados da GPU?
> Sim porém, a coleta de dados da GPU/placa-mãe pode ser limitada por permissões ou pela ausência de suporte no `psutil`. Pode ser expandido com bibliotecas como `py3nvml` ou `lmsensors`.

---


## 👨‍💻 Autor

Felipe Rodrigues Fonseca (felrfdev) ([Porfolio](https://felrfdev.netlify.app))  
Projeto criado com fins educacionais, acadêmicos e para aprendizado contínuo.

---

## 🧾 Licença

Este projeto está licenciado sob a MIT License. Sinta-se livre para usar, modificar e compartilhar.