# Agente de IA para Recomendação de Refeições

## Visão Geral do Projeto

Este repositório contém a implementação de um agente conversacional de IA, desenvolvido como solução para o "Case - Agente IA". O objetivo é fornecer um assistente que recomenda refeições de um cardápio local (arquivo `cardapio.json`) com base nas solicitações do usuário em linguagem natural.

O projeto utiliza o [Agents SDK](https://openai.github.io/openai-agents-python/) da OpenAI que se estende da [Responses API](https://openai.com/index/new-tools-for-building-agents/) requerida no case. Para consulta e classificação dos pratos foi feita uma tool de busca que o agente interage.

## 1. Instalação e Configuração do Ambiente

### Pré-requisitos

* Python 3.9 ou superior
* Git

### Passos para Instalação

#### Clonar o Repositório

```bash
git clone https://github.com/lucasouzamil/case-trela-ai-agent
cd case-trela-ai-agent
```

#### Criar e Ativar um Ambiente Virtual

```bash
# Criar o ambiente
python -m venv .venv

# Ativar no Windows
.\.venv\Scripts\activate

# Ativar no macOS/Linux
source .venv/bin/activate
```

#### Instalar as Dependências

```bash
pip install -r requirements.txt
```

#### Configurar a Chave da API

* Renomeie o arquivo `.env.example` para `.env`.
* Abra o arquivo `.env` e insira a chave da API:

```
OPENAI_API_KEY="sk-..."
```


## 2. Como Executar

O projeto possui duas formas de execução: um modo interativo e uma suíte dos testes pedidos no case.

### Executando o Agente Interativo

Para conversar diretamente com o agente no terminal, execute o arquivo `main.py`.

```bash
python main.py
```

### Executando os Testes

Para validar o comportamento do agente em todos os cenários do case, execute o script de testes localizado na pasta `/testes`. O script gerará um relatório (`test_AAAAMMDD_HHMMSS.txt`) na pasta `testes/outputs`.

```bash
python testes/run.py
```

## 3. Desafio Principal e Solução

O maior desafio do case foi garantir que o agente de IA utilizasse a ferramenta de busca (`buscar_cardapio`) adequadamente. Nas primeiras tentativas, o agente tinha dificuldades para traduzir a intenção do usuário (ex: "quero algo com proteína") em argumentos que a ferramenta pudesse usar para filtrar o `cardapio.json`, que não possuía tags explícitas para todos os conceitos.

A solução foi feita com uma simples engenharia de prompts:

### Consciência do Contexto de Dados

O prompt do agente é enriquecido no início da execução com a lista de todas as tags disponíveis extraídas do `cardapio.json`. Isso fornece um "mapa" do universo de filtros que ele pode usar ao invés de chutar uma tag que não existe no conjunto.

### Instruções Explícitas e Mapeamento Semântico

O prompt foi reestruturado para dar ao agente regras claras e hierárquicas sobre como usar a ferramenta:

* **Regra para Tags:** O agente é instruído a usar o filtro de tags apenas com as tags disponíveis.
* **Regra para Palavras-Chave:** Para conceitos que não são tags (como "proteína" ou "saudável"), o agente é instruído a usar o filtro de `palavras_chave` com uma lista de sinônimos ou ingredientes correspondentes (ex: `['frango', 'carne', 'peixe']` para "proteína").
* **Regra de Exceção:** Para conceitos subjetivos e não-buscáveis (como "prático" ou "rápido"), o agente é explicitamente instruído a ignorá-los.

## 4. Ordenação por Relevância (Sistema de Pontuação)

Para cumprir o requisito de "ordenar por relevância", a ferramenta `buscar_cardapio` têm um sistema de pontuação. Quando um prato corresponde aos critérios de busca, ele recebe pontos:

* **Correspondência de Tags:** Recebe uma pontuação maior (2).
* **Correspondência de Palavras-Chave:** Recebe uma pontuação menor (1).

Os resultados são ordenados em ordem decrescente por essa pontuação.

## 5. Análise da Evolução dos Testes

### Cenário Inicial (Primeira Execução)

No primeiro relatório de testes, o agente falhou no Teste 5: **"Quero um almoço prático, sou intolerante a lactose"**.

* **Análise:** O agente identificou corretamente a necessidade da tag `sem lactose`, mas, sem uma instrução específica, tratou "prático" como uma palavra-chave literal. Como nenhum prato "sem lactose" continha a palavra "prático" em sua descrição, a busca não retornou nada.

### Cenário Final (Segunda Execução)

Após a refatoração das intruções do agente, que incluiu a regra para ignorar conceitos subjetivos, a segunda execução dos testes se mostrou funcional.

* **Análise:** No mesmo Teste 5, o agente agora seguiu a nova regra: ignorou a palavra "prático" e focou no critério concreto "intolerante a lactose". Como resultado, ele chamou a ferramenta de busca apenas com o filtro relevante (`tags=['sem lactose']`) e forneceu uma lista útil de pratos.

## 6. Análise e Evolução do Protótipo

Durante o desenvolvimento deste protótipo, que é funcional e atende às instruções do case, me surgiram alguns questionamentos sobre quais seriam as melhores abordagens para uma implementação real em um ambiente de produção, caso eu precisasse colocá-lo em prática. Apesar de adequado dentro do escopo proposto, a solução apresentada neste projeto provavelmente não seria a mais adequada para um sistema em escala, com um catálogo maior e requisitos de performance e custoso.

### Abordagem 1: Classificação Com Um LLM (Inviável em Escala)

Uma primeira alternativa seria enviar o catálogo de produtos inteiro (o arquivo JSON) junto com a pergunta do usuário no mesmo prompt, pedindo ao LLM para analisar e retornar os itens mais relevantes.

Apesar de funcional para o pequeno conjunto de dados do teste, esta abordagem é inviável para um ambiente de produção por duas razões:
-   **Custo:** Com um catálogo de milhares de produtos, o número de tokens em cada chamada à API seria enorme, o que aumentaria e muito o custo do uso da API.
-   **Latência:** O tempo de processamento para uma janela de contexto deste tamanho geraria uma espera significativa para o usuário.

### Abordagem 2: Engenharia de Prompt (Implementada)

A solução adotada por mim neste case foi um *meio-termo*, focado em "ensinar" o agente a ser um especialista em buscas dentro de um conjunto de dados fixo. Em vez de o LLM analisar todos os produtos, ele aprende é instruído a traduzir a linguagem do usuário em parâmetros para uma ferramenta de busca específica (`buscar_cardapio`).

O principal ponto desta solução é um prompt que:
1.  Sempre informado sobre as **tags de filtro existentes** disponíveis no catálogo a cada chamada do agente.
2.  Contém **regras** para traduzir conceitos semânticos (como "saudável" ou "proteína") para buscas por palavras-chave.
3.  Instrui o agente a **ignorar termos subjetivos** ("prático", "rápido") que não têm correspondência nos dados.

### Abordagem 3: Estruturar os Dados (A Solução Ideal para a Trela)

Supondo que a Trela possui controle total sobre seu catálogo de produtos, a solução mais escalável e eficiente seria enriquecer os dados.

Em vez de depender da engenharia de prompt se adequar a um JSON genérico, os produtos no banco de dados da Trela poderiam ser estruturados com campos para busca, como `categorias`, `tags_dieteticas`, `atributos` (ex: "grelhado", "assado"), etc.

Com dados estruturados, a ferramenta do agente melhoraria:
-   A função `buscar_cardapio` executaria uma **query** em um banco de dados (ex: `SELECT * FROM produtos WHERE ...`).
-   No prompt do agente ainda seria fornecido as categorias e tags disponíveis, mas a chamada da ferramenta seria muito mais rápida e escalável.

### Abordagem 4: Busca Semântica e RAG (Para Catálogos Não Estruturados)

No cenário em que a Trela não tivesse controle sobre a estrutura dos dados, o maior problema seria fazer o match de semântica do prompt do usuário com os produtos disponíveis.

A solução adequada seria a implementação de umm classificador mais robusto de NLP como BERT (vetoriza os dados) e talvez até algo parecido com um RAG.

A própria Responses API têm uma ferramenta nativa para esta finalidade, a **[File Search](https://platform.openai.com/docs/guides/tools-file-search)**, que gerencia um `Vector Store` e otimiza a busca. Eu só não usei essa solução para o case pois eu precisava do acesso a conta da chave da OpenAI para algumas configurações.