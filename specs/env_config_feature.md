# Spec: Env Config

## Objective
Use the api keys and secrets from the project's .env file for Google Geminin and Telegram apis.

## Background
The infoPipeline uses a Planner to manage stages which include a Planner, Researcher, Curator and Writer. The Researcher and Curator use Google's Gemini for search and making judements on relevance respecively. Telegram sends the results from the writer to Telegram. Gemini and Telegram secrets are contained in the .env file in this project. Read more at architecture.md 

## Values available
* GEMINI_API_KEY
* TELEGRAM_BOT_TOKEN
* TELEGRAM_CHAT_ID

## Behavior
- Access to Google Gemini uses the GEMINI_API_KEY stored in the .env file.
- Sending a message to Telegram uses the TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID keys stored in the .env file.

## Edge Cases
- .env file doesn't exist
- A key is missing from the .env file which you require for an external resource call.

## Failure Handling
- If the .env file is missing or the necessary key is missing throw an error to the caller.

## Acceptance Criteria
- All external API calls requiring a key, secret, or id gets loaded from the project's .env file

## Out of Scope
- Do not edit the .env file
- Do not call the Gemini API
- Do not send message via Telegram