import re
from unicodedata import normalize
import os
import nltk
nltk.data.path.append(os.getcwd() + os.sep  + "nltk_data")
from nltk import corpus
from nltk import regexp_tokenize
from file_handle import file_io
import json
import pandas as pd

from EdgeGPT.EdgeGPT import Chatbot, ConversationStyle
from langchain.output_parsers import ResponseSchema
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import StructuredOutputParser
import asyncio


def convert_to_json(response):

  # Define the regular expression pattern to match the JSON data
  pattern = r'```json\s*(\{.*?\})\s*```'
  json_data = dict()
  # Use the re.findall() function to find all occurrences of the pattern in the data_string
  matches = re.findall(pattern, response, re.DOTALL)
  if matches:
    json_data = matches[0]
    json_data = json.loads(json_data)
  return json_data

def find_dodf_year(lstJornalDia):
    # Extract the year using regular expression
    dodf_year_pattern = r'\d{2}-\d{2}-(\d{4})'
    dodf_year_match = re.search(dodf_year_pattern, lstJornalDia[0])
    if dodf_year_match:
        return dodf_year_match.group(1)


def extract_fathers(child_id, hierarchy):
    fathers = []
    for father_id, child_ids in hierarchy.items():
        if child_id in child_ids:
            fathers.append(father_id)
    return fathers


def extract_info(child_id, lstHierarquia):
    for each in lstHierarquia:
        if child_id == each['co_demandante']:
            #if each['ds_sigla']:
            return [each['ds_nome'], each['ds_sigla']]
            # else:
            #     return each['ds_nome']
    return ""

def extract_orgao(list, lstHierarquia):
    for each_father in list:
        key = next(iter(each_father.keys()))
        sigla = each_father[key][1]
        #print(sigla)
        for each in lstHierarquia:
            #print(each)
            if str(key) in each['co_demandante']:
                if "3" in each['co_demandante_tipo'] and sigla is not None and sigla != "SUAG":
                    return str(each['ds_nome']) + " - " + str(each['ds_sigla'])
                # else:
                #     return each['ds_nome']
    return ""


def find_list_father(child_id, hierarchy, lstHierarquia):
    list = []
    last_father = child_id
    name = extract_info(child_id, lstHierarquia)
    if name:
        list_dict = dict()
        list_dict[child_id] = name
        list.append(list_dict)
    fathers = extract_fathers(child_id, hierarchy)
    while len(fathers) > 0:
        for father_id in fathers:
            if father_id == '0':
                return list
            name = extract_info(father_id, lstHierarquia)
            if name:
                list_dict = dict()
                list_dict[father_id] = name
                list.append(list_dict)
            fathers = extract_fathers(father_id, hierarchy)
            last_father = father_id
    return list

# def get_data(json_data):
#       print(json_data)
#       pattern = r'"objeto":\s*"([^"]*)".*?"objeto_compacto":\s*"([^"]*)".*?"tipo":\s*"([^"]*)".*?"classificacao":\s*"([^"]*)".*?"data_abertura":\s*["]?([^"]*)["]?.*?"valor":\s*["]?([^"]*)["]?.*?"orgao":\s*["]?([^"]*)["]?.*?"modalidade":\s*"([^"]*)".*?"id":\s*"([^"]*)".*?"processo":\s*["]?([^"]*)["]?.*?'
#       data = {}
#       result = None
  
#       if isinstance(json_data, str):
#           result = re.search(pattern, json_data, re.DOTALL)
#           if result:
#               objeto = result.group(1)
#               objeto_compacto = result.group(2)
#               tipo = result.group(3)
#               classificacao = result.group(4)
#               data_abertura = result.group(5)
#               valor = result.group(6)
#               orgao = result.group(7)
#               modalidade = result.group(8)
#               id = result.group(9)
#               processo = result.group(10)
#               processo_formatado = re.findall(r'\b(\d[\d./-]*\d)\b', processo, re.DOTALL)
#               processo = ', '.join(processo_formatado)
  
