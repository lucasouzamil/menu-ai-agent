import asyncio
from agente import agente_garcon
from agents import Runner
from openai.types.responses import ResponseTextDeltaEvent

async def main():
  print("=" * 80)
  print("Olá! Eu sou o Chef IA, seu assistente de recomendações.")
  print("Posso te ajudar a encontrar a refeição adequada para você no nosso cardápio.")
  print("(Digite 'sair' para encerrar o atendimento)")
  print("=" * 80)

  while True:

    user_input = await asyncio.to_thread(input, "\nO que você procura? ")

    if user_input.lower() == 'sair':
      print("Até mais! Volte sempre...")
      break

    if not user_input:
      continue

    try:
      print("Chef IA: Um minuto, estou pensando..\n")
      result = Runner.run_streamed(agente_garcon, user_input)
      async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
          print(event.data.delta, end="", flush=True)
      print('\n')

    except Exception as e:
      print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
  try:
    asyncio.run(main())
  except KeyboardInterrupt:
    print("\nEncerrando o agente...")