import customtkinter as ctk
import conteudo_rotina as conteudo_rotina 
import conteudo_config as conteudo_config
import conteudo_info as conteudo_info
import conteudo_pomodoro as conteudo_pomodoro
import conteudo_pontuacao as conteudo_pontuacao
from PIL import Image
import datetime
import schedule
from pystray import Icon, MenuItem as item,Menu
import threading
import ntx_database as db

#Lógica que usa lib datetime para pegar os dias e horários e transforma eles em string
hoje = datetime.datetime.now()
ontem = hoje - datetime.timedelta(days=1)
ontem = ontem.strftime("%A")
hora = hoje.strftime("%H:%M")

#Configurações da Janela Principal
janela = ctk.CTk(fg_color='gray2')
janela.geometry('1000x650')
janela.resizable(False,False)
janela.title('NeoTrax')
janela.iconbitmap('imagens/ntx_logo.ico')
#ctk.set_appearance_mode('light')

#Uma tela scrolável, pro programa ter liberdade de crescer
conteudo_frame = ctk.CTkFrame(janela,844,670,fg_color='transparent')
conteudo_frame.place(x=129,y=10)

#Imagens usadas no programa:
configbtn_image = ctk.CTkImage(Image.open('imagens/cfg.png'))
info_btn_image = ctk.CTkImage(Image.open('imagens/inf.png'))
rotina_atualbtn_image = ctk.CTkImage(Image.open('imagens/rotina_atual.png'), size=(40,40))
rotinas_btn_image = ctk.CTkImage(Image.open('imagens/rotinas.png'), size=(30,30))
pontos_btn_image = ctk.CTkImage(Image.open('imagens/pontuacao.png'), size=(40,40))
pomodoro_btn_image = ctk.CTkImage(Image.open('imagens/pomodoro.png'), size=(40,40))
icone = Image.open('imagens/ntx_logo.ico')

#Configurações da Aba Lateral, a Navegação do programa
aba = ctk.CTkFrame(janela,120,680,fg_color='gray4')
aba.place(x=1,y=-4)
creditos = ctk.CTkLabel(aba,text='NeoTrax©-2025',text_color='snow3',font=('',10))
creditos.place(x=19,y=627)

#Iniciando o programa:
conteudo_rotina.rotina_atual(conteudo_frame,janela)

#Botões:

#Botão de Configuração (Configurações do programa)
configbtn = ctk.CTkButton(aba,10,10,text='',command=lambda: conteudo_config.config(conteudo_frame,janela),image=configbtn_image,fg_color='transparent',hover_color='gray4')
configbtn.place(x= 70,y=600)

#Botão de Ajuda (Ajuda o usuário a navegar pelo Programa, e também, mostra os créditos (autor, etc))
info_btn = ctk.CTkButton(aba,25,10,text='',command=lambda: conteudo_info.info(conteudo_frame,janela),image= info_btn_image,fg_color='transparent',hover_color='gray4')
info_btn.place(x=10,y=600)

#Botão Minha Rotina (Rotina do dia Atual)
rotina_atualbtn = ctk.CTkButton(aba,10,50,text='',image=rotina_atualbtn_image, fg_color='transparent',font=('',100), command=lambda: conteudo_rotina.rotina_atual(conteudo_frame,janela),hover_color='gray4')
rotina_atualbtn.place(x=33,y=35)

#Botão Rotinas (Todas as rotinas)
rotinas_btn = ctk.CTkButton(aba,10,50,text='',image=rotinas_btn_image, fg_color='transparent',font=('',100),command=lambda: conteudo_rotina.rotinas(conteudo_frame,janela),hover_color='gray4')
rotinas_btn.place(x=34,y=122)

#Botão de Pontuação (Mostra a pontuação do usuário)
pontos_btn = ctk.CTkButton(aba,10,50,text='',image=pontos_btn_image, fg_color='transparent',font=('',100),command=lambda:conteudo_pontuacao.pontuacao(conteudo_frame,janela,hoje),hover_color='gray4')
pontos_btn.place(x=33,y=210)

#Botão do Pomodoro pessoal
pomodoro_btn = ctk.CTkButton(aba,10,50,text='',image=pomodoro_btn_image, fg_color='transparent',font=('',100),command=lambda:conteudo_pomodoro.pomodoro(conteudo_frame,janela),hover_color='gray4')
pomodoro_btn.place(x=33,y=305)


#Funções que vão verificar o dia e horário para mostrar as notificações das tarefas
def decidir_dia_atual():
    dia_atual = datetime.datetime.now().strftime("%A")
    return dia_atual

def loop_diario(tela_principal):
        schedule.run_pending()
        tela_principal.after(1000, lambda: loop_diario(janela))

def recarregar_notifi():
    
    dia_atual = decidir_dia_atual()    
    dados = db.carregar_rotina(dia_atual)
    dados_ontem = db.carregar_rotina(ontem)
    
    #Aproveitando o sistema de verificação das notificações para poder excluir as tarefas temporarias do dia anterior, sempre checando caso o usuário use o programa aberto direto, sem fechar
    for linha in dados_ontem:
        db.cursor.execute('''DELETE FROM trax WHERE temporario = ? AND dia = ?''',('1',ontem))
        db.conexao.commit()
            
    for linha in dados:
        try:        
            schedule.every().day.at(linha[4]).do(lambda t= linha[1], i= linha[2]: conteudo_rotina.notificar(f'Começando: {t}',i))    
            schedule.every().day.at(linha[5]).do(lambda t= linha[1], i= linha[2]: conteudo_rotina.notificar(f'Terminando: {t}',i))
        except Exception as e:
            print('Notificação inexistente.',e)    

schedule.every(5).seconds.do(recarregar_notifi)            
loop_diario(janela)

#Área para levar o programa minimizado para a bandeja de aplicativos e deixar rodando em segundo plano
def esconder_programa():
    janela.withdraw()
    mostrar_na_bandeja()

def mostrar_programa(icone=None,item=None):
    janela.deiconify()
    bandeja.stop()

def encerrar_programa(icone,item):
    bandeja.stop()
    janela.destroy()
    db.encerrar_conexao()    

def mostrar_na_bandeja():
    global bandeja        
    menu = Menu(
        item('Abrir',mostrar_programa),
        item('Encerrar',encerrar_programa)
    )
    bandeja = Icon('NeoTrax',icone,'NeoTrax!',menu)
    threading.Thread(target=bandeja.run,daemon=True).start()

def checar_minimizar():
    if janela.state() == 'iconic':
        esconder_programa()
    janela.after(1000,checar_minimizar)    

#Vai checar se o programa foi minimizado e vai esconder ele na bandeja
checar_minimizar()

#Encerrando programa e banco de dados
janela.mainloop()
db.encerrar_conexao()