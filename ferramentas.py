import json
from typing import List, Optional
from agents import function_tool

@function_tool
def buscar_cardapio(
  preco_maximo: Optional[float] = None,
  tags: Optional[List[str]] = None,
  palavras_chave: Optional[List[str]] = None,
  ordenar_por_preco: Optional[str] = None
) -> str:
  print("preco_maximo: ", preco_maximo)
  print("tags: ", tags)
  print("palavras_chave: ", palavras_chave)
  print("ordenar_por_preco: ", ordenar_por_preco)

  try:
    with open('cardapio.json', 'r', encoding='utf-8') as f:
      cardapio = json.load(f)
  except FileNotFoundError:
    return json.dumps({"erro": "Arquivo cardapio.json não encontrado."})

  resultados = []
  for item in cardapio:
    pontuacao = 0
    corresponde_criterios = True

    if preco_maximo is not None and item['preco'] > preco_maximo:
      corresponde_criterios = False

    if tags:
      tags_item = [t.lower() for t in item['tags']]
      if not all(tag.lower() in tags_item for tag in tags):
        corresponde_criterios = False
      else:
        pontuacao += len(tags) * 2

    if palavras_chave:
      conteudo = f"{item['nome']} {item['descricao']}".lower()
      if not all(palavra.lower() in conteudo for palavra in palavras_chave):
        corresponde_criterios = False
      else:
        pontuacao += len(palavras_chave)

    if corresponde_criterios:
      resultados.append({'item': item, 'pontuacao': pontuacao})

  if not resultados:
    return json.dumps({"mensagem": "Nenhum prato encontrado com esses critérios."})

  resultados.sort(key=lambda x: x['pontuacao'], reverse=True)

  if ordenar_por_preco == 'asc':
    resultados.sort(key=lambda x: x['item']['preco'])
  elif ordenar_por_preco == 'desc':
    resultados.sort(key=lambda x: x['item']['preco'], reverse=True)

  pratos_finais = [r['item'] for r in resultados]

  return json.dumps(pratos_finais[:10], indent=2, ensure_ascii=False)
