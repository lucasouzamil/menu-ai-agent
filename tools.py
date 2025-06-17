# ferramenta_busca.py
import json
from typing import List, Optional

# Carrega o cardápio do arquivo JSON uma única vez quando o módulo é importado
try:
  with open('cardapio.json', 'r', encoding='utf-8') as f:
    CARDAPIO = json.load(f)
except FileNotFoundError:
  print("Erro: O arquivo 'cardapio.json' não foi encontrado.")
  CARDAPIO = []
except json.JSONDecodeError:
  print("Erro: O arquivo 'cardapio.json' não é um JSON válido.")
  CARDAPIO = []

def buscar_refeicoes(
  keywords: Optional[List[str]] = None,
  tags: Optional[List[str]] = None,
  max_preco: Optional[float] = None,
  sort_by_price: str = "none" # Aceita "asc" para mais barato, "desc" para mais caro
) -> str:
  """
  Busca e filtra refeições do cardápio com base em palavras-chave, tags e preço máximo.

  Args:
    keywords: Uma lista de palavras-chave para buscar no nome e na descrição.
    tags: Uma lista de tags que a refeição deve ter (ex: 'vegano', 'picante').
    max_preco: O orçamento máximo para a refeição.
    sort_by_price: Ordena os resultados por preço. 'asc' para o mais barato, 'desc' para o mais caro.

  Returns:
    Uma string JSON contendo a lista de refeições encontradas (até 10) ou uma mensagem de "nenhum resultado".
  """
  print("Keywords: ", keywords)
  print("tags: ", tags)
  print("max_preco: ", max_preco)
  print("sort_by_price: ", sort_by_price)

  if not CARDAPIO:
    return json.dumps({"erro": "O cardápio não pôde ser carregado."})

  resultados_filtrados = CARDAPIO

  # 1. Filtrar por preço
  if max_preco is not None:
    resultados_filtrados = [
      item for item in resultados_filtrados if item.get('preco', 0) <= max_preco
    ]

  # 2. Filtrar por tags (deve conter TODAS as tags)
  if tags:
    resultados_filtrados = [
      item for item in resultados_filtrados
      if all(tag.lower() in [t.lower() for t in item.get('tags', [])] for tag in tags)
    ]

  # 3. Filtrar por palavras-chave (deve conter TODAS as palavras-chave no nome ou descrição)
  if keywords:
    resultados_filtrados = [
      item for item in resultados_filtrados
      if all(
        keyword.lower() in item.get('nome', '').lower() or
        keyword.lower() in item.get('descricao', '').lower()
        for keyword in keywords
      )
    ]

  # 4. Ordenar por relevância (neste caso, por preço se solicitado)
  if sort_by_price == "asc":
    resultados_filtrados.sort(key=lambda x: x.get('preco', float('inf')))
  elif sort_by_price == "desc":
    resultados_filtrados.sort(key=lambda x: x.get('preco', 0), reverse=True)

  # 5. Limitar a 10 resultados
  resultados_finais = resultados_filtrados[:10]

  if not resultados_finais:
    return json.dumps({"resultado": "Nenhuma refeição encontrada com esses critérios."})

  return json.dumps(resultados_finais, indent=2, ensure_ascii=False)