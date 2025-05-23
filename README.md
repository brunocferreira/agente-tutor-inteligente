# Agente Tutor Inteligente

## Descrição

Este projeto é um agente tutor inteligente que utiliza a API da OpenAI para fornecer assistência e informações para o processo de aprendizagem e reforço de conhecimento.

## Configuração do Ambiente

### Passos para Configuração

1. Clone este repositório para o seu ambiente local:
   ```bash
   git clone git@github.com:brunocferreira/agente-tutor-inteligente.git
   ```
2. Navegue até o diretório do projeto:
   ```bash
   cd agente-tutor-inteligente
   ```
3. Crie um ambiente virtual:
   ```bash
   python3 -m venv venv
   ```
4. Ative o ambiente virtual:
   ```bash
   source venv/bin/activate
   ```
5. Instale as dependências listadas no arquivo `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
6. Crie um arquivo `.env` no diretório raiz do projeto e adicione sua chave da OpenAI:
   ```Plaintext
   OPENAI_API_KEY=sua_chave_de_API_da_OpenAI
   ```

## Uso

Para iniciar o projeto, certifique-se de que seu ambiente virtual esteja ativado e execute o arquivo principal do projeto.

- Inicialize o streamlit para executar o projeto:

```bash
streamlit run main.py
```

### Material de apoio

Para os testes deste projeto, foi usado o e-book de **Cálculo é Fácil** do professor _Walter Ferreira Velloso Junior_, disponível no:

> [portal de livros da USP](https://www.livrosabertos.abcd.usp.br/portaldelivrosUSP/catalog/view/496/447/1723)

## Contribuição

Para contribuir com este projeto, por favor faça um fork do repositório e envie um pull request com suas alterações.

## Licença

Este projeto está licenciado sob a licença MIT. Consulte o arquivo LICENSE para obter mais informações.
