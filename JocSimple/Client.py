import pygame
import socket
import pickle

# Configuració del client
HOST = 'localhost'  # Direcció IP del servidor
PORT = 5000        # Port de connexió

# Inicialitzar Pygame
pygame.init()

WIDTH, HEIGHT = 800, 900 # Mida finestra
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Crear una font per al text del nom del jugador
font = pygame.font.Font(None, 24)

# Crear una font per al text del missatge de la partida
font2 = pygame.font.Font(None, 50)

# Inicialitzar el socket del client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# Obtenir les posicions inicials i direcció de projectils des del servidor
data = client_socket.recv(4096)
jp_forma, js_forma, player_projectile_direction, direccio_projectils_js = pickle.loads(data)

# Nom del usuari
nom_jugador = "Tu"

# Llista de projectils del jugador
projectils_jp = []

# Cooldown entre projectils
shoot_cooldown = 0

# Variable per a controlar si el jugador ha perdut
has_perdut = False

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    if not has_perdut:
        # Moviment del personatge
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and jp_forma.left > 0:
            jp_forma.x -= 5
        if keys[pygame.K_RIGHT] and jp_forma.right < WIDTH:
            jp_forma.x += 5
        if keys[pygame.K_UP] and jp_forma.top > 0:
            jp_forma.y -= 5
        if keys[pygame.K_DOWN] and jp_forma.bottom < HEIGHT:
            jp_forma.y += 5
        
        # Verificar si el jugador xoca amb la paret
        if jp_forma.colliderect(pygame.Rect(WIDTH // 2 - 5, 0, 10, HEIGHT)):
            if jp_forma.left < WIDTH // 2:
                jp_forma.right = WIDTH // 2 - 5
            else:
                jp_forma.left = WIDTH // 2 + 5
             
        # Disparar un projectil si el cooldown està en 0
        if keys[pygame.K_SPACE] and shoot_cooldown == 0:
            projectile_rect = pygame.Rect(jp_forma.centerx, jp_forma.top, 10, 10)
            projectils_jp.append(projectile_rect)
            shoot_cooldown = 30  # Establir el cooldown a 30 frames (0.5 segons)
        
        # Moure els projectils del jugador
        for projectile in projectils_jp:
            projectile.x += 5 * player_projectile_direction
    
            # Eliminar el projectil si toca les vores de la pantalla
            if projectile.right < 0 or projectile.left > WIDTH:
                projectils_jp.remove(projectile)
        
        # Actualitzar el cooldown
        shoot_cooldown = max(0, shoot_cooldown - 1)
    
    # Enviar la posició del jugador i els projectils al servidor
    data = pickle.dumps((jp_forma, projectils_jp))
    client_socket.sendall(data)
    
    try:
        # Rebre la posició de l'altre jugador i els projectils des del servidor
        data = client_socket.recv(4096)
        js_forma, projectils_js, direccio_projectils_js = pickle.loads(data)
    except:
        break

    if not has_perdut:
        for projectile in projectils_js:
            if projectile.colliderect(jp_forma): 
                # Eliminar al jugador principal i al projectil
                jp_forma = pygame.Rect(0, 0, 0, 0)
                nom_jugador = ""
                projectils_jp = []
                has_perdut = True
                break
    
    # Moure els projectils de l'altre jugador
    for projectile in projectils_js:
        projectile.x += 5 * direccio_projectils_js
    
    # Actualitzar la pantalla
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (0, 0, 255), jp_forma)
    pygame.draw.rect(screen, (255, 0, 0), js_forma)
    
    # Dibuixar els projectils del jugador
    for projectile in projectils_jp:
        pygame.draw.rect(screen, (255, 255, 0), projectile)
    
    # Dibuixar els projectils de l'altre jugador
    for projectile in projectils_js:
        pygame.draw.rect(screen, (255, 255, 0), projectile)
    
    # Dibuixar-la paret
    pygame.draw.line(screen, (255, 255, 255), (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 10)
    
    # Mostrar el nom del jugador
    nom_jugador_format = font.render(nom_jugador, True, (255, 255, 255))
    nom_jugador_posicio = nom_jugador_format.get_rect()
    nom_jugador_posicio.center = jp_forma.center
    screen.blit(nom_jugador_format, nom_jugador_posicio)
    
    # Mostrar missatge si el jugador ha perdut
    if has_perdut:
        missatge_partida = font2.render("Has Perdut...", True, (0, 143, 57))
        format_missatge = missatge_partida.get_rect()
        format_missatge.center = (WIDTH // 2, HEIGHT // 2)
        screen.blit(missatge_partida, format_missatge)
    
    # Mostrar missatge si el jugador ha guanyat
    elif not js_forma and not projectils_js:
        missatge_partida = font2.render("Has Guanyat!!", True, (0, 143, 57))
        format_missatge = missatge_partida.get_rect()
        format_missatge.center = (WIDTH // 2, HEIGHT // 2)
        screen.blit(missatge_partida, format_missatge)
    
    pygame.display.flip()
    
    # Limitar la velocitat d'actualització
    clock.tick(60)

# Tancar el socket i finalitzar Pygame
client_socket.close()
pygame.quit()