#               data = {
#                   'objeto': objeto,
#                   'objeto_compacto': objeto_compacto,
#                   'tipo': tipo,
#                   'classificacao': classificacao,
#                   'data_abertura': data_abertura,
#                   'valor': valor,
#                   'orgao': orgao,
#                   'modalidade': modalidade,
#                   'id': id,
#                   'processo': processo,
#               }
#               # data = {
#               #     'objeto': [objeto],
#               #     'objeto_compacto': [objeto_compacto],
#               #     'tipo': [tipo],
#               #     'classificacao': [classificacao],
#               #     'data_abertura': [data_abertura],
#               #     'valor': [valor],
#               #     'orgao': [orgao],
#               #     'modalidade': [modalidade],
#               #     'id': [id],
#               #     'processo': [processo],
#               # }
  
#       return data


async def query(prompt):

        try:
            bot = await Chatbot.create() # Passing cookies is "optional", as explained above
            response = await bot.ask(prompt=prompt, conversation_style=ConversationStyle.precise) # 'creative', 'balanced' or 'precise'
            if response:
                #json_data = response["item"]["messages"][1]["adaptiveCards"][0]["body"][0]["text"]
                response_string = response["item"]["messages"][-1]["text"]
                if response_string:
                    data = convert_to_json(response_string)
                    #data = get_data(json_data)
                    #print(data)
                    print(data)                  
            await bot.close()
            return data
            #return json_data
            #conversation_style = ConversationStyle.balanced
        except Exception as e:
            print("An exception occurred:", str(e))



objeto_schema = ResponseSchema(name="objeto",
                               description="Extraia o objeto da licitação, \
                                          incluindo as características mais importantes do negócio a ser realizado.")



objeto_compact_schema = ResponseSchema(name="objeto_compacto",
                                       description="Considerando o objeto da licitação, extraia a palavra-chave que melhor define a natureza do material/produto ou serviço que está sendo contratado.")

tipo_schema = ResponseSchema(name="tipo",
                             description="Com base nas informações do 'objeto' e do 'objeto_compacto', \
                                                  esta licitação trata da aquisição/compra de um material/equipamento, \
                                                  da prestação/contratação de um serviço? \
                                                  Considere que a prestação do serviço com utilização de mão de obra e fornecimento de material \
                                                  deve ser considerado um serviço. Também é considerado serviço a aquisição/compra de um material/equipamento \
                                                  com a instalação realizada pelo prestador. \
                                                  Respostas possíveis: ['1 - Material', '2 - Serviço']")

classificacao_schema = ResponseSchema(name="classificacao",
                                      description="Considerando o 'tipo' acima, em caso de aquisição/compra de material ('1 - Material'), \
                                                   classificar a aquisição em uma das seguintes categorias de aquisição/compra: \
                                                   ['4 - AQUISIÇÃO DE MEDICAMENTOS, INSUMOS, EQUIPAMENTOS OU PRODUTOS HOSPITALARES APLICADOS À ÁREA DE SAÚDE', '19 - AQUISIÇÃO DE VEÍCULOS' \
                                                   '24 - AQUISIÇÃO DE PERIFÉRICOS/HARDWARE/SOFTWARE APLICADO À CIÊNCIA DE DADOS/COMPUTAÇÃO']. Caso nenhuma dessas categorias seja similar, \
                                                   classificar o objeto como '3 - AQUISIÇÃO (OUTROS)'. Em caso de prestação ou\
                                                   contratação de um 'serviço', classificar o serviço a ser contratado \
                                                   em uma das seguintes categorias de serviços: ['2, 6, 12, 22, 23, 25 - OBRAS OU SERVIÇOS DE ENGENHARIA', '9, 10, 11 - LOCAÇÃO', \
                                                   '13 - SERVIÇOS DE TECNOLOGIA DA INFORMAÇÃO'.  Caso nenhuma dessas categorias seja similar, \
                                                   classificar o objeto na seguinte categoria: '7, 8, 14, 15, 18, 20, 21 - SERVIÇOS (OUTROS)'. \
                                                   Atenção para contratação de consultoria. Quando a consultoria envolver obras ou serviços de engenharia deve ser classificada \
                                                   como '2, 6, 12, 22, 23, 25 - OBRAS OU SERVIÇOS DE ENGENHARIA'. Quando a consultoria tratar de assuntos relacionados a \
                                                   Tecnologia da Informação classificar como '13 - SERVIÇOS DE TECNOLOGIA DA INFORMAÇÃO'. Nos demais casos, \
                                                   classificar a consultoria como '7, 8, 14, 15, 18, 20, 21 - SERVIÇOS (OUTROS)'.")

