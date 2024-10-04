# Descrição do Projeto

Este repositório tem como objetivo gerar uma base de dados no formato .pkl com os projetos finalizados da plataforma [Catarse](https://www.catarse.me/) utilizando sua api aberta.

# Como Instalar

Para utilizar este repositório, recomenda-se criar um ambiente virtual ou utilizar um gerenciador de dependências, como o Poetry. Abaixo, estão as instruções para ambas as abordagens:

### Usando Poetry

1. Instale o Poetry via pipx:

   ```bash
   pipx install poetry
   ```
   
2. Navegue até o diretório do projeto:

   ```bash
   cd caminho/para/o/projeto
   ```
   
3. Instale as dependências:

   ```bash
   poetry install
   ```


### Usando Ambiente Virtual

1. Crie um ambiente virtual:
   ```bash
   python -m venv ambiente_virtual
   ```
   
2. Ative o ambiente virtual:
   - Em Linux ou macOS:

     ```bash
     source ambiente_virtual/bin/activate
     ```

   - Em Windows:

     ```bash
     ambiente_virtual\Scripts\activate
     ```
   
3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

# Gerando o Dataset

Se certifique que está dentro de um ambiente com as bibliotecas dependentes explicadas em [Como Instalar](#como-instalar), após isso, dentro da raiz do projeto, rode o seguinte comando:


```bash
python make_dataset\get_project_details.py
```

O consumo da API está travado em 300 requisições por minuto, mas o processamento das requisições podem variar de acordo com demais situações, o número de 300 requisições é o máximo que o arquivo está configurado para consumir em 1 minuto.

Após aguardar o final da execução do código, você terá o arquivo `project_details.pkl` como seu dataset, confira possíveis erros e a execução do código utilizando o arquivo `logs.txt` que será gerado conforme a execução do script.



