import pygame
import random
import sys
import math
import os

pygame.init()

# -----------------------------
# CONFIGURAÇÕES DA TELA
# -----------------------------
LARGURA = 800
ALTURA = 400
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo do Dinossauro 🦖")

# -----------------------------
# CORES
# -----------------------------
AZUL_CLARO = (180, 230, 255)
LARANJA = (255, 180, 100)
AZUL_ESCURO = (20, 20, 60)
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
AMARELO = (255, 240, 100)
LARANJA_SOL = (255, 200, 80)
VERDE_DASH = (100, 255, 150)
VERDE_CHAO = (0, 180, 0)

clock = pygame.time.Clock()
FPS = 60

fonte = pygame.font.SysFont(None, 40)
fonte_pequena = pygame.font.SysFont(None, 30)

gravidade = 1
velocidade_jogo_base = 10

# -----------------------------
# PATHS
# -----------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SPRITE_DIR = os.path.join(SCRIPT_DIR, "sprite")

def carregar_imagem(nome_arquivo, scale=None):
    caminho = os.path.join(SPRITE_DIR, nome_arquivo)
    try:
        img = pygame.image.load(caminho).convert_alpha()
        if scale is not None:
            img = pygame.transform.smoothscale(img, scale)
        return img
    except:
        return None

