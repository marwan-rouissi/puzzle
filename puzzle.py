import pygame 
from pygame.locals import *
import random
import time 

# initialisation de la police
pygame.font.init()

## variables constantes 
#
# couleurs
#
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (100, 100, 100)
BG = BLACK
#
# paramètres de jeu
#
WIDTH = 1100
HEIGHT = 630
FPS = 60
title = "Slide Puzzle"
TILESIZE = 100
#
# mode de difficulté
#
EASY = 3 * TILESIZE
MEDIUM = 4 * TILESIZE
HARD = 5 * TILESIZE
#

class Tile(pygame.sprite.Sprite):
    # création d'un objet pour les cases

    def __init__(self, game, x, y, text):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.x, self.y = x + 0.5, y + 0.5
        self.text = text
        self.rect = self.image.get_rect()

        # si text est différent de "empty"
        if self.text != "empty":
            # création de la police du texte (font)
            self.font = pygame.font.SysFont("arial", 50)
            # application de cette police
            fontSurface = self.font.render(self.text, True, BLACK)
            # fond (bg) de la case 
            self.image.fill(WHITE)
            self.fontSize = self.font.size(self.text)

            # centrer le text dans les cases (tiles)
            drawX = (TILESIZE / 2) - self.fontSize[0] / 2
            drawY = (TILESIZE / 2) - self.fontSize[1] / 2

            # application du text au centre de la case
            self.image.blit(fontSurface, (drawX, drawY))

        else:
            # fond (bg) de la case vide 
            self.image.fill(GREY)
    
    def update(self):
        self.rect.x = self.x * TILESIZE
        self.rect.y = self.y * TILESIZE

    def click(self, mouseX, mouseY):
        # vérification de la position horizontale et verticale de la souris pat rapport à la case cliquée 
        return self.rect.left <= mouseX <= self.rect.right and self.rect.top <= mouseY <= self.rect.bottom

    def right(self):
        return self.rect.x + TILESIZE < self.game.gameSize * TILESIZE
    
    def left(self):
        return self.rect.x - TILESIZE >= 0
    
    def up(self):
        return self.rect.y - TILESIZE >= 0
    
    def down(self):
        return self.rect.y + TILESIZE < self.game.gameSize * TILESIZE


class screenText:
    # création d'un objet pour le texte affiché à l'écran

    def __init__(self, x, y, text):
        self.x, self.y = x, y
        self.text = text
    
    # dessiner le texte
    def draw(self, screen, fontSize):
        # création de la police du texte (font)
        font = pygame.font.SysFont("Consolas", fontSize)
        # application de cette police
        text = font.render(self.text, True, WHITE)
        
        screen.blit(text, (self.x, self.y))


class Button:
    # objet pour les boutons 

    def __init__(self, x, y, width, height, text, color, textColor) :
        self.color, self.textColor = color, textColor
        self.width, self.height = width, height
        self.x, self.y = x, y 
        self.text = text 

    # dessiner le bouton
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), 0, 20)
        font = pygame.font.SysFont("comics", 50)
        text = font.render(self.text, True, self.textColor)
        self.fontSize = font.size(self.text)

        # centrer le text dans les cases (tiles)
        drawX = self.x + (self.width / 2) - self.fontSize[0] / 2
        drawY = self.y + (self.height / 2) - self.fontSize[1] / 2

        screen.blit(text, (drawX, drawY))

    def click(self, mouseX, mouseY):
        # vérification de la position horizontale et verticale de la souris pat rapport à la case cliquée 
        return self.x <= mouseX <= self.x + self.width and self.y <= mouseY <= self.y + self.height