data_abertura_schema = ResponseSchema(name="data_abertura",
                                      description="Qual a data de abertura da licitação? \
                                                  Responder no formato dd/mm/aaaa. \
                                                  Se não encontrar a informação, \
                                                  retornar -1 como saída.")
valor_schema = ResponseSchema(name="valor",
                              description="Extrair o valor total da licitação/contratação em R$ (moeda BRL).")

orgao_schema = ResponseSchema(name="orgao",
                              description="Qual o órgão/empresa pública responsável pela realização da licitação? Se não encontrar o nome \
                                                 do órgão/empresa pública de forma explícitiva, extrair a Unidade Administrativa de Serviços Gerais - UASG. \
                                                 Se não encontrar o nome nem a UASG, retornar -1 como resposta.")


modalidade_schema = ResponseSchema(name="modalidade",
                                   description="""Considerando o 'Texto da Licitação', atue como um modelo de classificação e classifique a licitação na categoria que melhor se relaciona \
                                                    (mais similar) com a modalidade de licitação escolhida pelo ente público, considerando as possibilidades da lista a seguir:
                                                    ['4 - PREGÃO ELETRÔNICO POR ATA OU SISTEMA DE REGISTRO DE PREÇOS (SRP)' (aplicável quando o objetivo for a formação de registro de preço),
                                                    '5 - PREGÃO PRESENCIAL POR ATA OU SISTEMA DE REGISTRO DE PREÇOS (SRP)' (aplicável quando o objetivo for a formação de registro de preço),
                                                    '6 - REGIME DIFERENCIADO DE CONTRATAÇÕES (RDC)',
                                                    '16 - LICITAÇÃO REGIDA PELA LEI Nº 13.303/2016 (RILC)',
                                                    '7 - CONCORRÊNCIA',
                                                    '11 - TOMADA DE PREÇOS',
                                                    '12 - LICITAÇÃO PÚBLICA NACIONAL (LPN)',
                                                    '13 - PROCEDIMENTO LICITATÓRIO (PL)',
                                                    '14 - LICITAÇÃO PÚBLICA INTERNACIONAL (LPI)',
                                                    '15 - CONVITE',                                                        
                                                    '17 - PROCEDIMENTO LICITATÓRIO ELETRÔNICO (PLe)',
                                                    '18 - PROCEDIMENTO LICITATÓRIO PRESENCIAL',
                                                    '19 - CHAMAMENTO PÚBLICO',
                                                    '20 - COTAÇÃO ELETRÔNICA',
                                                    '2 - PREGÃO PRESENCIAL',
                                                    '3 - PREGÃO ELETRÔNICO']. 
                                                    Caso nenhuma \
                                                    das modalidades mencionadas até então seja aplicável, classificar como '99 - OUTRAS MODALIDADES DE LICITAÇÃO'.
                                                    Para realizar esta tarefa, atente para as seguintes orientações:
                                                    1) só classique nas categorias '12 - LICITAÇÃO PÚBLICA NACIONAL (LPN)' e '14 - LICITAÇÃO PÚBLICA INTERNACIONAL (LPI)' as licitações \
                                                    financiadas pelo Banco Interamericano de Desenvolvimento - BID, Banco Mundial - BIRD, ou outro organismo multilateral de fomento;  
                                                    2) qualquer menção a Lei nº 13.303/2016 ou ao Regimento Interno de Licitações e Contratações/Contratos ou sua sigla abreviada RILC \
                                                    no 'Texto da Licitação' torna muito provável que a classificação correta seja '16 - LICITAÇÃO REGIDA PELA LEI Nº 13.303/2016 (RILC),' \
                                                    bem como licitações realizadas por empresas públicas ou sociedades de economia mista do Distrito Federal, em que o nome da modalidade \
                                                    parece não se adequar às categorias definidas acima;
                                                    3) o '6 - REGIME DIFERENCIADO DE CONTRATAÇÕES (RDC)' é aplicável quando constar menção a Lei nº 12.462/11 e quando o objeto envolver \
                                                    a Copa das Confederações da FIFA 2013, a Copa do Mundo FIFA 2014, Jogos Olímpicos e Paraolímpicos de 2016, bem como obras de infraestrutura \
                                                    e de contratação de serviços para os aeroportos das capitais próximas àqueles eventos).""")
