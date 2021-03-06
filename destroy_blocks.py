import os
import pygame
import random
import sys
import traceback
from collections import deque

os.chdir(os.path.dirname(__file__))

# Centralizar a janela do jogo na tela do computador
# if sys.platform in ["win32", "win64"]:
os.environ["SDL_VIDEO_CENTERED"] = "1"

# Inicializar PyGame
pygame.init()

# Definir backgrounds do jogo
bg_main = pygame.image.load('Imagens/main.png')  # Menu
background = pygame.image.load('Imagens/gamerun.png')  # Background
fim1 = pygame.image.load('Imagens/telafinal1.png')  # Tela final 1 player
fim2V = pygame.image.load('Imagens/telafinal2V.png')  # Tela final player red win
fim2A = pygame.image.load('Imagens/telafinal2A.png')  # Tela final player blue win
pause = pygame.image.load('Imagens/telapause.png')  # Tela de pausa
spark = pygame.image.load('Imagens/spark.png')  # Imagem de quando colide
sos = pygame.image.load('Imagens/ajuda.png')  # Tela de ajuda

# Definindo objetos do jogo
nave1 = pygame.image.load('Imagens/naveVermelha.png')  # Nave player 1
nave2 = pygame.image.load('Imagens/naveAzul.png')  # Nave player 2
bloco1 = pygame.image.load('Imagens/cometaVermelho.png')  # Cometa vermelho
bloco2 = pygame.image.load('Imagens/cometaAzul.png')  # Cometa azul

# Definir largura e comprimento da tela do jogo
(width, height) = (750, 700)
screen = pygame.display.set_mode((width, height))

# Definir nome do jogo
pygame.display.set_caption("Destroy Comets")

# Controlar o tempo de jogo e o FPS
clock = pygame.time.Clock()

# Algumas definições de fontes
font32 = pygame.font.SysFont("Orbit", 32)
font60 = pygame.font.SysFont("Orbit", 60)
font120 = pygame.font.SysFont("Orbit", 120)
font150 = pygame.font.SysFont("Orbit", 150)

# Arquivo .txt para guardar o Highest Score
file = open("hs.txt", "r")
highest_score = int(file.read().strip())
file.close()

# Algumas definições de cores
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BUTTON_PRESSED = (180, 20, 180)
BUTTON_NON_PRESSED = (0, 0, 0)


