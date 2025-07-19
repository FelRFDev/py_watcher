
# 🔍 System Monitor Dashboard (Django + Redis + WSL)

Este é um projeto de dashboard de monitoramento do sistema, desenvolvido com Django, que exibe o uso de CPU, RAM, disco e outras informações do sistema operacional em tempo real. Utiliza Redis para comunicação assíncrona entre os processos e coleta os dados diretamente do sistema operacional.

---

## 📌 Funcionalidades

- Monitoramento em tempo real de:
  - Uso de CPU (por núcleo)
  - Memória RAM
  - Disco
  - Processos ativos
  - IP local e uptime do sistema
- Atualização automática dos dados na interface (sem recarregar a página)
- Funciona com WSL2 no Windows para coletar dados do Ubuntu

---

## ⚙️ Como funciona

- O backend coleta os dados usando a biblioteca `psutil`
- Um script separado coleta os dados e envia para o Redis
- A view principal consome os dados via API
- A interface exibe os dados usando JavaScript e Chart.js com requisições AJAX

---

## 🧩 Requisitos

- Python 3.10+
- Redis instalado e rodando
- Ambiente com Ubuntu (via WSL ou nativo)
- Django

---

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

```bash
pip install -r requirements.txt
```

---

## 🧠 Executando o Projeto

### 1. Inicie o Redis

Se estiver usando o WSL:

```bash
sudo service redis-server start
```

Ou diretamente com:

```bash
redis-server
```

> ❗ O Redis **é obrigatório** para funcionar corretamente com o WSL e para o fluxo de dados entre o script e o Django.

---

### 2. Execute o coletor de dados

```bash
python scripts/data_collector.py
```

---

### 3. Inicie o servidor Django

```bash
python manage.py runserver
```

Abra no navegador: http://127.0.0.1:8000

---

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
> Ainda não. A coleta de temperatura de GPU/placa-mãe pode ser limitada por permissões ou pela ausência de suporte no `psutil`. Pode ser expandido com bibliotecas como `py3nvml` ou `lmsensors`.

---

## 📈 Futuras melhorias

- Suporte à leitura da temperatura da GPU e sensores da placa-mãe
- Painel separado para monitorar containers Docker
- Notificações em tempo real
- Histórico de uso e relatórios

---

## 👨‍💻 Autor

Felipe ([@felrfdev](https://www.instagram.com/felrfdev/))  
Projeto criado com fins educacionais, acadêmicos e para aprendizado contínuo.

---

## 🧾 Licença

Este projeto está licenciado sob a MIT License. Sinta-se livre para usar, modificar e compartilhar.