class Game:
    # création d'un objet pour le jeu
    
    def __init__(self):
        # initialiser pygame
        pygame.init()
        # affichage de l'écran
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        # affichage du titre de la fenêtre
        pygame.display.set_caption(title)
        # minuteur
        self.clock = pygame.time.Clock()
        #
        self.shuffleTime = 0
        # variable déterminant si l'action est active ou pas
        self.startShuffle = False
        # variable contenant le dernier choix random effectué
        self.previousChoice = ""
        #
        self.choice = ""
        # variable determinant si le jeu a commencé ou pas
        self.startGame = False
        # variable du timer initialement désactivé
        self.startTimer = False
        # variable contenant la valeur du temps écoulé
        self.elapsedTime = 0
        #
        self.tiles = []
        ## variable meilleur score
        # easy
        self.highScoreEasy = float(self.getHighScore()[0])
        # medium
        self.highScoreMedium = float(self.getHighScore()[1])
        # hard
        self.highScoreHard = float(self.getHighScore()[2])

    # récupérer le meilleur score encregistré
    def getHighScore(self):
        with open("scores.txt", "r") as file:
            scores = file.read().splitlines()
        return scores
    
    # sauvegarder le score
    def saveScore(self):
        with open("scores.txt", "w") as file:
            file.write(str("%.1f\n" % self.highScoreEasy))
            file.write(str("%.1f\n" % self.highScoreMedium))
            file.write(str("%.1f" % self.highScoreHard))

    def createGame(self, gameSize):
        # liste vide
        grid = []
        # variable nombre à ajouter à la liste
        number = 1

        # pour chaque x dans l'intervalle (nombre de cases horizontales)
        for x in range(gameSize):
            
            # ajouter une liste à la liste vide
            grid.append([])
        
        # pour chaque y dans l'intervalle (nombre de cases verticales)
            for y in range(gameSize):
                
                # ajouter la variable number à la liste nouvellement ajoutée (index[x]) 
                grid[x].append(number)
                
                # incrémenter number de 1
                number += 1

        # remplacer le dernier nombre ajouté par 0
        grid[-1][-1] = 0
        # print(grid)
        return grid
    
    def shuffle(self):
        # liste des mouvements possibles
        possibleMoves = []
        # pour toutes les cases contenues sur le plateau de jeu
        for row, tiles in enumerate(self.tiles):
            for col, tile in enumerate(tiles):
                # pour la case 0/vide/"empty"
                if tile.text == "empty":
                    # si mouvement à droite possible
                    if tile.right():
                        # ajouter le mouvement à la liste
                        possibleMoves.append("right")
                    # si mouvement à gauche possible
                    if tile.left():
                        # ajouter le mouvement à la liste
                        possibleMoves.append("left")
                    # si mouvement vers le haut possible
                    if tile.up():
                        # ajouter le mouvement à la liste
                        possibleMoves.append("up")
                    # si mouvement vers le bas possible
                    if tile.down():
                        # ajouter le mouvement à la liste
                        possibleMoves.append("down")
                    # interrompre la boucle
                    break
            # si la liste de mouvements possibles contient plus de 2 éléments
            if len(possibleMoves) > 0:
                # interrompre la boucle
                break
        
        # si le choix random précédent est mouvement vers la droite
        if self.previousChoice == "right":
            # retirer mouvement vers la gauche, seulement s'il est présent dans la liste des mouvements possibles
            possibleMoves.remove("left") if "left" in possibleMoves else possibleMoves
        # sinon si le choix random précédent est mouvement vers la gauche
        elif self.previousChoice == "left":
            # retirer mouvement vers la droite, seulement s'il est présent dans la liste des mouvements possibles
            possibleMoves.remove("right") if "right" in possibleMoves else possibleMoves
        # sinon si le choix random précédent est mouvement vers le haut
        elif self.previousChoice == "up":
            # retirer mouvement vers le bas, seulement s'il est présent dans la liste des mouvements possibles
            possibleMoves.remove("down") if "down" in possibleMoves else possibleMoves
        # sinon si le choix random précédent est mouvement vers le bas
        elif self.previousChoice == "down":
            # retirer mouvement vers le haut, seulement s'il est présent dans la liste des mouvements possibles
            possibleMoves.remove("up") if "up" in possibleMoves else possibleMoves

        # variable choix random
        choice = random.choice(possibleMoves)
        #
        self.previousChoice = choice
        # si le choix random est mouvement vers la droite
        if choice == "right":
            # intervertir les positions de ces 2 cases
            self.tiles_grid[row][col], self.tiles_grid[row][col + 1] = self.tiles_grid[row][col + 1], self.tiles_grid[row][col]
        # sinon si le choix random est mouvement vers la gauche
        elif choice == "left":
            # intervertir les positions de ces 2 cases
            self.tiles_grid[row][col], self.tiles_grid[row][col - 1] = self.tiles_grid[row][col - 1], self.tiles_grid[row][col]
        # sinon si le choix random est mouvement vers le haut
        elif choice == "up":
            # intervertir les positions de ces 2 cases
            self.tiles_grid[row][col], self.tiles_grid[row - 1][col] = self.tiles_grid[row - 1][col], self.tiles_grid[row][col]
        # sinon si le choix random est mouvement vers le bas
        elif choice == "down":
            # intervertir les positions de ces 2 cases
            self.tiles_grid[row][col], self.tiles_grid[row + 1][col] = self.tiles_grid[row + 1][col], self.tiles_grid[row][col]

    def drawTiles(self):
        self.tiles = []
        # pour l'index et son élément enuméré dans la liste (tiles_grid)
        for row, x in enumerate(self.tiles_grid):
            
            # ajouter une liste vide
            self.tiles.append([])

            # l'index et son élément énuméré dans la liste (x) ajoutée précédément
            for col, tile in enumerate(x):

                # si la case est différente de 0
                if tile != 0:
                    # dessiner la case (class Tile)
                    self.tiles[row].append(Tile(self, col, row, str(tile)))
                # sinon
                else:
                    # laisser vide
                    self.tiles[row].append(Tile(self, col, row, "empty"))

    def newGame(self):
        self.all_sprites = pygame.sprite.Group()

        # grille de jeu
        self.tiles_grid = self.createGame(self.gameSize)
        
        # grille de comparaison (grille de victoire)
        self.tiles_grid_completed = self.createGame(self.gameSize)

        ## reset variables
        # 
        self.elapsedTime = 0
        #
        self.moves = 0
        #  
        self.startTimer = False
        #
        self.startGame = False

        # dessiner les cases
        self.drawTiles()

        # liste des boutons 
        self.buttonList = []

        # boutons à ajouter à la liste
        self.buttonList.append(Button(775, 100, 200, 50, "Mélanger", WHITE, BLACK))
        self.buttonList.append(Button(775, 170, 200, 50, "Reset", WHITE, BLACK))
        self.buttonList.append(Button(800, 450, 150, 50, "facile", WHITE, BLACK))
        self.buttonList.append(Button(800, 510, 150, 50, "moyen", WHITE, BLACK))
        self.buttonList.append(Button(800, 570, 150, 50, "difficile", WHITE, BLACK))

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        
        # si le jeu est en cours
        if self.startGame:
            # si la grille actuelle est égale à la grille de vérification
            if self.tiles_grid == self.tiles_grid_completed:
                # le jeu sarrête / variable inactive
                self.startGame = False
                if self.gameChoice == EASY:
                  # si meilleur score supérieur 0
                  if self.highScoreEasy > 0:
                    # meilleur score = temps écoulé si temps écoulé inférieur à meilleur score sinon meilleur reste tel quel
                    self.highScoreEasy = self.elapsedTime if self.elapsedTime < self.highScoreEasy else self.highScoreEasy
                  # sinon
                  else:
                      # meilleur score = temps écoulé
                      self.highScoreEasy = self.elapsedTime
                elif self.gameChoice == MEDIUM:
                  if self.highScoreMedium > 0:
                    # meilleur score = temps écoulé si temps écoulé inférieur à meilleur score sinon meilleur reste tel quel
                    self.highScoreMedium = self.elapsedTime if self.elapsedTime < self.highScoreMedium else self.highScoreMedium
                # sinon
                  else:
                      # meilleur score = temps écoulé
                      self.highScoreMedium = self.elapsedTime
                elif self.gameChoice == HARD:
                  if self.highScoreHard > 0:
                      # meilleur score = temps écoulé si temps écoulé inférieur à meilleur score sinon meilleur reste tel quel
                      self.highScoreHard = self.elapsedTime if self.elapsedTime < self.highScoreHard else self.highScoreHard
                  # sinon
                  else:
                      # meilleur score = temps écoulé
                      self.highScoreEasy = self.elapsedTime  
                # sauvegarder le score
                self.saveScore()

            # si la varible est active
            if self.startTimer:
                # récupération du temps actuel
                self.timer = time.time()
                # variable déactivée
                self.startTimer = False
            # temps écoulé = temps actuel - temps récupéré plus haut    
            self.elapsedTime = time.time() - self.timer

        # si la variable est vraie
        if self.startShuffle:
            
            # appel de la fonction pour mélanger 
            self.shuffle()
            
            # appel de la fonction pour déssiner les cases
            self.drawTiles()
            
            # incrémentation du temps de mélange par 1
            self.shuffleTime += 1
            
            # si le temps de mélange est supérieur à 2s
            if self.shuffleTime > 120:
                
                # la variable n'est plus vraie
                self.startShuffle = False

                # la variable pour commencer le jeu est activée
                self.startGame = True

                # variable du timer activé
                self.startTimer = True
        
        # MAJ 
        self.all_sprites.update()
 
    # dessiner le plateau de jeu
    def drawGrid(self):
        
        # pour chaque ligne dans l'interval (-1, nombre de cases*taille de la case, taille de la case)
        for row in range(-1, self.gameChoice, TILESIZE):
            
            # dessiner une ligne qui a pox de la ligne, 0 en y) et pour coordonnées d'arrivée: (x de la ligne, nombre de cases*taille de la case en y)
            pygame.draw.line(self.screen, GREY, (row + 50, 50), (row + 50, self.gameChoice + 50))
        
        # pour chaque colonne dans l'interval (-1, nombre de cases*taille de la case, taille de la case)
        for col in range(-1, self.gameChoice, TILESIZE):
            
            # dessiner une colonne qui a : (0 en x), y de la colonne) et pour coordonnées d'arrivée: (nombre de cases*taille de la case en x, y de la colonne)
            pygame.draw.line(self.screen, GREY, (50, col + 50), (self.gameChoice + 50, col + 50))

    def draw(self):

        # appliquer une couleur de fond
        self.screen.fill(BG)
        
        self.all_sprites.draw(self.screen)

        # dessiner la grille de jeu
        self.drawGrid()

        # mode de jeu
        if self.gameChoice == EASY:
            screenText(820, 320, "Facile").draw(self.screen, 30)
            # text pour le score
            screenText(700, 380, "Meilleur Score - %.1f" % (self.highScoreEasy if self.highScoreEasy > 0 else 0)).draw(self.screen, 30)
        elif self.gameChoice == MEDIUM:
            screenText(820, 320, "Moyen").draw(self.screen, 30)
            # text pour le score
            screenText(700, 380, "Meilleur Score - %.1f" % (self.highScoreMedium if self.highScoreMedium > 0 else 0)).draw(self.screen, 30)
        elif self.gameChoice == HARD:
            screenText(800, 320, "Difficile").draw(self.screen, 30)
            # text pour le score
            screenText(700, 380, "Meilleur Score - %.1f" % (self.highScoreMedium if self.highScoreMedium > 0 else 0)).draw(self.screen, 30)  

        # dessiner les boutons contenus dans la liste dédiée
        for button in self.buttonList:
            button.draw(self.screen)
        
        # text pour le timer
        screenText(770, 35, "timer :  %.1f" % self.elapsedTime).draw(self.screen, 30)

        # text pour le nombre de coups joués
        screenText(770, 250, "coups :  %.0f" % self.moves).draw(self.screen, 30)

        # MAJ de l'affichage
        pygame.display.flip()

    def events(self):

        for event in pygame.event.get():
            # condition de sortie de boucle
            if event.type == pygame.QUIT:
                pygame.quit()
                quit(0)
            
            # pour tout event (touches clavier)
            if event.type == pygame.KEYDOWN:

                # pour toutes les cases contenues sur le plateau de jeu
                for row, tiles in enumerate(self.tiles):
                    for col, tile in enumerate(tiles):
                        
                        # pour la case vide
                        if tile.text == "empty":
                            # si touche directionnelle de gauche pressée
                            if event.key == K_LEFT and tile.left():

                                # intervertir sa position avec la case "empty"
                                self.tiles_grid[row][col], self.tiles_grid[row][col - 1] = self.tiles_grid[row][col - 1], self.tiles_grid[row][col]
                        
                            # si touche directionnelle de droite pressée
                            if event.key == K_RIGHT and tile.right():
                        
                                # intervertir sa position avec la case "empty"
                                self.tiles_grid[row][col], self.tiles_grid[row][col + 1] = self.tiles_grid[row][col + 1], self.tiles_grid[row][col]
                            
                            # si touche directionnelle du haut pressée
                            if event.key == K_UP and tile.up():

                                # intervertir sa position avec la case "empty"
                                self.tiles_grid[row][col], self.tiles_grid[row - 1][col] = self.tiles_grid[row - 1][col], self.tiles_grid[row][col]
                            
                            # si touche directionnelle du bas pressée
                            if event.key == K_DOWN and tile.down():
                                    
                                # intervertir sa position avec la case "empty"
                                self.tiles_grid[row][col], self.tiles_grid[row + 1][col] = self.tiles_grid[row + 1][col], self.tiles_grid[row][col]

                            # dessiner le nouvel emplacement des cases
                            self.drawTiles()
                            self.moves += 1
            
            # si la souris est cliquée
            if event.type == pygame.MOUSEBUTTONDOWN:
                # récupération de la position de la souris
                mouseX, mouseY = pygame.mouse.get_pos()

            ## décommenter l. 510 à 542 pour autorisé le deplacement des cases à l'aide de la souris 

                # # pour toutes les cases contenues sur le plateau de jeu
                # for row, tiles in enumerate(self.tiles):
                #     for col, tile in enumerate(tiles):

                #         # si la case cliquée 
                #         if tile.click(mouseX, mouseY):
                            
                #             # check s'il y a une case à droite de la case cliquée et si cette case est la case "0" / "empty" de notre liste de jeu
                #             if tile.right() and self.tiles_grid[row][col + 1] == 0:

                #                 # intervertir les positions de ces 2 cases
                #                 self.tiles_grid[row][col], self.tiles_grid[row][col + 1] = self.tiles_grid[row][col + 1], self.tiles_grid[row][col]
                            
                #             # check s'il y a une case à gauche de la case cliquée et si cette case est la case "0" / "empty" de notre liste de jeu
                #             if tile.left() and self.tiles_grid[row][col - 1] == 0:

                #                 # intervertir les positions de ces 2 cases
                #                 self.tiles_grid[row][col], self.tiles_grid[row][col - 1] = self.tiles_grid[row][col - 1], self.tiles_grid[row][col]

                #             # check s'il y a une case au dessus de la case cliquée et si cette case est la case "0" / "empty" de notre liste de jeu
                #             if tile.up() and self.tiles_grid[row - 1][col] == 0:

                #                 # intervertir les positions de ces 2 cases
                #                 self.tiles_grid[row][col], self.tiles_grid[row - 1][col] = self.tiles_grid[row - 1][col], self.tiles_grid[row][col]

                #             # check s'il y a une case en dessous de la case cliquée et si cette case est la case "0" / "empty" de notre liste de jeu
                #             if tile.down() and self.tiles_grid[row + 1][col] == 0:

                #                 # intervertir les positions de ces 2 cases
                #                 self.tiles_grid[row][col], self.tiles_grid[row + 1][col] = self.tiles_grid[row + 1][col], self.tiles_grid[row][col]

                #             self.drawTiles()
                #             self.moves += 1

                # pour les boutons dans la liste de boutons
                for button in self.buttonList:
                    # si le bouton est cliqué
                    if button.click(mouseX, mouseY):
                        
                        # si bouton facile cliqué
                        if button.text == "facile":
                              # changement des variables de jeu et taille du plateau en circonstance
                              self.gameChoice = EASY
                              self.gameSize = 3

                              # relancement du jeu avec nouvelles variables
                              self.newGame()
                        
                        # si bouton moyen est cliqué
                        if button.text == "moyen":
                            # changement des variables de jeu et taille du plateau en circonstance
                            self.gameChoice = MEDIUM
                            self.gameSize = 4

                            # relancement du jeu avec nouvelles variables
                            self.newGame()

                        # si bouton difficile est cliqué 
                        if button.text == "difficile":
                            # changement des variables de jeu et taille du plateau en circonstance
                            self.gameChoice = HARD
                            self.gameSize = 5

                            # relancement du jeu avec nouvelles variables
                            self.newGame()
                        
                        # si bouton Mélanger est cliqué
                        if button.text == "Mélanger":
                            # reset du temps de mélange et activation de la variable
                            self.moves = 0
                            self.shuffleTime = 0
                            self.startShuffle = True

                        # si bouton Reset est cliqué
                        if button.text == "Reset":
                            self.moves = 0
                            # relancement du jeu
                            self.newGame()

    # fonction pour lancer le jeu avec variables par défaut
    def showStartScreen(self):
      self.gameChoice = EASY
      self.gameSize = 3
    
# initialisation du jeu
game = Game()
game.showStartScreen()
while True:
    game.newGame()
    game.run()