class Game:
    def __init__(self, player, diff):
        self.blocks_type = deque()
        self.line_org = [0, 0, 0, 0]
        # Posição 0: Relacionado com a cor vermelha
        # Posição 2: Relacionado com a cor azul

        self.score_1 = 0
        self.score_2 = 0
        self.diff = diff
        self.stop = 1000 * 60

        # Inicialização para 1 jogador
        if player == 1:
            self.player1_x = 105
            self.player1_y = 635
            self.player2_x = None
            self.player2_y = None

        # Inicialização para 2 jogadores
        if player == 2:
            self.player1_x = 105
            self.player1_y = 560
            self.player2_x = 105
            self.player2_y = 635

    # Geração dos cometas a serem destruídos
    def blocks(self):
        for i in range(0, 2):
            self.line_org[2 * i + 1] = 1

        if self.blocks_type:
            if self.blocks_type[0][0][1] > height:
                self.blocks_type.popleft()

            for elem in self.blocks_type:
                elem[0][1] = elem[0][1] + self.diff * 1

                if self.line_org[2 * elem[2]] > 0 and self.line_org[2 * elem[2] + 1] == 1:
                    self.line_org[2 * elem[2]] = self.line_org[2 * elem[2]] - self.diff * 2
                    self.line_org[2 * elem[2] + 1] = 0

                if elem[2]:
                    screen.blit(bloco1, (elem[0][0], elem[0][1]))
                else:
                    screen.blit(bloco2, (elem[0][0], elem[0][1]))

        line = random.randrange(1, 7)  # Escolher randomicamente uma das 6 colunas onde surgem os blocos
        color = random.randrange(2)  # Escolher randomicamente cor Azul ou Vermelha para o cometa

        # Impedir sobreposição de cometas
        if self.line_org[2 * color] == 0:
            if self.blocks_type and self.blocks_type[-1][1] == line:
                return
            if color:
                block = [[115 + 95 * (line - 1), 80, 65, 65], line, color]
                screen.blit(bloco1, (block[0][0], block[0][1]))
            else:
                block = [[115 + 95 * (line - 1), 80, 65, 65], line, color]
                screen.blit(bloco2, (block[0][0], block[0][1]))

            self.blocks_type.append(block)  # Insere o bloco na fila
            self.line_org[2 * color] = 200

    # Destruir blocos se o centro (x, y) do player estiver na região delimitada pelo cometa
    def destroy(self, x, y, player):
        isRemove = False
        for elem in self.blocks_type:
            if elem[0][0] < x < (elem[0][0] + elem[0][2]):
                if elem[0][1] < y < (elem[0][1] + elem[0][3]):
                    if player == elem[2] or (player - 2) == elem[2]:
                        isRemove = True  # Se atender as condições, remove o cometa
                        item = elem
                        # Aumentar a pontuação
                        if player == 1:
                            self.score_1 = self.score_1 + 1
                        if player == 2:
                            self.score_2 = self.score_2 + 1
                        break
        if isRemove:
            screen.blit(spark, (item[0][0], item[0][1]))
            pygame.display.update()
            self.blocks_type.remove(item)

    # Semelhante as destroy, mas aqui perde ponto caso atinga o cometa da cor errada
    def to_dodge(self, x, y, player):
        isRemove = False
        for elem in self.blocks_type:
            if elem[0][0] < x < (elem[0][0] + elem[0][2]):
                if elem[0][1] < y < (elem[0][1] + elem[0][3]):
                    if not (player == elem[2] or (player - 2) == elem[2]):
                        isRemove = True
                        item = elem
                        # Desconta pontuação
                        if player == 1:
                            self.score_1 = self.score_1 - 1
                        if player == 2:
                            self.score_2 = self.score_2 - 1
                        break
        if isRemove:
            screen.blit(spark, (item[0][0], item[0][1]))
            pygame.display.update()
            self.blocks_type.remove(item)

    # Mostrar quanto tempo falta para o fim da partida em formato de um retângulo
    def timer(self, start):
        x_time = (1 - (self.stop - (pygame.time.get_ticks() - start)) / self.stop) * 225  # Tempo restante
        pygame.draw.rect(screen, WHITE, (280, 68, 225, 20))
        pygame.draw.rect(screen, BLACK, (280, 68, x_time, 20))
        # Os 4 valores representam, respectivamente: x da origem, y da origem, comprimento e altura do retângulo

    def run(self):
        global highest_score  # Variável para armazenar a maior pontuação
        running = True
        start = pygame.time.get_ticks()

        # Loop enquanto estiver jogando
        while self.stop > (pygame.time.get_ticks() - start) and running:
            screen.fill((0, 0, 0))

            # Texto na tela para cada caso (1 ou 2 jogadores)
            if self.player2_x is None:
                screen.blit(background, (0, 0))
                screen.blit(font60.render("HS: " + "{}".format(highest_score), True, (0, 0, 0)), (325, 0))
                screen.blit(font60.render("P1: " + "{}".format(self.score_1), True, (255, 0, 0)), (10, 14))
            else:
                screen.blit(background, (0, 0))
                screen.blit(font60.render("HS: " + "{}".format(highest_score), True, (0, 0, 0)), (325, 0))
                screen.blit(font60.render("P1: " + "{}".format(self.score_1), True, (255, 0, 0)), (10, 14))
                screen.blit(font60.render("P2: " + "{}".format(self.score_2), True, (0, 0, 255)), (620, 14))

            # Sair da partida se pressionar o X no canto superior direito
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()

            # Pegar informações do teclado para movimentar o player 1

            # Mover player 1 para a esquerda
            if keys[pygame.K_LEFT] and self.player1_x > 105:
                self.player1_x -= 2
            # Mover player 1 para a direita
            if keys[pygame.K_RIGHT] and self.player1_x < 660:
                self.player1_x += 2
            # Destruir cometa vermelho
            if keys[pygame.K_DOWN]:
                self.destroy(self.player1_x + 32, self.player1_y + 32, 1)

            self.to_dodge(self.player1_x + 32, self.player1_y + 32, 1)
            screen.blit(nave1, (self.player1_x, self.player1_y))

            # Pegar informações do teclado para movimentar o player 2
            if self.player2_x is not None:
                # Mover player 2 para a esquerda
                if keys[pygame.K_a] and self.player2_x > 105:
                    self.player2_x -= 2
                # Mover player 2 para a direita
                if keys[pygame.K_d] and self.player2_x < 660:
                    self.player2_x += 2
                # Destruir cometa azul
                if keys[pygame.K_s]:
                    self.destroy(self.player2_x + 32, self.player2_y + 32, 2)

                self.to_dodge(self.player2_x + 32, self.player2_y + 32, 2)
                screen.blit(nave2, (self.player2_x, self.player2_y))

            self.blocks()
            self.timer(start)
            pygame.display.update()

            if keys[pygame.K_SPACE]:
                pause_run = True
                while pause_run:
                    mouse = pygame.mouse.get_pos()  # Determinar onde está o cursor do mouse
                    click = pygame.mouse.get_pressed()  # Saber se houve click do mouse
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pause_run = False

                        if 490 > mouse[0] > 250:
                            if 350 > mouse[1] > 320:
                                if click[0] == 1:
                                    pause_run = False

                        if 450 > mouse[0] > 300:
                            if 435 > mouse[1] > 400:
                                if click[0] == 1:
                                    pause_run = False
                                    running = False

                    pygame.display.update()
                    screen.blit(pause, (0, 0))

        running = True
        while running:
            # Atualizar a tela
            pygame.display.update()

            if self.score_2 == 0:
                screen.blit(fim1, (0, 0))
                screen.blit(font150.render("{}".format(self.score_1), True, (255, 0, 0)), (320, 290))
                # Atualizar a nova pontuação máxima
                if self.score_1 > highest_score:
                    highest_score = self.score_1
                screen.blit(font120.render("{}".format(highest_score), True, (255, 255, 255)), (540, 540))
            else:
                if self.score_1 > self.score_2:
                    screen.blit(fim2V, (0, 0))
                    screen.blit(font150.render("{}".format(self.score_1), True, (255, 0, 0)), (370, 300))
                    screen.blit(font150.render("{}".format(self.score_2), True, (0, 0, 255)), (370, 400))
                    # Atualizar a nova pontuação máxima
                    if self.score_1 > highest_score:
                        highest_score = self.score_1

                    screen.blit(font120.render("{}".format(highest_score), True, (255, 255, 255)), (570, 570))

                elif self.score_2 > self.score_1:
                    screen.blit(fim2A, (0, 0))
                    screen.blit(font150.render("{}".format(self.score_1), True, (255, 0, 0)), (370, 300))
                    screen.blit(font150.render("{}".format(self.score_2), True, (0, 0, 255)), (370, 400))
                    # Atualizar a nova pontuação máxima
                    if self.score_2 > highest_score:
                        highest_score = self.score_2

                    screen.blit(font120.render("{}".format(highest_score), True, (255, 255, 255)), (570, 570))

                else:
                    highest_score = self.score_2

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False


