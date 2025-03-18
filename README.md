# 🤖 Bot do Telegram com Integração Gemini

Este projeto é um bot do Telegram que processa imagens e textos usando a API Gemini. O bot pode lidar com mensagens contendo fotos com legendas ou mensagens de texto simples.

## 🌟 Funcionalidades

- Responde ao comando `/start` com uma mensagem de boas-vindas.
- Processa fotos com legendas fazendo upload da foto para o Gemini e gerando uma resposta baseada na imagem e no texto.
- Processa mensagens de texto simples enviando o texto para o Gemini e gerando uma resposta.
- Responde ao comando `/stop` para parar o bot.

## 🛠️ Configuração

1. Clone o repositório.
2. Crie um arquivo `.env` no diretório do projeto com as seguintes variáveis de ambiente:
    ```
    GEMINI_API_KEY=seu_api_key_do_gemini
    TELEGRAM_BOT_TOKEN=seu_token_do_bot_telegram
    ```
3. Instale as dependências necessárias:
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Executando o Bot

Para iniciar o bot, execute o seguinte comando:
```bash
python telegram_bot.py
```

## 📋 Uso

- Envie o comando `/start` para o bot para receber uma mensagem de boas-vindas.
- Envie uma foto com uma legenda para o bot para processar a imagem e o texto.
- Envie uma mensagem de texto simples para o bot para processar o texto.
- Envie o comando `/stop` para parar o bot.

## 📄 Registro de Logs

O bot registra eventos importantes e erros no console. O formato do log inclui o timestamp, nome do logger, nível do log e mensagem.

## ⚠️ Tratamento de Erros

O bot lida com erros de forma graciosa registrando os detalhes do erro e enviando uma mensagem de erro para o usuário.

## 📜 Licença

Este projeto está licenciado sob a Licença MIT.
