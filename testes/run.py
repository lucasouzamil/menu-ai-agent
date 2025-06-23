import asyncio
from datetime import datetime
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from agents import Runner
from agente import agente_garcon


testes = [
  "Quero um prato apimentado, que tenha proteína",
  "Prato sem lactose de até R$55",
  "Refeição saudável com proteína, arroz e legumes",
  "Pratos veganos de até R$40",
  "Quero um almoço prático, sou intolerante a lactose",
  "Quero o prato mais barato"
]

async def executar_testes():
  data_execucao = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
  
  nome_arquivo_relatorio = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
  caminho_completo_relatorio = os.path.join(project_root+"/testes/outputs/", nome_arquivo_relatorio)

  print("Iniciando a execução dos testes automatizados...")
  with open(caminho_completo_relatorio, 'w', encoding='utf-8') as f:
    f.write("=" * 60 + "\n")
    f.write("    RELATÓRIO DE TESTES - AGENTE GARÇOM AI\n")
    f.write(f"    Executado em: {data_execucao}\n")
    f.write("=" * 60 + "\n\n")

    for i, pergunta in enumerate(testes):
      print(f"Executando teste {i+1}/{len(testes)}: '{pergunta}'")

      f.write(f"--- INÍCIO DO TESTE {i+1} ---\n\n")
      f.write(f"PERGUNTA: {pergunta}\n\n")
      
      try:
        resultado_run = await Runner.run(agente_garcon, pergunta)
        
        f.write("RESPOSTA DO AGENTE:\n")
        f.write("-" * 20 + "\n")
        f.write(resultado_run.final_output)
        f.write("\n" + "-" * 20 + "\n")

      except Exception as e:
        f.write(f"!!! OCORREU UM ERRO NESTE TESTE !!!\n")
        f.write(f"Erro: {str(e)}\n")

      f.write(f"\n--- FIM DO TESTE {i+1} ---\n\n")
      f.write("=" * 60 + "\n\n")

  print(f"\nTestes concluídos! Relatório salvo em: '{caminho_completo_relatorio}'")


if __name__ == "__main__":
  asyncio.run(executar_testes())