# Definir botões na tela inicial para configurar o jogo (jogadores e tempo de jogo)
def button(main_org):
    global highest_score  # Variável para armazenar a maior pontuação
    mouse = pygame.mouse.get_pos()  # Determinar onde está o cursor do mouse
    click = pygame.mouse.get_pressed()  # Saber se houve click do mouse

    # Explorar cada evento no mouse ou no teclado
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        # Detectar se o cursor do mouse está dentro das regiões onde ficam os botões e executar ações quando clicar
        if 215 + 60 > mouse[0] > 215:
            if 320 + 60 > mouse[1] > 320:
                if click[0] == 1:
                    if main_org[1] == 0:
                        main_org[0] = 1
                        main_org[1] = 1
                        break
                    if main_org[1] == 1:
                        main_org[0] = 0
                        main_org[1] = 0
                        break
            if 400 + 60 > mouse[1] > 400:
                if click[0] == 1:
                    if main_org[1] == 0:
                        main_org[0] = 2
                        main_org[1] = 1
                        break
                    if main_org[1] == 1:
                        main_org[0] = 0
                        main_org[1] = 0
                        break

        if 565 + 60 > mouse[0] > 565:
            if 320 + 60 > mouse[1] > 320:
                if click[0] == 1:
                    if main_org[3] == 0:
                        main_org[2] = 2
                        main_org[3] = 1
                        break
                    if main_org[3] == 1:
                        main_org[2] = 0
                        main_org[3] = 0
                        break
            if 400 + 60 > mouse[1] > 400:
                if click[0] == 1:
                    if main_org[3] == 0:
                        main_org[2] = 1
                        main_org[3] = 1
                        break
                    if main_org[3] == 1:
                        main_org[2] = 0
                        main_org[3] = 0
                        break
        
        # Botão Help: Encaminha para a página de ajuda para jogar
        if 460 > mouse[0] > 315:
            if 660 > mouse[1] > 590:
                if click[0] == 1:
                    help()

        # Botão GO!: Dar início ao jogo se as opções de jogadores e tempo tiverem sido escolhidas
        if main_org[1] == 1 and main_org[3] == 1:
            if 345 + 60 > mouse[0] > 345 and 595 + 60 > mouse[1] > 535:
                if click[0] == 1:
                    game = Game(main_org[0], main_org[2])
                    game.run()

    return True


