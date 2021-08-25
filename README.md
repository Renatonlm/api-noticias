Uso:

# Buscar noticia:
Tipo: GET
URL: /search
Params:  query_type (“autor”, “titulo” ou “texto”),  termo(string)
Exemplo:  _{query_type:  ”titulo”,  termo:  ”Angela Merkel”)}_
Resposta: Lista com as noticias encontradas
# Publicar noticia:
Tipo: POST
URL: /publish
Params:  autor(string), titulo(string), texto(string), empresa(string) – se o autor já não estiver cadastrado   
Exemplo:  _{autor:  ”Carlos Alberto”, titulo :”Islândia reabre a fronteira”, texto:  “Islândia reabre a fronteira para turistas brasileiros que tenham tomado a segunda dose de alguma das vacinas aplicadas pelo SUS.”}_
Resposta: Dados da noticia publicada
# Atualizar noticia:
Tipo: POST
URL: /update
Params:  id(obrigatório, string),  titulo(string), texto(string),  autor(string
Exemplo:  _{id: ”02919382bc9174ba”, titulo: ”Islândia reabre a fronteira”}_
Resposta: Dados atualizados
# Deletar noticia:
Tipo: POST
URL: /delete
Params:  id(obrigatório, string)
Exemplo:  _{id: ”02919382bc9174ba”}_
Resposta: id da noticia deletada
