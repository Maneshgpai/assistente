import openai
import streamlit as st
from dotenv import load_dotenv
from loguru import logger
from streamlit_option_menu import option_menu
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import PyPDF2
import io
import sys
import pathlib
import pandas as pd
import json
import traceback
import tiktoken
# import datetime
# import pytz
import os
# import zipfile

# hashed_passwords = stauth.Hasher(['your_pwd_here']).generate()
st.set_page_config(page_title='Assistente', page_icon = "🇧🇷", layout = 'wide', initial_sidebar_state = 'collapsed')
with open('config_assistente.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

def hideStreamlitHeader():
    hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
            </style>
            """
    st.markdown(hide_st_style, unsafe_allow_html=True)
hideStreamlitHeader()

col1, col2, col3 = st.columns(3)
with col1:
  st.write('')
with col2:
  name, authentication_status, username = authenticator.login('Login', 'main')
with col3:
  st.write('')

####################################### SKIP LOGIN #########################################
# st.session_state["authentication_status"]=True
####################################### SKIP LOGIN #########################################

if st.session_state["authentication_status"]:
################################################################################

  ### Define session vars ###
  if "vLang" not in st.session_state:
    st.session_state["vLang"]=False
  if "file_uploader_key" not in st.session_state:
    st.session_state["file_uploader_key"] = 0
  if "vFileData" not in st.session_state:
    st.session_state["vFileData"]=""
  if "vSmry" not in st.session_state:
    st.session_state["vSmry"]=""
  if "vArbResp" not in st.session_state:
    st.session_state["vArbResp"]=""
  if "vIsArbSubmit" not in st.session_state:
    st.session_state["vIsArbSubmit"]=False
  if "vPrcedncResp" not in st.session_state:
    st.session_state["vPrcedncResp"] = ""
  if "vflNm" not in st.session_state:
    st.session_state["vflNm"] = ""
  
  col1, col2 = st.columns([0.88, 0.12])
  with col1:
    st.write(' ')
  with col2:
    st.session_state["vLang"] = st.toggle("English", value=False)

  ### Define global vars ###
  if st.session_state["vLang"]:
    vPgHome = 'Home'
    vPgSetting = 'Setting'
    vHomeTitle = '**Welcome to A.I based Legal assistant**'
    vHomeHeader = 'To summarize case files, identify the right court, clarify doubts on legal matters, search for old case records\
    and much more.\
    \n\
    More features coming soon. Stay tuned!'
    vSettingPgHeader='Work in progress...'
    vFileUpldrLabel='Upload case file'
    vSubmitHomeFileUpldLabel="Summarize"
    vCheckButtonLabel="Submit"
    css='''
      <style>
      [data-testid="stFileUploadDropzone"] div div::before {content:"Drag and drop file here"}
      [data-testid="stFileUploadDropzone"] div div span{display:none;}
      [data-testid="stFileUploadDropzone"] div div::after {color:grey; font-size: .8em; content:"Limit 20MB per file • PDF"}
      [data-testid="stFileUploadDropzone"] div div small{display:none;}
      </style>
      '''
    st.markdown(css, unsafe_allow_html=True)
    vResponseTitle='Summarising '
    vWarningNoFileUpld = 'Warning: Please upload case file to proceed'
    vSmryDwnldButtonMsg = 'Download case summary :arrow_down:'
    vArbDwnldButtonMsg = 'Download arbitration summary :arrow_down:'
    vPrecDwnldButtonMsg = 'Download precedence summary:arrow_down:'
    vGenericDwnldButtonMsg = 'Download :arrow_down:'
    vSmryFileNm='summary'
    vArbRespFileNm='arbitration'
    vPrcedncRespFileNm='precedence'
    vIsArbitrationQue = 'Step 2. Would you like to check if this case qualifies for private arbitration?'
    vOptionNo='No'
    vOptionYes='Yes'
    vIsPrecedenceQue='Step 3. Would you like to check for precedence?'
    vCaseSummaryQue='Step 1. Please upload the case file to begin'
    vDisclaimerArb='Views expressed by the system are generated by an artificial intelligence. It is important to consult with a qualified attorney to further evaluate the \
      specific circumstances of the case and ensure compliance with the latest legal structure in Brazil.'
    vDisclaimerPrec='As an A.I, I have limited access to prior legal files. We are working in the background to bring this feature soon.'
    vWelcomeMsg='Welcome'
    vLogoutButtonTitle='Logout'
  else:
    vPgHome = 'lar'
    vPgSetting = 'contexto'
    vHomeTitle = '**Bem-vindo ao seu próprio assistente jurídico de A.I**'
    vHomeHeader = 'Por toda a sua assistência jurídica, como resumir arquivos de casos, identificar o judiciário correto a ser instaurado e muito mais. \
      \n\
      Muitos mais recursos estão chegando. Fique atento!'
    vSettingPgHeader='trabalho em progresso...'
    vFileUpldrLabel='Carregar arquivo do caso'
    vSubmitHomeFileUpldLabel="Resumir"
    vCheckButtonLabel="Enviar"
    css='''
      <style>
      [data-testid="stFileUploadDropzone"] div div::before {content:"Arraste e solte o arquivo aqui"}
      [data-testid="stFileUploadDropzone"] div div span{display:none;}
      [data-testid="stFileUploadDropzone"] div div::after {color:grey; font-size: .8em; content:"Limite de 20MB por arquivo • PDF"}
      [data-testid="stFileUploadDropzone"] div div small{display:none;}
      </style>
      '''
    st.markdown(css, unsafe_allow_html=True)
    vResponseTitle='Resumindo '
    vWarningNoFileUpld = 'Aviso: faça upload do arquivo do caso para prosseguir'
    vSmryDwnldButtonMsg = 'Baixar resumo do caso :arrow_down:'
    vArbDwnldButtonMsg = 'Baixe o resumo da arbitragem :arrow_down:'
    vPrecDwnldButtonMsg = 'Baixar resumo de precedência :arrow_down:'
    vGenericDwnldButtonMsg = 'Baixar :arrow_down:'
    vSmryFileNm='resumido'
    vArbRespFileNm='arbitragem'
    vPrcedncRespFileNm='precedência'
    vIsArbitrationQue = 'Etapa 2. Gostaria de verificar se este caso se qualifica para arbitragem privada?'
    vOptionNo='Não'
    vOptionYes='Sim'
    vIsPrecedenceQue='Etapa 3. Gostaria de verificar a precedência?'
    vDisclaimerArb='As opiniões expressas pelo sistema são geradas por uma inteligência artificial. É importante consultar um advogado qualificado para avaliar melhor o \
      circunstâncias específicas do caso e garantir o cumprimento da mais recente estrutura jurídica do Brasil.'
    vDisclaimerPrec='Como A.I, tenho acesso limitado a arquivos jurídicos antigos. Mas estamos trabalhando em segundo plano para trazer esse recurso em breve.'
    vCaseSummaryQue='Etapa 1. Faça upload do arquivo do caso para começar'
    vWelcomeMsg='Bem vindo'
    vLogoutButtonTitle='Sair'

  ### Welcome and Logout buttons ###
  col1, col2 = st.columns([0.9, 0.1])
  with col1:
    st.caption(f'{vWelcomeMsg} **{st.session_state["name"]}**')
  with col2:
    authenticator.logout(vLogoutButtonTitle, 'main', key='unique_key')


  load_dotenv()
  openai.api_key = os.getenv("OPENAI_API_KEY")
  input_files = []
  vUpldMultipleFiles = False
  vResponse = ""
  flName = ""
  vPg = vPgHome
  # llm_model = "gpt-3.5-turbo" #For Dev
  llm_model = "gpt-4" #For Prod

  ### Initiate logging ###
  logger_format = (
      "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
      "<level>{level: <8}</level> | "
      "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
      +username+" | "
      "{extra[ip]} {extra[user]} - <level>{message}</level>"
  )
  logger.configure(extra={"ip": "", "user": ""})  # Default values
  logger.remove()
  logger.add(username+"_{time:YYYY-MM-DD!UTC}.log", format=logger_format, rotation="10 MB", compression="zip")
  logger.info("*********** Started Assistente ***********")

  ### Start funcs definitions ###

  encoding = tiktoken.encoding_for_model(llm_model)
  def num_tokens_from_response(response_text):
    num_tokens = len(encoding.encode(response_text))
    return num_tokens

  def num_tokens_from_messages(messages):
    tokens_per_message = 3
    tokens_per_name = 1
    num_tokens = 0
    for message in messages:
      num_tokens += tokens_per_message
      for key, value in message.items():
        num_tokens += len(encoding.encode(value))
        if key == "name":
          num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens

  def getOpenaiApiCost(llm_name,completion_tokens,prompt_tokens):
    if llm_name == "gpt-3.5-turbo":
      ###	4K context: Input/Prompt tokens @ $0.0015/1K tokens, Output/Response tokens @ $0.002/1K tokens
      ip_cost = (prompt_tokens/1000) * 0.0015
      op_cost = (completion_tokens/1000) * 0.002

    elif llm_name == "gpt-3.5-turbo-16k":
      ###	16K context: Input/Prompt tokens @ $0.003/1K tokens, Output/Response tokens @ $0.004/1K tokens
      ip_cost = (prompt_tokens/1000) * 0.003
      op_cost = (completion_tokens/1000) * 0.004

    elif llm_name == "gpt-4":
      ###	8K context: Input/Prompt tokens @ $0.03/1K tokens, Output/Response tokens @ $0.06/1K tokens
      ip_cost = (prompt_tokens/1000) * 0.03
      op_cost = (completion_tokens/1000) * 0.06

    tot_cost = round((op_cost + ip_cost),4)
    return (tot_cost)

  def getFileData(rawFileData):
    file_extension = pathlib.Path(rawFileData.name).suffix
    logger.info("file_extension:{var}",var=file_extension)
    if file_extension.upper()=='.TXT':
      file_data = rawFileData.getvalue().decode('utf-8')
    elif file_extension.upper()=='.PDF':
      file_pages = []
      p = io.BytesIO(rawFileData.getvalue());
      pdf = PyPDF2.PdfReader(p)
      for page in pdf.pages:
        text = page.extract_text()
        file_pages.append(text)
        file_data = ''
        for k in range(len(file_pages)):
          file_data = file_data + file_pages[k]
    logger.info("Data from file:{var}",var=file_data)
    return file_data

  def getAiMessages(prompt):
     message = [{"role": "system", "content": "Assistant is an highly experienced lawyer from Brazil,\
     who knows both portugese and english language and is an expert in all matters related to legal, judicial,\
     and laws"},{"role": "user", "content": prompt}]
     return message

  def getAiResponse(message, isStreaming, prompt, llm_model, temperature):
    result = ""
    collected_messages = []
    report1 = []
    res_box1 = st.empty()
    response = openai.ChatCompletion.create(model=llm_model, messages=message, temperature=temperature, stream=isStreaming,)
    for chunk in response:
      chunk_message = chunk['choices'][0]['delta']
      collected_messages.append(chunk_message)
      if "content" in chunk_message:
        report1.append(chunk_message['content'])
        result = "".join(report1)
        res_box1.success(f'*{result}*')
    vResponse = [''.join([m.get('content', '') for m in collected_messages])]
    return vResponse

  def getSmryPrompt(data):
    if (st.session_state["vLang"]):
      vLang = 'English'
    else:
      vLang = 'Portueguese'
    prompt = f"""Your task is to summarize in atleast 300 words, the legal document provided between three backticks in {vLang} language.
    It is VERY IMPORTANT that you include only the summarised text and nothing else, not a title, post script or any other text.
    You will summarise the legal document in the format and language of a very efficient and experienced advocate.

    It is VERY IMPORTANT that you STRICTLY provide response in {vLang} language.

    After fetching the response, you will review the response to check if you have followed the critera provided between\
     triple commas as delimiters
    ,,,You will review the summary for any important legal points which is missed.
    You should review as per the latest legal structure of Brazil.
    You will include all personal information or PII data related to any person, all dates, names of places, companies etc.
    Include only the summarized response. Do not include any title or post script or anyother text which is not related \
    to the legal document provided between three backticks\
    The response should be in {vLang} language.
    ,,,
    ```{data}```
    """

    # prompt = f"""Your task is to summarize in less than 10 words, the legal document provided between three backticks in {vLang} language.
    # It is VERY IMPORTANT that you include only the summarised text and nothing else, not a title, post script or any other text.
    # You will summarise the legal document in the format and language of a very efficient and experienced advocate.

    # It is VERY IMPORTANT that you STRICTLY provide response in {vLang} language.

    # After fetching the response, you will review the response to check if you have followed the critera provided between\
    #  triple commas as delimiters
    # ,,,You will review the summary for any important legal points which is missed.
    # You should review as per the latest legal structure of Brazil.
    # You will include all personal information or PII data related to any person, all dates, names of places, companies etc.
    # Include only the summarized response. Do not include any title or post script or anyother text which is not related \
    # to the legal document provided between three backticks\
    # The response should be in {vLang} language.
    # ,,,
    # ```{data}```
    # """
    logger.info(prompt)
    return prompt

  def getPromptIsArbitration(data):
    if (st.session_state["vLang"]):
      vLang = 'English'
    else:
      vLang = 'Portuguese'

    prompt = f"""Your task is to check if the case summary provided between three backticks, \
    qualify for private arbitrage in brazil.\
    You will arrive at the decision by considering the Brazil Arbitration Act (Law No. 9.307/1996).
    It is VERY IMPORTANT that you consider the guidelines provided between three tilde symbols.
    ~~~ 
    You will assume that both parties have consented for entering into an written arbitration agreement.
    Carefully analyze the case summary provided the between three backticks to see if this case qualifies to be tried under \
    private arbitration in Brazil under Brazil Arbitration Act (Law No. 9.307/1996)?
    You will use the tone and language of an experienced advocate from Brazil.
    You will not paraphrase or include the case summary in your response.
    The decision should be based only on Brazil Arbitration Act (Law No. 9.307/1996).~~~

    It is VERY IMPORTANT that you STRICTLY provide response in {vLang} language.

    After fetching the response, you will STRICTLY ensure the response follows the guidelines mentioned between three plus signs.\
    +++Your response should only the clarification whether the case qualifies for private arbitration in Brazil. \
    It should also have the why or the reason for considering this under private arbitration.
    You should remove the intial paraphrasing of summary from the response.
    The language of response should be in {vLang}. 
    +++
    
    ```{data}```
    """

    # prompt = f"""Your task is to check if the case summary provided between three backticks, \
    # qualify for private arbitrage in brazil.\
    # You will arrive at the decision by considering the Brazil Arbitration Act (Law No. 9.307/1996).
    # It is VERY IMPORTANT that you consider the guidelines provided between three tilde symbols.
    # ~~~ 
    # You will assume that both parties have consented for entering into an written arbitration agreement.
    # Carefully analyze the case summary provided the between three backticks to see if this case qualifies to be tried under \
    # private arbitration in Brazil under Brazil Arbitration Act (Law No. 9.307/1996)?
    # You will use the tone and language of an experienced advocate from Brazil.
    # You will not paraphrase or include the case summary in your response.
    # The decision should be based only on Brazil Arbitration Act (Law No. 9.307/1996).~~~

    # It is VERY IMPORTANT that you STRICTLY provide response in {vLang} language in LESS THAN 10 WORDS.

    # After fetching the response, you will STRICTLY ensure the response follows the guidelines mentioned between three plus signs.\
    # +++Your response should only the clarification whether the case qualifies for private arbitration in Brazil. \
    # It should also have the why or the reason for considering this under private arbitration.
    # You should remove the intial paraphrasing of summary from the response.
    # The language of response should be in {vLang}. 
    # +++
    
    # ```{data}```
    # """
      
    logger.info(prompt)
    return prompt

  def getPromptIsPrecedence(data, vDisclaimerPrec):
    if (st.session_state["vLang"]):
      vLang = 'English'
    else:
      vLang = 'Portuguese'

    prompt = f"""Your task is to check if the case summary provided between three backticks, \
    has any precedence in in brazil. You will arrive at the decision by following the instructions given between three Tilde symbols.
    ~~~ Carefully analyze the case summary provided the between three backticks.
    Compare it against the cases from Brazil legal system, to only what you have access to.
    If you do not have any access, do not generate hallucinations or imaginary cases.
    Check the precedence of the similar case in this 10 years of Brazil's legal system.~~~

    It is VERY IMPORTANT that you STRICTLY provide response in {vLang} language.

    After fetching the response, you will STRICTLY follow the guidelines given between three Hash symbols.\
    ### You will rewrite the response in the tone, format and language of a very efficient and highly experienced advocate from Brazil.\
    You will check TWICE whether the precedence cited are imaginary or hallucinations. If they are either, you will reject them.
    You will check TWICE whether the Citation URLs are working or not. If they are not working, you will not include any imaginary or placeholder URLs.
    You will not include any summary of the case provided between three backticks. You will only include details of the precedence
    
    You will give your response in only STRICTLY IN JSON format and in {vLang} language. You will not provide any other text beyond this JSON data in {vLang} language.
    [Case_file=input details of precedence cases,Verdict_Date=Input date of precedence cases here, Judgement=Input the verdict give and against whom in the preceednce case, Citation=Input the working URL to the precedence case]
    ,[Case_file=input details of precedence cases,Verdict_Date=Input date of precedence cases here, Judgement=Input the verdict give and against whom in the preceednce case, Citation=Input the working URL to the precedence case]
    If you do not have any precedence case, you will respond with empty JSON.

    Before generating the response you will again check whether the response follows the guidelines given between three Hash symbols.

    You will give your response in only STRICTLY IN JSON format. You will not provide any other text beyond this JSON data.
    If you do not have any precedence case, you will respond with JSON in below format.
    [{vDisclaimerPrec}]

    ```{data}```
    """

    logger.info(prompt)
    return prompt

  def renderHomePgHeader():
    st.subheader(vHomeTitle)
    st.info(vHomeHeader)

  def renderSettingPg():
    st.subheader(vSettingPgHeader)

  # @logger.catch
  # @st.cache_data(max_entries=3,ttl=3600,show_spinner=False)
  # def summarizeFiles(data):
  #   prompt = getSmryPrompt(data)
  #   vResponse = getAiResponse(True,prompt,llm_model,0.3)
  #   return vResponse[0]

  def renderResponse(df):
    st.divider()
    st.dataframe(df, use_container_width=True)
    st.divider()

  def renderMenubar():
    col1, col2 = st.columns([0.5, 0.5])
    with col1:
      vPg = option_menu(None, [vPgHome, vPgSetting],
      icons=['house', 'gear'],
      menu_icon="cast", default_index=0, orientation="horizontal")
    with col2:
      st.write(' ')
    return vPg

  def dwnldSmryResp(data):
    return data

  def dwnldArbResp(data):
    return data

  def dwnldPrcedncResp(data):
    if str(data[0]) == '{}':
      return vDisclaimerPrec
    else:
      return data

################################################################################

  # vPg = renderMenubar()
  if vPg == vPgHome:
    renderHomePgHeader()
    col1, col2, col3 = st.columns([0.15,0.7,0.15])
    with col1:
      st.write(" ")
    with col2:
      tab1, tab2 = st.tabs([" "," "])
      with tab1:
        with st.form("smry", clear_on_submit=True):
          col4, col5 = st.columns([0.85,0.15])
          with col4:
            st.subheader(vCaseSummaryQue)
          with col5:
            vSubmitHomeFileUpld = st.form_submit_button(vSubmitHomeFileUpldLabel, type="primary")
          input_files = st.file_uploader("", type=['pdf'], accept_multiple_files=vUpldMultipleFiles,key=st.session_state["file_uploader_key"],label_visibility="visible")
          if vSubmitHomeFileUpld and not(input_files):
            st.warning(vWarningNoFileUpld)
            st.session_state["vSmry"] = ""
          if vSubmitHomeFileUpld and not(not(input_files)):
            fl_ext = pathlib.Path(input_files.name).suffix
            st.session_state["vflNm"] = input_files.name.replace(fl_ext,'')
            
            with st.spinner('Processing...'):
              file_data = getFileData(input_files).strip()
              st.session_state["vFileData"]=file_data
              prompt = getSmryPrompt(file_data)
              message = getAiMessages(prompt)
              prompt_tokens = num_tokens_from_messages(message)
            
            tokenSzExceed = False
            if prompt_tokens < 4000:
              smry_llm="gpt-3.5-turbo"
            elif prompt_tokens > 4000 and prompt_tokens < 8000:
              smry_llm="gpt-4"
            elif prompt_tokens > 8000 and prompt_tokens < 16000:
              smry_llm="gpt-3.5-turbo-16k"
            else:
              tokenSzExceed = True

            if not(tokenSzExceed):
              st.caption(f'***{st.session_state["vflNm"]} : Case Summary***')
              vResponse = getAiResponse(message, True, prompt, smry_llm, 0)
              st.session_state["vSmry"] = vResponse[0]
              completion_tokens = num_tokens_from_response(st.session_state["vSmry"])
            else:
              st.error("prompt_tokens:"+str(prompt_tokens))
              st.error('Currently system can handle only small case files.\
                \n\
                We are working in the background to increase this limit!')

        col1,col2 = st.columns([0.7,0.3])
        with col1:
          st.write('')
        with col2:
          if st.session_state["vSmry"] != '':
            st.write()
            st.download_button(vSmryDwnldButtonMsg, (st.session_state["vSmry"]), file_name=st.session_state["vflNm"]+'_'+vSmryFileNm+'.txt', type="secondary", key='SmryDwnld', use_container_width=True)

        if st.session_state["vSmry"] != '':
          st.write("--------------------------------------------------------------")
          with st.form("arbitr", clear_on_submit=True):
            col1,col2 = st.columns([0.85,0.15])
            with col1:
              st.write(vIsArbitrationQue)
            with col2:
              vIsArbitrationSubmit = st.form_submit_button(vCheckButtonLabel, type="primary")
            if vIsArbitrationSubmit:
              st.session_state["vIsArbSubmit"] = True
              with st.expander('', expanded=True):
                prompt = getPromptIsArbitration(st.session_state["vSmry"])
                message = getAiMessages(prompt)
                st.caption(f'***{st.session_state["vflNm"]} : Arbitration check***')
                vResp = getAiResponse(message,True,prompt,llm_model,0)
                st.session_state["vArbResp"] = vResp[0]

        if st.session_state["vArbResp"]:
          col1,col2 = st.columns([0.65,0.35])
          with col1:
            st.write('')
          with col2:
            st.download_button(vArbDwnldButtonMsg, dwnldArbResp(st.session_state["vArbResp"]), file_name=st.session_state["vflNm"]+'_'+vArbRespFileNm+vSmryFileNm+'.txt', type="secondary", key='IsArbitrationDwnld',use_container_width=True)
          st.caption(f':Gray[{vDisclaimerArb}]')
          st.session_state["vIsArbSubmit"] = False

        if st.session_state["vFileData"] != '':
          st.write("--------------------------------------------------------------")
          with st.form("prece", clear_on_submit=True):
            col1,col2 = st.columns([0.85,0.15])
            with col1:
              st.write(vIsPrecedenceQue)
            with col2:
              vIsPrecedenceSubmit = st.form_submit_button(vCheckButtonLabel, type="primary")
            if vIsPrecedenceSubmit and st.session_state["vFileData"] != '':
              with st.expander('', expanded=True):
                prompt = getPromptIsPrecedence(st.session_state["vSmry"], vDisclaimerPrec)
                st.caption(f'***{st.session_state["vflNm"]} : Precedences***')
                message = getAiMessages(prompt)
                st.session_state["vPrcedncResp"] = vDisclaimerPrec
                st.success(vDisclaimerPrec)

        if st.session_state["vPrcedncResp"] != '':
          col1,col2 = st.columns([0.64,0.36])
          with col1:
            st.write('')
          with col2:
            st.download_button(vPrecDwnldButtonMsg, dwnldPrcedncResp(st.session_state["vPrcedncResp"]), file_name=st.session_state["vflNm"]+'_'+vPrcedncRespFileNm+vSmryFileNm+'.txt', type="secondary", key='IsPrcedncDwnld',use_container_width=True)
          # st.caption(f':Gray[{vDisclaimerPrec}]')
      with tab2:
        st.write('')

    with col3:
      st.write(" ")

elif st.session_state["authentication_status"] is False:
  col1, col2, col3 = st.columns(3)
  with col1:
    st.write('')
  with col2:
    st.error('Username/password is incorrect')
  with col3:
    st.write('')
elif st.session_state["authentication_status"] is None:
  col1, col2, col3 = st.columns(3)
  with col1:
    st.write('')
  with col2:
    st.warning('Please enter your username and password')
  with col3:
    st.write('')
else:
  col1, col2, col3 = st.columns(3)
  with col1:
    st.write('')
  with col2:
    st.error('Contact admin @ maneshgpai@gmail.com')
  with col3:
    st.write('')
