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

  return 'nao encontrei nada'
