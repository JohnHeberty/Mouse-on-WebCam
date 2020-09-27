# import the necessary packages
from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2 as cv
import pyautogui as py
import numpy as np

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-t", "--tracker", type=str, default="csrt",help="OpenCV object tracker type")
args = vars(ap.parse_args())

# CAPTURANDO VERSÃO DO OPENCV, EVITA ERROS AO ABRIR O RASTREADOR
(major, minor) = cv.__version__.split(".")[:2]

# INICIALIZANDO AS CAIXAS DELIMITADORAS DOS RASTREADORES
initMouse_Move = None
initMouse_Click = None

# NOME DA TELA QUE APARECE AS IMAGENS
ID_frame = 'Frame'

# INICIANDO CAPTURA DE VIDEO DA WEBCAM
print("[INFO] Iniciando a WebCam...")
cap = VideoStream(src=0).start()
time.sleep(1.0)

# CAPTURA IMAGEM DO MONITOR PRINCIPAL PARA OBTER SUAS DIMENSÕES
# PARA TER IDEIA DOS LIMITES DE MOVIMENTAÇÃO DO MOUSE
image_monitor = np.array(py.screenshot())
(Mon_H, Mon_W) = image_monitor.shape[:2]

# SALVA OQUE O MOUSE FAZ, TRUE CLICADO FALSE DESCLICADO
status_mouse = False
status_aux_click = False

# W DA IMAGEM, H E PROPORCIONAL
width = 500 # RESOLUÇÃO PARA PROCESSO DE RASTREAMENTO
width_show = 640 # RESOLUÇÃO PARA MOSTRAR NA TELA