id_schema = ResponseSchema(name="id",
                           description="Qual o título/número de identificação da licitação? Retorne como resposta apenas número e ano. Exemplos: ['65/2013', '65/2023'")

processo_schema = ResponseSchema(name="processo",
                                 description="Qual o número do processo relativo a licitação? \
                                             Se não encontrar a informação, \
                                                  retornar -1 como saída")

response_schemas = [objeto_schema,
                    objeto_compact_schema,
                    tipo_schema,
                    classificacao_schema,
                    data_abertura_schema,
                    valor_schema,
                    orgao_schema,
                    modalidade_schema,
                    id_schema,
                    processo_schema]

output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
format_instructions = output_parser.get_format_instructions()

#    Retorne as informações no idioma português, atentando para os sinais de pontuação e corrigindo quebras de continuidade de texto, como espaços extras no meio de uma palavra.


template = """\

Para o texto da licitação/certame a seguir:

Texto da Licitação: '{text}'

Primeiramente, corrija quebras de continuidade na meio da palavra, como excesso de espaços. 
Por exemplo, 'A d e s p e s a c o r r e r á a c o n t a d o P r o j e t o D E R'  deve ser corrigido para 'A despesa correrá a conta do Projeto DER'. 
Outro exemplo: '0 0 111 - 0 0 0 11 3 4 6 / 2 0 1 9 - 4 0' deve ser corrigido para '00111-00011346/2019-40.' 

Em seguida, extrair as seguintes informações relativas ao 'objeto', 'objeto_compacto', 'tipo', 'classificacao', 'data_abertura' , 'valor', 'orgao', 'modalidade', 'id' e 'processo'.    
Formatar a resposta como JSON utilizando as chaves acima e a estrutura detalhada abaixo.

Your goal is to extract structured information from 'Texto da Licitação' that matches the form described below. When extracting information please make sure it matches the type information exactly. Do not add any attributes that do not appear in the schema shown below.
{format_instructions}
"""

prompt_template = ChatPromptTemplate.from_template(template)
prompt = ChatPromptTemplate.from_template(template=template)


