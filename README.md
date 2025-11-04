# 📘 Vledger — Inteligência para seus lançamentos contábeis

O **Vledger** é um sistema em Python com interface Streamlit que automatiza o preenchimento de contas **Débito** e **Crédito** a partir de um **extrato financeiro**. Ele identifica palavras-chave nas descrições das transações e cruza essas informações com uma **tabela de referência de contas contábeis**.

---

## 🚀 Funcionalidades principais

* Upload de **extratos bancários** (CSV ou Excel)
* Upload de **tabela de referência** de contas (CSV ou Excel)
* Identificação automática de **palavras-chave** nas descrições
* Preenchimento das colunas **Débito** e **Crédito** com base na referência
* Opções de correspondência:

  * Substring (padrão)
  * Palavra inteira
  * Expressão Regular (Regex)
* Modo **case sensitive** (opcional)
* Exportação dos resultados em **Excel (.xlsx)**
* Geração de um **modelo de referência** pronto para download

---

## 🧩 Estrutura do Projeto

```
Vledger/
│
├── Vledger_app.py          # Código principal do sistema
├── README_Vledger.md       # Documentação do projeto
├── referencia_modelo.csv   # Modelo de referência gerado pelo app (opcional)
└── requirements.txt        # Dependências (opcional)
```

---

## ⚙️ Instalação

### 1️⃣ Pré-requisitos

* Python 3.8 ou superior

### 2️⃣ Instale as bibliotecas necessárias

```bash
pip install streamlit pandas openpyxl
```

### 3️⃣ Execute o sistema

```bash
streamlit run Vledger_app.py
```

O sistema abrirá automaticamente no navegador (geralmente em `http://localhost:8501`).

---

## 🧮 Como usar

1. **Abra o Vledger**

   * Execute o comando acima e acesse a interface.

2. **Anexe os arquivos**

   * **Extrato**: planilha com colunas como Data, Descrição e Valor.
   * **Referência**: planilha com as colunas `Nome`, `Conta_D` e `Conta_E`.

3. **Configure o modo de correspondência** (Substring, Palavra inteira ou Regex)

4. **Clique em “Executar classificação”**

   * O sistema cruzará os dados e preencherá as contas Débito e Crédito.

5. **Baixe o resultado**

   * Faça download do arquivo final em formato Excel (.xlsx).

---

## 🧾 Exemplo de Tabela de Referência

| Nome        | Conta_D | Conta_E |
| ----------- | ------- | ------- |
| Intermedica | 282     | 537     |
| Amil        | 310     | 537     |
| Unimed      | 295     | 537     |
| Sulamerica  | 320     | 537     |
| Bradesco    | 400     | 537     |

---

## 💡 Exemplo de Resultado Gerado

| Data       | Descrição            | Valor  | Débito | Crédito |
| ---------- | -------------------- | ------ | ------ | ------- |
| 05/10/2025 | INTERMEDICA          | 5,00   | 282    | 537     |
| 06/10/2025 | ASHS INTERMEDICA ASA | 10,00  | 282    | 537     |
| 07/10/2025 | Amil                 | 2,00   | 310    | 537     |
| 07/10/2025 | Unimed               | 500,00 | 295    | 537     |

---

## 🧠 Ideias Futuras

* Edição manual das classificações diretamente na interface
* Fuzzy Matching (para detectar nomes parecidos)
* Aprendizado com correções do usuário
* Integração com SharePoint, Power BI ou sistemas contábeis
* Histórico de execuções e relatórios analíticos

---

## 👩‍💻 Autoria

Desenvolvido por **Lucilia Rosa**
💬 *Vledger — Inteligência para seus lançamentos contábeis*