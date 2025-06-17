# agente.py
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from tools import buscar_refeicoes

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
  raise ValueError("A chave da API da OpenAI não foi encontrada. Defina a variável de ambiente OPENAI_API_KEY em um arquivo chamado `.env` na raiz do projeto.")
client = OpenAI(api_key=api_key)

print("API KEY: ", api_key)

tools = [{
  "type": "function",
  "function": {
    "name": "buscar_refeicoes",
    "description": "Busca refeições no cardápio com base em critérios como palavras-chave, restrições alimentares (tags) e orçamento.",
    "parameters": {
      "type": "object",
      "properties": {
        "keywords": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Lista de palavras-chave para buscar. Ex: ['proteína', 'arroz']"
        },
        "tags": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Lista de tags para filtros exatos. Ex: ['vegano', 'sem lactose', 'picante']"
        },
        "max_preco": {
          "type": "number",
          "description": "O preço máximo da refeição. Ex: 55.0"
        },
        "sort_by_price": {
          "type": "string",
          "enum": ["asc", "desc", "none"],
          "description": "Ordena os resultados. 'asc' para o mais barato, 'desc' para o mais caro."
        }
      },
      "required": []
    }
  }
}]

ASSISTANT_ID = "asst_v0g16vVo5PU3P4JHzPuGcdtd"

try:
  assistant = client.beta.assistants.retrieve(assistant_id=ASSISTANT_ID)
  print(f"Assistente existente (ID: {ASSISTANT_ID}) carregado.")
except Exception:
  assistant = client.beta.assistants.create(
    name="Assistente de Restaurante",
    instructions="""
    Você é um assistente de restaurante amigável e prestativo. Seu objetivo é ajudar os usuários a encontrar a refeição
    perfeita em nosso cardápio. Use a ferramenta `buscar_refeicoes` para encontrar pratos que correspondam aos pedidos 
    do usuário. Sempre que encontrar resultados, liste o nome, a descrição e o preço de cada prato. Se a busca não 
    retornar nenhum resultado, peça desculpas de forma amigável e talvez sugira uma busca mais ampla. Mantenha sempre um
    tom simpático e conversacional.""",
    tools=tools,
    model="gpt-4o",
  )
  ASSISTANT_ID = assistant.id
  print(f"Novo assistente criado com o ID: {ASSISTANT_ID}. Salve este ID para uso futuro.")

def main():
  print("\nOlá! 👋 Sou seu assistente de refeições. Como posso te ajudar hoje?")

  thread = client.beta.threads.create()

  while True:
    user_input = input("\nO que você procura? ")
    if user_input.lower() in ['sair', 'exit', 'quit']:
      print("Até logo! Bom apetite! 🍽️")
      break

    client.beta.threads.messages.create(
      thread_id=thread.id,
      role="user",
      content=user_input
    )

    print("\nAssistente:", end="", flush=True)
    try:
      with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=assistant.id
      ) as stream:
        for event in stream:
          if event.event == "thread.run.requires_action":
            run_id = event.data.id
            tool_calls = event.data.required_action.submit_tool_outputs.tool_calls
            
            tool_outputs = []
            for tool_call in tool_calls:
              if tool_call.function.name == "buscar_refeicoes":
                args = json.loads(tool_call.function.arguments)
                print(f"\n🤖 O Agente está buscando com os filtros: {args}")
                output = buscar_refeicoes(**args)
                tool_outputs.append({
                  "tool_call_id": tool_call.id,
                  "output": output,
                })
            
            # Envia o resultado da ferramenta de volta para o assistente em um stream
            with client.beta.threads.runs.submit_tool_outputs_stream(
              thread_id=thread.id,
              run_id=run_id,
              tool_outputs=tool_outputs,
            ) as tool_stream:
              # Apenas iteramos para garantir que a submissão foi processada
              for tool_event in tool_stream:
                pass

          # Evento: A resposta do assistente está sendo gerada token a token
          elif event.event == "thread.message.delta":
            for delta in event.data.delta.content:
              if delta.type == 'text' and delta.text:
                print(delta.text.value, end="", flush=True)
          
          # Adiciona uma nova linha no final da resposta completa do assistente
          print()
    except Exception as e:
      print(f"\nOcorreu um erro: {e}")

if __name__ == "__main__":
  main()