def help():
    screen.blit(sos, (0, 0))
    running = True
    while running:
        # Atualizar a tela
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.display.update()  # Atualizar a tela


# Desenhar os botões na tela inicial
def draw(main_org):
    global blink
    screen.blit(bg_main, (0, 0))  # Background do menu inicial

    # Escrever o Highest Score na tela inicial
    screen.blit(font60.render("HS: {}".format(highest_score), True, (0, 0, 0)), (50, 610))

    # Colocar os botões na tela inicial, alterando cores quando selecionados
    if main_org[1] == 1:
        if main_org[0] == 1:
            pygame.draw.circle(screen, BUTTON_PRESSED, (245, 350), 30)
            pygame.draw.circle(screen, BUTTON_NON_PRESSED, (245, 430), 30)
        if main_org[0] == 2:
            pygame.draw.circle(screen, BUTTON_NON_PRESSED, (245, 350), 30)
            pygame.draw.circle(screen, BUTTON_PRESSED, (245, 430), 30)

    if main_org[1] == 0:
        pygame.draw.circle(screen, BUTTON_NON_PRESSED, (245, 350), 30)
        pygame.draw.circle(screen, BUTTON_NON_PRESSED, (245, 430), 30)

    if main_org[3] == 1:
        if main_org[2] == 1:
            pygame.draw.circle(screen, BUTTON_NON_PRESSED, (595, 350), 30)
            pygame.draw.circle(screen, BUTTON_PRESSED, (595, 430), 30)
        if main_org[2] == 2:
            pygame.draw.circle(screen, BUTTON_PRESSED, (595, 350), 30)
            pygame.draw.circle(screen, BUTTON_NON_PRESSED, (595, 430), 30)

    if main_org[3] == 0:
        pygame.draw.circle(screen, BUTTON_NON_PRESSED, (595, 350), 30)
        pygame.draw.circle(screen, BUTTON_NON_PRESSED, (595, 430), 30)

    pygame.display.update()  # Atualizar a tela


def main():
    main_org = [0, 0, 0, 0]
    # Posição 0: Se for 1, será 1 jogador. Se for 2, serão 2 jogadores
    # Posição 1: indica se o botão de seleção de quantidade de jogadores está apertado
    # Posição 1: Se for 1, será 1 min.Se for 2, serão 2 min
    # Posição 3: indica se o botão de seleção de tempo de jogo está apertado

    while True:
        draw(main_org)
        if not button(main_org):
            break
        clock.tick(100)  # Controla a velocidade do jogo

        # Atualizar valor do Highest Score no arquivo .txt
        file = open("hs.txt", "w")
        file.write(str(highest_score))
        file.close()


if __name__ == "__main__":
    try:
        main()

    except:
        traceback.print_exc()
        pygame.quit()
        input()
