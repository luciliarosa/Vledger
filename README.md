# ⚙️ Vledger — Sistema de Classificação Contábil Automatizada

O **Vledger** é um sistema desenvolvido em **Python + Streamlit** para auxiliar na **classificação contábil automatizada de lançamentos bancários**.  
Ele permite cadastrar **empresas**, definir **referências contábeis** (plano de contas) e classificar **extratos bancários** automaticamente, armazenando todos os dados em um banco **SQLite**.

---

## 🚀 Funcionalidades Principais

- 📁 Cadastro e gestão de **empresas**
- 🔗 Cadastro de **referências contábeis** (relação descrição → débito/crédito)
- ⚙️ **Classificação automática** de extratos (CSV ou XLSX)
- 💾 Armazenamento de classificações no banco de dados local (`vledger.db`)
- 📊 Exibição de classificações agrupadas por **ano e mês**
- 📤 Exportação de classificações em Excel (.xlsx)
- 🧩 Interface totalmente interativa via **Streamlit**

---

## 🧠 Estrutura Geral do Projeto

📂 Vledger/
├── app.py
├── pages/
│ ├── empresas.py
│ ├── referencias.py
│ └── classificacao.py
├── vledger.db
├── requirements.txt
└── README.md

yaml
Copiar código

---

## 🧩 Banco de Dados: `vledger.db`

O sistema utiliza **SQLite** para armazenar todos os dados localmente.  
As principais tabelas são:

### 🏢 `empresas`
| Campo | Tipo | Descrição |
|-------|------|------------|
| id | INTEGER | Chave primária |
| nome_empresa | TEXT | Nome da empresa |
| cnpj | TEXT | CNPJ da empresa (opcional) |
| responsavel | TEXT | Nome do responsável |

---

### 📘 `referencias`
| Campo | Tipo | Descrição |
|-------|------|------------|
| id | INTEGER | Chave primária |
| empresa_id | INTEGER | ID da empresa (chave estrangeira) |
| nome | TEXT | Nome ou palavra-chave para busca na descrição |
| conta_d | TEXT | Conta de débito |
| conta_e | TEXT | Conta de crédito |

---

### 📚 `classificacoes`
| Campo | Tipo | Descrição |
|-------|------|------------|
| id | INTEGER | Chave primária |
| empresa_id | INTEGER | ID da empresa |
| descricao | TEXT | Descrição da movimentação |
| debito | TEXT | Conta de débito atribuída |
| credito | TEXT | Conta de crédito atribuída |
| valor | REAL | Valor do lançamento |
| data_movimento | TEXT | Data original do movimento |
| data_processamento | TEXT | Data/hora em que foi classificado |

---

## ⚙️ Instalação e Configuração

### 1️⃣ Clonar o projeto
```bash
git clone https://github.com/seu-usuario/vledger.git
cd vledger
2️⃣ Criar ambiente virtual (opcional, mas recomendado)
bash
Copiar código
python -m venv .venv
.venv\Scripts\activate   # (no Windows)
3️⃣ Instalar as dependências
Crie o arquivo requirements.txt com o seguinte conteúdo:

nginx
Copiar código
streamlit
pandas
openpyxl
E instale com:

bash
Copiar código
pip install -r requirements.txt
4️⃣ Executar o sistema
bash
Copiar código
streamlit run app.py
O navegador abrirá automaticamente em:
👉 http://localhost:8501

🖥️ Como Usar
🏢 Página Empresas
Cadastre as empresas que terão classificações.

Cada empresa tem seu próprio conjunto de referências e classificações.

🔗 Página Referências
Cadastre as palavras-chave que o sistema deve procurar nas descrições dos lançamentos.

Para cada palavra, informe a conta de débito e a conta de crédito correspondentes.

Exemplo:

Nome (descrição)	Conta Débito	Conta Crédito
PIX Recebido	1.1.1	3.1.1
Pagamento Fornecedor	2.1.3	1.1.1

⚙️ Página Classificação
Selecione a empresa desejada.

Faça o upload do extrato (CSV ou XLSX).

O sistema tentará classificar automaticamente com base nas referências cadastradas.

Visualize o resultado e clique em 💾 Salvar classificações no banco.

Os lançamentos serão gravados na tabela classificacoes.

Você pode consultar o histórico agrupado por Ano → Mês.

🧾 Formato Esperado do Extrato
O arquivo deve conter pelo menos uma coluna de descrição e uma coluna de valor.
O sistema identifica automaticamente o nome das colunas (ex: “Descrição”, “Histórico”, “Valor”, “Data”).

Exemplo:

Data	Descrição	Valor
01/01/2024	PIX Recebido de João	150.00
03/01/2024	Pagamento Fornecedor XPTO	-500.00

🧰 Como visualizar o banco vledger.db
Você pode inspecionar os dados usando o DB Browser for SQLite (gratuito).

Passos:
Abra o programa DB Browser for SQLite

Clique em “Abrir Banco de Dados”

Selecione o arquivo vledger.db

Vá até a aba “Navegar pelos dados”

Escolha a tabela: empresas, referencias ou classificacoes

Dica: use o botão “Executar SQL” para rodar consultas, por exemplo:

sql
Copiar código
SELECT * FROM classificacoes ORDER BY data_processamento DESC;
📤 Exportação
Após a classificação, é possível:

Baixar o arquivo classificado em Excel (.xlsx)

O nome do arquivo segue o formato:

php-template
Copiar código
classificacao_<empresa>_<datahora>.xlsx
🧑‍💻 Tecnologias Utilizadas
Python 3.12+

Streamlit (interface web)

Pandas (manipulação de dados)

SQLite3 (banco de dados local)

OpenPyXL (para leitura/escrita de Excel)

🧩 Futuras melhorias
Implementar exclusão/edição de classificações

Adicionar filtros e buscas avançadas

Relatórios contábeis automáticos

Integração com Power BI ou Excel Online

✍️ Autoria
Desenvolvido por: Lucilia dos Passos Rosa
📅 Projeto Vledger — 2025
💼 Sistema interno para classificação contábil inteligente.