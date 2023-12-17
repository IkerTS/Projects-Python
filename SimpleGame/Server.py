import pygame
import socket
import pickle
import os

os.environ['SDL_VIDEODRIVER'] = 'dummy'

# Configuració del servidor
HOST = 'localhost'  # Direcció IP del servidor
PORT = 5000        # Port de conmexió

# Inicialitzar Pygame
pygame.init()

WIDTH, HEIGHT = 800, 900 # Mida finestra
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Crear un rectangle com a personatge per al jugador principal
jp_forma = pygame.Rect(0, 0, 50, 50)
jp_color = (0, 0, 255)

# Crear un rectangle com a personatge per al jugador secundari
js_forma = pygame.Rect(0, 0, 50, 50)
js_color = (255, 0, 0)

# Direcció dels projectils de cada jugador (1: dreta, -1: esquerra)
direccio_projectils_jp = 1
direccio_projectils_js = -1

# Inicialitzar el socket del servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(2)  # Acceptar fins 2 connexions
print("Esperan connexions...")

# Acceptar les connexions entrants
clients_sockets = []
while len(clients_sockets) < 2:
    client_socket, addr = server_socket.accept()
    clients_sockets.append(client_socket)
    print("Connexió establerta des de", addr)

# Generar posicions inicials úniques per a cada jugador
jp_posicio_inicial = pygame.Rect(50, 350, 50, 50)  # Posició inicial del jugador principal
js_posicio_inicial = pygame.Rect(WIDTH - 100, 350, 50, 50)  # Posició inicial del jugador secundari

# Enviar les posicions inicials i adreça de projectils als clients
data = pickle.dumps((jp_posicio_inicial, js_posicio_inicial, direccio_projectils_jp, direccio_projectils_js))
clients_sockets[0].sendall(data)
data = pickle.dumps((js_posicio_inicial, jp_posicio_inicial, direccio_projectils_js, direccio_projectils_jp))
clients_sockets[1].sendall(data)

# Llistes de projectils de cada jugador
projectils_jp = []
projectils_js = []

while True:
    # Obtenir la posició del jugador des del client 1
    try:
        data = clients_sockets[0].recv(4096)
        jp_forma, projectils_jp = pickle.loads(data)
    except:
        break

    for projectil in projectils_jp:
        if projectil.colliderect(js_forma):
            # Eliminar al jugador secundari i al projectil  
            js_forma = pygame.Rect(0, 0, 0, 0)
            nom_jugador = ""
            projectils_js = []
            break
    
    # Obtenir la posició del jugador des del client 2
    try:
        data = clients_sockets[1].recv(4096)
        js_forma, projectils_js = pickle.loads(data)
    except:
        break
    
    # Actualitzar la posició dels projectils del jugador principal
    for projectil in projectils_jp:
        projectil.x += 5 * direccio_projectils_jp
    
    # Actualitzar la posició dels projectils del jugador secundari
    for projectil in projectils_js:
        projectil.x += 5 * direccio_projectils_js
    
    # Enviar la posició de l'altre jugador i els projectils a cada client
    data = pickle.dumps((js_forma, projectils_js, direccio_projectils_js))
    clients_sockets[0].sendall(data)
    
    data = pickle.dumps((jp_forma, projectils_jp, direccio_projectils_jp))
    clients_sockets[1].sendall(data)
    
    # Actualitzar la pantalla
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, jp_color, jp_forma)
    pygame.draw.rect(screen, js_color, js_forma)
    
    # Dibuixar els projectils del jugador principal
    for projectil in projectils_jp:
        pygame.draw.rect(screen, (255, 255, 0), projectil)
    
    # Dibuixar els projectils del jugador secundari
    for projectil in projectils_js:
        pygame.draw.rect(screen, (255, 255, 0), projectil)
    
    # Dibuixar-la paret
    pygame.draw.line(screen, (255, 255, 255), (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 10)
    
    pygame.display.flip()
    
    # Limitar la velocitat d'actualització
    clock.tick(60)

# Tancar els sockets i finalitzar Pygame
for client_socket in clients_sockets:
    client_socket.close()

server_socket.close()
pygame.quit()