# ============================================================
# FUNÇÕES VISUAIS
# ============================================================
def interpolar_cor(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def desenhar_degrade(tela, c1, c2):
    for y in range(ALTURA):
        t = y / ALTURA
        cor = interpolar_cor(c1, c2, t)
        pygame.draw.line(tela, cor, (0, y), (LARGURA, y))

def desenhar_sol(tela, t):
    x = int(t * LARGURA)
    y = int(200 - 150 * math.sin(math.pi * t))
    if 0 <= x <= LARGURA:
        pygame.draw.circle(tela, LARANJA_SOL, (x, y), 30)

# ============================================================
# DASH SYSTEM
# ============================================================
class DashSystem:
    def __init__(self, dash_vel=21, dash_frames=15, dash_cooldown=7000):
        self.dash_vel = dash_vel
        self.dash_frames = dash_frames
        self.dash_timer = 0
        self.invulneravel = False
        self.dash_cooldown = dash_cooldown
        self.ultimo_dash = -dash_cooldown

    def tentar_iniciar_dash(self):
        agora = pygame.time.get_ticks()
        if not self.dash_timer and agora - self.ultimo_dash >= self.dash_cooldown:
            self.dash_timer = self.dash_frames
            self.invulneravel = True
            self.ultimo_dash = agora
            return True
        return False

    def atualizar_dash(self, x, direcao):
        if self.dash_timer > 0:
            x += self.dash_vel * direcao
            self.dash_timer -= 1
            if self.dash_timer == 0:
                self.invulneravel = False
        return x

    def tempo_restante(self):
        resto = pygame.time.get_ticks() - self.ultimo_dash
        if resto >= self.dash_cooldown:
            return 0
        return (self.dash_cooldown - resto) / 1000

    def pronto(self):
        return self.tempo_restante() <= 0

# ============================================================
# CLASSES DO JOGO
# ============================================================
class Dino(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        img = carregar_imagem("coelho.png", scale=(64, 64))
        if img:
            self.image_original = img
        else:
            s = pygame.Surface((64, 64))
            s.fill((0, 150, 0))
            self.image_original = s

        self.image = self.image_original.copy()
        self.rect = self.image.get_rect()
        self.rect.x = 80
        self.rect.y = ALTURA - 100
        self.vel_y = 0
        self.pulando = False
        self.vel_x = 5
        self.direcao = 1
        self.tempo_pulo = 0

        self.dash = DashSystem(dash_vel=24, dash_frames=15)

    def update(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.direcao = -1
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.direcao = 1

        if self.dash.dash_timer > 0:
            self.rect.x = self.dash.atualizar_dash(self.rect.x, self.direcao)
            self.image = self.image_original.copy()
            self.image.fill(VERDE_DASH, special_flags=pygame.BLEND_RGB_ADD)
            return

        if keys[pygame.K_a]:
            self.rect.x -= self.vel_x
        if keys[pygame.K_d]:
            self.rect.x += self.vel_x

        if self.pulando and keys[pygame.K_SPACE] and self.tempo_pulo < 15:
            self.vel_y -= 0.8
            self.tempo_pulo += 1

        self.vel_y += gravidade
        self.rect.y += self.vel_y

        if self.rect.bottom >= ALTURA - 50:
            self.rect.bottom = ALTURA - 50
            self.pulando = False
            self.vel_y = 0
            self.tempo_pulo = 0

        self.rect.x = max(0, min(self.rect.x, LARGURA))
        self.image = self.image_original.copy()

    def pular(self):
        if not self.pulando and not self.dash.invulneravel:
            self.vel_y = -16
            self.pulando = True
            self.tempo_pulo = 0
            return True
        return False

    def dash_acao(self):
        return self.dash.tentar_iniciar_dash()

    def get_cooldown_info(self):
        return self.dash.pronto(), self.dash.tempo_restante()


# ============================================================
# CACTO 50% MAIS LARGO
# ============================================================
class Cacto(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        img = carregar_imagem("arbusto.png", scale=(60, 60))
        if img:
            self.image = img
        else:
            self.image = pygame.Surface((30, 50))
            self.image.fill((200, 0, 0))

        self.rect = self.image.get_rect()
        self.rect.width *= 1.5
        self.rect.bottom = ALTURA - 50
        self.rect.x = LARGURA
        self.vel = 10

    def update(self):
        self.rect.x -= self.vel
        if self.rect.right < 0:
            self.kill()

# ============================================================
# PÁSSARO
# ============================================================
class Voador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        img = carregar_imagem("passaro.png", scale=(96, 64))
        if img:
            self.image = img
        else:
            self.image = pygame.Surface((80, 60))
            self.image.fill((150, 0, 200))

        self.rect = self.image.get_rect()
        self.rect.width *= 2
        self.rect.height *= 0.5
        self.rect.x = LARGURA
        self.rect.y = random.randint(50, ALTURA - 150)
        self.vel = random.randint(7, 11)

    def update(self):
        self.rect.x -= self.vel
        if self.rect.right < 0:
            self.kill()

# ============================================================
# NUVEM
# ============================================================
class Nuvem(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((60, 30), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (255,255,255,160), (0,0,60,30))
        self.rect = self.image.get_rect()
        self.rect.x = LARGURA + random.randint(0,100)
        self.rect.y = random.randint(30,150)
        self.vel = random.uniform(1,3)

    def update(self):
        self.rect.x -= self.vel
        if self.rect.right < 0:
            self.kill()

# ============================================================
# **CHÃO VERDE**
# ============================================================
class Chao:
    def __init__(self):

        self.image = pygame.Surface((LARGURA, ALTURA//3))
        self.image.fill(VERDE_CHAO)

        self.y = ALTURA - ALTURA//3
        self.x1 = 0
        self.x2 = LARGURA

    def update(self, vel):
        self.x1 -= vel
        self.x2 -= vel
        if self.x1 + LARGURA < 0: self.x1 = self.x2 + LARGURA
        if self.x2 + LARGURA < 0: self.x2 = self.x1 + LARGURA

    def draw(self, t):
        t.blit(self.image, (self.x1, self.y))
        t.blit(self.image, (self.x2, self.y))


# ============================================================
# CICLO DE FUNDO
# ============================================================
def atualizar_ciclo_visual(tela,pontos):
    t = pontos/800
    if t < .5:
        cor_topo = interpolar_cor(AZUL_CLARO,LARANJA,t*2)
        cor_base = interpolar_cor(BRANCO,(255,200,120),t*2)
    elif t<1:
        cor_topo = interpolar_cor(LARANJA,AZUL_ESCURO,(t-.5)*2)
        cor_base = interpolar_cor((255,200,120),(30,30,60),(t-.5)*2)
    else:
        cor_topo = AZUL_ESCURO
        cor_base = (20,20,50)

    desenhar_degrade(tela,cor_topo,cor_base)
    desenhar_sol(tela,t)

# ============================================================
# GAME OVER
# ============================================================
def tela_game_over(pontos):
    while True:
        TELA.fill(AZUL_ESCURO)
        fim = fonte.render(f"GAME OVER - Pontos: {int(pontos)}", True, BRANCO)
        TELA.blit(fim, (200, 120))
        TELA.blit(fonte.render("R - Reiniciar", True, AMARELO), (220, 200))
        TELA.blit(fonte.render("ESC - Sair", True, BRANCO), (240, 250))
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT: sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: return
                if e.key == pygame.K_ESCAPE: sys.exit()

# ============================================================
# LOOP PRINCIPAL
# ============================================================
def jogo():
    pontos = 0
    velocidade = velocidade_jogo_base

    dino = Dino()
    chao = Chao()

    grupo = pygame.sprite.Group(dino)
    cactus = pygame.sprite.Group()
    inimigos = pygame.sprite.Group()
    nuvens = pygame.sprite.Group()

    t_cacto = t_inimigo = t_nuvem = pygame.time.get_ticks()

    while True:
        clock.tick(FPS)
        pontos += .4
        velocidade = velocidade_jogo_base + pontos*0.01

        atualizar_ciclo_visual(TELA,pontos)

        for e in pygame.event.get():
            if e.type == pygame.QUIT: sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE: dino.pular()
                if e.key == pygame.K_q: dino.dash_acao()

        tempo = pygame.time.get_ticks()

        if tempo - t_cacto > 1200:
            c = Cacto()
            c.vel = velocidade
            grupo.add(c); cactus.add(c); inimigos.add(c)
            t_cacto = tempo

        if tempo - t_inimigo > 4000:
            v = Voador()
            grupo.add(v); inimigos.add(v)
            t_inimigo = tempo

        if tempo - t_nuvem > 3000:
            n = Nuvem()
            grupo.add(n); nuvens.add(n)
            t_nuvem = tempo

        grupo.update()
        chao.update(velocidade)

        nuvens.draw(TELA)
        chao.draw(TELA)
        grupo.draw(TELA)

        TELA.blit(fonte.render(f"Pontos: {int(pontos)}",True,PRETO),(10,10))

        if not dino.dash.invulneravel:
            if pygame.sprite.spritecollide(dino,inimigos,False):
                return int(pontos)

        pygame.display.flip()

# ============================================================
# EXECUÇÃO
# ============================================================
while True:
    tela_game_over(jogo())