# LOOP DO PROCESSO PRINCIPAL
while True:

    # CAPTURANDO IMAGEM DA CÂMERA
    frame = cap.read()
    # INVERTENDO A IMAGEM HORIZONTALMENTE PARA FACILITAR AO DESENHAR
    frame = cv.flip(frame, 1) 
	
    # CASO DE ALGUM ERRO DEVE PARAR O PROCESSO
    if frame is None:
        break
        
    # REDIMENSIOANDO A IMAGEM PARA BAIXO PARA PROCESSAR MAIS RÁPIDO
    frame = imutils.resize(frame, width=width)
    
    # DIMENSÇÕES DA IMAGEM
    (H, W) = frame.shape[:2]
    
    # COPIANDO O FRAME ORIGINAL PARA NÃO ESTRAGAR IMAGEM COM DESENHOS
    frame_copy = frame.copy()
    
    # VERIFIQUE SE OBJETO FOI RASTREADO
    if initMouse_Move is not None:
        # OBTENDO AS NOVAS COORDENADAS DAS CAIXAS DELIMITADORAS
        (success, box) = tracker_Move.update(frame)
        # VERIFICANDO SE DEU CERTO RASTREAMENTO
        if success:
            (x, y, w, h) = [int(v) for v in box]
            cv.rectangle(frame_copy, (x, y), (x + w, y + h), (50, 255, 50), 2)
            
        # MOVENDO O MOUSE, REGRA DE TREZ PARA CONVERTER TELA DO MOUSE PARA TELA TOTAL
        x_f = int(((Mon_W+w)/W)*(x+(w/2)))
        y_f = int(((Mon_H+h)/H)*(y+(h/2)))
        
        # EVITANDO ERROS DE NÚMEROS MAIORES OU MENORES QUE TAMANHO DA TELA
        if x_f >= Mon_W: x_f = Mon_W
        if x_f <= 0: x_f = 0
        if y_f >= Mon_H: y_f = Mon_H
        if y_f <= 0: y_f = 0
        
        # POR VENTURA PODE OCASIONAR ERROS QUE NÃO SEI RESOLVER
        try:
            py.moveTo(x_f,y_f)
        except:
            pass
        
        # VERIFICANDO POSIÇÃO DO MOUSE
        position = tuple(py.position())
        
        # PARANDO POIS ALGUEM TOCOU NO MOUSE
        if position != (x_f,y_f):
            break
        
    # VERIFIQUE SE OBJETO FOI RASTREADO
    if initMouse_Click is not None:
        # OBTENDO AS NOVAS COORDENADAS DAS CAIXAS DELIMITADORAS
        (success, box) = tracker_Click.update(frame)
        # VERIFICANDO SE DEU CERTO RASTREAMENTO
        if success:
            (x, y, w, h) = [int(v) for v in box]
            cv.rectangle(frame_copy, (x, y), (x + w, y + h), (50, 255, 50), 2)
            
        # CENTRO DA CAIXA RASTREADA
        x_c = int(x+(w)/2)
        y_c = int(y+(h)/2)
        
        # DELIMITAÇÃO DOS BOTÃO VERDE PARA CLICK
        if (x_c <= int(W/2)-2) and (y_c >= H-120):
            if status_mouse is False:
                status_mouse = True
                print('\n Click')
                try:
                    py.mouseDown()
                except:
                    pass
        
        # CASO SAIA DA REGIÃO UNCICK
        elif status_mouse is True:
            status_mouse = False
            try:
                py.mouseUp()
            except:
                pass
            print('\n UnClick')            
        
        # DELIMITAÇÃO DOS BOTÃO VERMELHO PARA CLICK AUXILIAR
        if (x_c >= int(W/2)+2) and (y_c >= H-120):
            if status_aux_click is False:
                status_aux_click = True
                try:
                    py.rightClick()
                except:
                    pass
                    
        # CASO SAIA DA REGIÃO UNCICK
        elif status_aux_click:
            status_aux_click = False
    
    cv.rectangle(frame_copy, (2, H-120), (int(W/2)-2, H-2), (0,255,0), 4) # DESENHANDO BOTÃO VERDE PARA USUARIO VER
    cv.rectangle(frame_copy, (int(W/2)+2, H-120), (W-2, H-2), (0,0,255), 4) # DESENHANDO BOTÃO VERMELHO PARA USUARIO VER
    
    # MOSTRANDO IMAGEM DE FUNDO CASO PEÇA PARA QUE SEJA MOSTRADO
    frame_copy = imutils.resize(frame_copy, width=width_show)
    # ESCREVENDO O TEMPO
    # cv.putText(frame_copy,'Follow Insta ToPraSerEng <3',(0,int(H/2)), cv.FONT_HERSHEY_SIMPLEX,2,(255,0,0),3,cv.LINE_AA)
    cv.imshow(ID_frame,frame_copy)
    key = cv.waitKey(1) & 0xFF
    
    # ESPERANDO 1MS PARA CLICAR W, CASO CLIQUE IRA DESATIVAR O MOSTRAR PROCESSO DE FUNDO
    if key in [ord('s'), ord('S')]:
        
        # se estivermos usando OpenCV 3.2 OU ANTES, podemos usar uma fábrica especial
        # função para criar nosso objeto tracker_Move
        if int(major) == 3 and int(minor) < 3:
            tracker_Move = cv.tracker_create(args["tracker"].upper())
            tracker_Click = cv.tracker_create(args["tracker"].upper())
            
        # caso contrário, para OpenCV 3.3 OR NEWER, precisamos chamar explicitamente o
        # construtor de movimento do rastreador de objeto apropriado:
        else:
            # inicializar um dicionário que mapeia strings para seus correspondentes
            # OpenCV object tracker_Move implementations
            OPENCV_OBJECT_TRACKERS = {
                "csrt": cv.TrackerCSRT_create,
                "kcf": cv.TrackerKCF_create,
                "boosting": cv.TrackerBoosting_create,
                "mil": cv.TrackerMIL_create,
                "tld": cv.TrackerTLD_create,
                "medianflow": cv.TrackerMedianFlow_create,
                "mosse": cv.TrackerMOSSE_create
			}
            # pegue o objeto apropriado tracker_Move usando nosso dicionário de
            # OpenCV object tracker_Move objects
            tracker_Move = OPENCV_OBJECT_TRACKERS[args["tracker"]]()
            tracker_Click = OPENCV_OBJECT_TRACKERS[args["tracker"]]()
        
        # CAIXA INICIAL ONDE SERA INICIADO O RASTREAMENTO
        box_Move = (int(W*(5/6))-75, int(H/2)-35), (int(W*(5/6)), int(H/2)+35)
        initMouse_Move = (box_Move[0][0],box_Move[0][1],box_Move[1][0]-box_Move[0][0],box_Move[1][1]-box_Move[0][1])
        
        # CAIXA INICIAL ONDE SERA INICIADO O RASTREAMENTO
        box_click = (int(W/5), int(H/2)-35), (int(W/5)+75, int(H/2)+35)
        initMouse_Click = (box_click[0][0],box_click[0][1],box_click[1][0]-box_click[0][0],box_click[1][1]-box_click[0][1])
        
        # CONTADOR DE TEMPO PARA INICIAR 
        time_count = 5
        
        # INICIANDO O CONTADOR DE TEMPO
        time_start = time.time()
        
        # VARIAVEL QUE SALVA O TEMPO PARA SER MOSTRADO CORRETAMENTE
        aux_time = 0
        
        # LOOP ATÉ QUE POSICIONE O DEDO NO LUGAR CORRETO
        while True:

            # CAPTURANDO IMAGEM DA CÂMERA
            frame = cap.read()
            # INVERTENDO A IMAGEM HORIZONTALMENTE PARA FACILITAR AO DESENHAR
            frame = cv.flip(frame, 1) 
            
            # REDIMENSIOANDO A IMAGEM PARA BAIXO PARA PROCESSAR MAIS RÁPIDO
            frame = imutils.resize(frame, width=width)
            
            # COPIANDO O FRAME ORIGINAL PARA NÃO ESTRAGAR IMAGEM COM DESENHOS
            frame_copy = frame.copy()
            
            # DESENHANDO LUAGAR CORRETO DOS BOX
            cv.rectangle(frame_copy, box_Move[0], box_Move[1], (255,0,0), 2)
            cv.rectangle(frame_copy, box_click[0], box_click[1], (255,0,0), 2)
            
            # SALVA O TEMPO PERCORRIDO
            tempo_percorrido = (time.time()-time_start)
            
            # ESCREVENDO O TEMPO
            cv.putText(frame_copy,str(round(tempo_percorrido,1)),(int(W/2)-50,int(H/2)), cv.FONT_HERSHEY_SIMPLEX,2,(255,0,0),3,cv.LINE_AA)
            
            # MOSTRANDO IMG NA TELA
            frame_copy = imutils.resize(frame_copy, width=width_show)
            cv.imshow(ID_frame,frame_copy)
            cv.waitKey(1)
            
            # CHEGOU AO FIM INICIE 
            if tempo_percorrido >= time_count:
                # INICIANDO O RASTREADOR DO OpenCV
                tracker_Move.init(frame, initMouse_Move) 
                tracker_Click.init(frame, initMouse_Click)
                break
                
    # ESPERANDO 1MS PARA CLICAR Q, CASO CLIQUE IRA PARAR
    if key in [ord('q'),ord('Q')]:
        break
    # ESPERANDO 1MS PARA CLICAR R, CASO CLIQUE IRA REINICIAR TODO PROCESSO
    if key in [ord('r'),ord('R')]:
        initMouse_Move = None
        initMouse_Click = None

# When everything done, release the capture
cap.stop()
cv.destroyAllWindows()