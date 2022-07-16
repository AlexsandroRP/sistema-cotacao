import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry # Campo de infortmação de data
import requests #módulo que permite puxar informações de apis
from tkinter.filedialog import askopenfilename
import pandas as pd
from datetime import datetime
import numpy as np

requisicao = requests.get('https://economia.awesomeapi.com.br/json/all') #puxa as info do site
dicionario_moedas = requisicao.json() #transforma dici json em python

lista_moedas = list(dicionario_moedas.keys())#retorna as chaves do dicionário

def pegar_cotacao():
    moeda = combobox_selecionarmoeda.get()
    data_cotacao = calendario_moeda.get()
    ano = data_cotacao[-4:] # mes 4 até o final
    mes = data_cotacao[3:5] # a partir do 3 até o 5
    dia = data_cotacao[:2] # até caracter indice 2
    link = f"https://economia.awesomeapi.com.br/{moeda}-BRL/10?start_date={ano}{mes}{dia}&end_date={ano}{mes}{dia}"
    requisicao_moeda = requests.get(link)
    cotacao = requisicao_moeda.json() # lista criada no link
    valor_moeda = cotacao[0]['bid'] # atribui a variavel valor_moeda o indice 0 da chave 'bid'
    label_textocotacao['text'] = f"A cotação da {moeda} no dia {data_cotacao} foi de: R$ {valor_moeda}" # Texto após gerar cotação

def selecionar_arquivo():
    caminho_arquivo = askopenfilename(title="Selecione o arquivo de moeda")
    var_caminhoarquivo.set(caminho_arquivo) # muda o texto da var_caminhoarquivo para caminho_arquivo
    #Essa variavel var_caminho arquivo teve que ser criada para poder ser acessada na próxima função
    if caminho_arquivo:
        label_arquivoselecionado['text'] = f'Arquivo selecionado: {caminho_arquivo}' # Muda o texto para o caminho selecionado

def atualizar_cotacoes():
    try:
        # Le o df de moedas
        df = pd.read_excel(var_caminhoarquivo.get())
        moedas = df.iloc[:, 0] #Todas as linhas e coluna de indice 0
        #Pega a data de inicio e fim das cotações
        data_inicial = calendario_datainicial.get()
        data_final = calendario_datafinal.get()
        ano_inicial = data_inicial[-4:]
        mes_inicial = data_inicial[3:5]
        dia_inicial = data_inicial[:2]

        ano_final = data_final[-4:]
        mes_final = data_final[3:5]
        dia_final = data_final[:2]

        #Pra cada moeda pegar todas as cotações daquela moeda
        for moeda in moedas:
            link = f"https://economia.awesomeapi.com.br/json/daily/{moeda}-BRL/?" \
                   f"start_date={ano_inicial}{mes_inicial}{dia_inicial}&" \
                   f"end_date={ano_final}{mes_final}{dia_final}"

            requisicao_moeda = requests.get(link)
            cotacoes = requisicao_moeda.json()
            for cotacao in cotacoes:
                timestamp = int(cotacao['timestamp']) #timestamp informações vinda das cotações do site
                bid = float(cotacao['bid']) #bid informações vinda das cotações do site
                data = datetime.fromtimestamp(timestamp) #transforma timestamp em formato de data
                data = data.strftime('%d/%m/%Y') #Transforma o texto em data BR
                if data not in df: #olha as colunas e ve se data não existe nas coluna, dai cria as colunas
                    df[data] = np.nan
                # Criar coluna em novo df com todas as cotações daquela moeda
                df.loc[df.iloc[:, 0] == moeda, data] = bid # Linha onde na primeira coluna, tem a moeda. =bid vai ser a moeda
        #cria arquivo com todas as cotações
        df.to_excel("Teste.xlsx")
        label_atualizarcotacoes['text'] = 'Arquivo atualizado com sucesso'

    except: #caso o usuario selecione um arquivo que não seja excel
        label_atualizarcotacoes['text'] = 'Selecione um arquivo excel no formato correto'


janela = tk.Tk()

janela.title("Ferramenta de cotação de moedas")

label_cotacaomoeda = tk.Label(text="Cotação de 1 moeda específica", borderwidth=2, relief="solid") # Tamanho e estilo da borda
label_cotacaomoeda.grid(row=0, column=0, padx=10, pady=10, sticky="nswe", columnspan=3) # x distancia esquerda a direita, pady distancia cima-baixo

label_selecionarmoeda = tk.Label(text="Selecionar moeda", anchor='e')
label_selecionarmoeda.grid(row=1, column=0, padx=10, pady=10, sticky="nswe", columnspan=2)

combobox_selecionarmoeda = ttk.Combobox(values=lista_moedas) # lista de moedas
combobox_selecionarmoeda.grid(row=1, column=2, padx=10, pady=10, sticky="nswe")

label_selecionardia = tk.Label(text="Selecione o dia que deseja pegar a cotação", anchor='e')
label_selecionardia.grid(row=2, column=0, padx=10, pady=10, sticky="nswe", columnspan=2)

calendario_moeda = DateEntry(year=2022, locale='pt_br')
calendario_moeda.grid(row=2, column=2, padx=10, pady=10, sticky='nswe')

label_textocotacao = tk.Label(text="") #texto vazio só aparece após ação
label_textocotacao.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky='nswe')

botao_pegarcotacao = tk.Button(text="Pegar cotação", command=pegar_cotacao)
botao_pegarcotacao.grid(row=3, column=2, padx=10, pady=10, sticky='nsew')


# Cotação de várias moedas

label_cotacaovariasmoedas = tk.Label(text="Cotação de multíplas moedas", borderwidth=2, relief="solid")
label_cotacaovariasmoedas.grid(row=4, column=0, padx=10, pady=10, sticky="nswe", columnspan=3)

var_caminhoarquivo = tk.StringVar()

label_selecionararquivo = tk.Label(text="Selecione um arquivo em excel com as Moedas na coluna A")
label_selecionararquivo.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky='nswe')

botao_selecionararquivo = tk.Button(text="Clique aqui para selecionar", command=selecionar_arquivo)
botao_selecionararquivo.grid(row=5, column=2, padx=10, pady=10, sticky='nsew')

label_arquivoselecionado = tk.Label(text="Nenhum arquivo selecionado", anchor='e') #anchor direção nswe
label_arquivoselecionado.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky='nswe')

label_datainicial = tk.Label(text='Data Inicial', anchor='e')
label_datafinal = tk.Label(text='Data Final', anchor='e')
label_datainicial.grid(row=7, column=0, padx=10, pady=10, sticky='nswe')
label_datafinal.grid(row=8, column=0, padx=10, pady=10, sticky='nswe')

calendario_datainicial = DateEntry(year=2022, locale='pt_br')
calendario_datafinal = DateEntry(year=2022, locale='pt_br')
calendario_datainicial.grid(row=7, column=1, padx=10, pady=10, sticky='nswe')
calendario_datafinal.grid(row=8, column=1, padx=10, pady=10, sticky='nswe')

botao_atualizarcotacoes = tk.Button(text='Atualizar cotações', command=atualizar_cotacoes)
botao_atualizarcotacoes.grid(row=9, column=0, padx=10, pady=10, sticky='nswe')

label_atualizarcotacoes = tk.Label(text="")
label_atualizarcotacoes.grid(row=9, column=1, columnspan=2, padx=10, pady=10, sticky='nswe')

botao_fechar = tk.Button(text='Fechar', command=janela.quit) #não precisa função pra fefchar a janela, já passa o comando direto
botao_fechar.grid(row=10, column=2, padx=10, pady=10, sticky='nswe')

janela.mainloop()