class classifier_model():
  
  def __init__(self):
    self.files = object
    self.data_schema = object
    self.model_result = []
    self.model_header = []

  def set_model_parameters(self, files, data_schema):
    self.files = files
    self.data_schema = data_schema
  
  def set_model_result(self, model_result):
    self.model_result = model_result

  def get_model_result(self):
    return self.model_result

  def set_model_header(self, model_header):
    self.model_header = model_header

  def get_model_header(self):
    return self.model_header
  
  def start_classifier_model(self, fileType, single_multiple_class):

    print(self.data_schema)
    response_schemas = []
    name_schemas = []
    df_dict = self.data_schema.to_dict(orient='records')
    print(df_dict)
    
    for each in df_dict:
      name_schemas.append(each['Schema'])
      response_schemas.append(ResponseSchema(name=each['Schema'], description=each['Description']))

    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()

    name_schemas = ', '.join(name_schemas)
    
    #    Retorne as informações no idioma português, atentando para os sinais de pontuação e corrigindo quebras de continuidade de texto, como espaços extras no meio de uma palavra.

        # Em seguida, extrair as seguintes informações relativas ao 'objeto', 'objeto_compacto', 'tipo', 'classificacao', 'data_abertura' , 'valor', 'orgao', 'modalidade', 'id' e 'processo'.    
    
    template = """\
    
    Para o texto da licitação/certame a seguir:
    
    Texto da Licitação: '{text}'
    
    Primeiramente, corrija quebras de continuidade na meio da palavra, como excesso de espaços. 
    Por exemplo, 'A d e s p e s a c o r r e r á a c o n t a d o P r o j e t o D E R'  deve ser corrigido para 'A despesa correrá a conta do Projeto DER'. 
    Outro exemplo: '0 0 111 - 0 0 0 11 3 4 6 / 2 0 1 9 - 4 0' deve ser corrigido para '00111-00011346/2019-40.' 
    
    Em seguida, extrair as chaves de informação relacionadas abaixo no formato JSON.
    
    Your goal is to extract structured information from 'Texto da Licitação' that matches the form described below. When extracting information please make sure it matches the type information exactly. Do not add any attributes that do not appear in the schema shown below.
    {format_instructions}
    """
    
    prompt_template = ChatPromptTemplate.from_template(template)
    prompt = ChatPromptTemplate.from_template(template=template)
        
    
    model_result = []
    df_atos_licitacao = []
    
    for each_file in self.files:
    
      class_data = file_io(each_file)
      #data = class_data.dispatch_filetype()

      data = class_data.switch_file_type.get(fileType, class_data.process_unknown_file_type)()
      
      #class_file_io.switch_single_multiple_class.get(singleMultipleClassif, class_file_io.process_unknown_classif)()      
      model_result_each_file = []

      if fileType == 'plain_text':
      #data = normalize('NFKD', data).encode('ASCII','ignore').decode('ASCII')
        data = re.split(chr(12), data)
  
        for index, page in enumerate(data):
            page_number = str(index + 1)
            string_page = str(page) 
            headers_list = []
            data_list = []           
            question = string_page
            print(question)
            messages = prompt.format_messages(text=question,
                                                    format_instructions=format_instructions)
            question = messages[0].content
            find_classification = asyncio.run(query(question))
                        # file_name_with_extension = os.path.basename(each_file)
                        # filename = os.path.splitext(file_name_with_extension)[0]
                
                        # find_classification = [filename, page_number, header[document_type], best_fit_tfidf_model,tfidf_alert, best_fit_lsi_model, lsi_alert]     
            if bool(find_classification) and isinstance(find_classification, dict):            
              #output_dict = output_parser.parse(find_classification)
              #print(output_dict)
              #print(type(output_dict))
              headers_list = list(find_classification.keys()) 
              data_list = list(find_classification.values())     
              print("Headers List:", headers_list)
              print("Data List:", data_list)
              model_result_each_file.append(data_list)
        model_result.append(model_result_each_file) 
        model_header = headers_list
        self.set_model_result(model_result)
        self.set_model_header(model_header)
    
      elif fileType == 'json':

            regex_licitacao = r'(?:NOTIFICA[CÇ][ÃAOÕ][EO][S]?|VENCEDOR|SUSPENS[AÃ]O|REVOGA[ÇC][AÃ]O|TERMO|RESULTADO|DISPENSA|INEXIGIBILIDADE|JULGAMENTO|AUDI[EÊ]NCIA\s+P[ÚU]BLICA|SUPRIMENTO|HOMOLOGA[CÇ][AÃ]O|ADJUDICA[CÇ][AÃ]O|ADIAMENTO|CONVOCA[CÇ][AÃ]O|AQUISI[CÇ][AÃ]O|LICEN[CÇ]A|RECURSO|ANULAÇÃO|CANCELAMENTO|COOPERAÇÃO|APRESENTAÇÃO|DISCUSSÃO|AQUISIÇÕES|CLASSIFICAÇÃO|CONSULTA\s+PÚBLICA|DESCLASSIFICAÇÃO|LEILÃO|IMPUGNAÇÃO|FRACASSADA|DESERTA|PRORROGAÇÃO|AUTORIZAÇÃO|COMUNICADO|INTIMAÇÃO|IMÓVEIS|COMPRAS|RESCISÃO|CONTRATO|EXTRATO|PUBLICIDADE|SUSPENÇÃO|FORNECEDOR|LICENCIAMENTO|VENDEDORES)'


            try:
                lstHierarquia = data['json']['lstHierarquia']['lstDemandantes']
                hierarchy = data['json']['lstHierarquia']['hierarquia']
                # print(hierarchy)

                if 'Seção III' in data['json']['INFO']:
                    section_3 = data['json']['INFO']['Seção III']
                    for orgao in section_3:
                        for documento in section_3[orgao]:
                            for ato in section_3[orgao][documento]:

                                titulo = section_3[orgao][documento][ato]['titulo']
                                tipo = section_3[orgao][documento][ato]['tipo']


                                #if tipo is not None and tipo != "Ineditorial":
                                if tipo is not None and (tipo == "Aviso" or tipo == "Pregão"):

                                    if titulo is not None and re.search(regex_licitacao, titulo.upper()) is None:
                                        # if re.search(regex_licitacao, titulo) is not None:
                                        coDemandante = section_3[orgao][documento][ato]['coDemandante']
                                        #titulo = html.unescape(titulo)



                                        #texto_html = section_3[orgao][documento][ato]['texto']
                                        texto_html = """<p style="text-align:center;">""" + titulo + """</p>""" + section_3[orgao][documento][ato]['texto']

                                        # texto = section_3[orgao][documento][ato]['texto']
                                        # texto = re.sub(r'<[^>]*>', '',
                                        #                titulo + " " + section_3[orgao][documento][ato]['texto'])
                                        # print(texto)

                                        #texto_html = html.unescape(texto_html)


                                        texto = re.sub(r'<[^>]*>', ' ', str(titulo) + section_3[orgao][documento][ato]['texto'])


                                        # texto = section_3[orgao][documento][ato]['texto']
                                        # texto = re.sub(r'<[^>]*>', '',
                                        #                titulo + " " + section_3[orgao][documento][ato]['texto'])
                                        # print(texto)

                                        #texto = html.unescape(texto)

                                        #texto = section_3[orgao][documento][ato]['texto']
                                        # print(texto)
                                        # print(titulo)
                                        #
                                        ano = find_dodf_year(data['lstJornalDia'])
                                        numero_dodf = data['json']['nu_numero'] + "/" + ano
                                        coMateria = section_3[orgao][documento][ato]["coMateria"]

                                        # atos_licitacao['titulo'].append(titulo)
                                        # atos_licitacao['texto'].append(re.sub(r'<[^>]*>', '', titulo + " " + section_3[orgao][documento][ato]['texto']))
                                        # # res = self.parse_regex(section_3[orgao][documento][ato]['texto'])
                                        #
                                        #
                                        # atos_licitacao['processo'].append('processo')
                                        # atos_licitacao['numero_licitacao'].append('numero_licitacao')
                                        # atos_licitacao['modalidade'].append('modalidade')

                                        list_father = find_list_father(coDemandante, hierarchy, lstHierarquia)
                                        orgao_df = extract_orgao(list_father, lstHierarquia)

                                        atos_licitacao = {
                                            'numero_dodf': numero_dodf,
                                            'coMateria': coMateria,
                                            'tipo': tipo,
                                            'titulo': titulo,
                                            'texto': texto,
                                            'texto_html': texto_html,
                                            'orgao': orgao_df
                                        }
                                        df_atos_licitacao.append(atos_licitacao)
                                        #print(df_atos_licitacao)
                                        # print(re.sub(r'<[^>]*>', '', titulo + " " + section_3[orgao][documento][ato]['texto']))
                #df_atos_licitacao = pd.DataFrame(atos_licitacao)
            except KeyError:
                print(f"Chave 'Seção III' não encontrada no DODF {data['lstJornalDia']}!")        
      filtered_df = pd.DataFrame(df_atos_licitacao)
      print(filtered_df)
      print(filtered_df.head(5).texto.iloc[3])    
      #data = [['16', 4, 0.832574, 'ok', 0.95689666, 'ok'], ['17', 4, 0.7490662, 'ok', 0.9434082, 'ok'], ['18', 3, 0.7548005, 'ok', 0.88454604, 'ok']]
      
      #data_dict = [dict(zip(['col1', 'col2', 'col3', 'col4', 'col5', 'col6'], row)) for row in model_result]
      #import json
      #data_json = json.dumps(data_dict)
      
      #print(data_dict)
      #print("data_json:", data_json)
      
    # model_header = ['Filename','Page Number','Classification', 'Model 1 Prediction', 'Model 1 Alert', 'Model 2 Prediction', 'Model 2 Alert']
      #ee