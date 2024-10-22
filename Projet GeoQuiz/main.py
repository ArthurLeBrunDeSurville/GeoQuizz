#                                                       /$$$$$$      /$$              /$$$$$$            /$$                                                                    #   
#                                                      /$$__  $$    | $/             /$$__  $$          |__/                                                                    #   
#                                                     | $$  \__/  /$$$$$$   /$$$$$$ | $$  \ $$ /$$   /$$ /$$ /$$$$$$$$                                                          #   
#                                                     | $$ /$$$$ /$$__  $$ /$$__  $$| $$  | $$| $$  | $$| $$|____ /$$/                                                          #   
#                                                     | $$|_  $$| $$$$$$$$| $$  \ $$| $$  | $$| $$  | $$| $$   /$$$$/                                                           #   
#                                                     | $$  \ $$| $$_____/| $$  | $$| $$/$$ $$| $$  | $$| $$  /$$__/                                                            #   
#                                                     |  $$$$$$/|  $$$$$$$|  $$$$$$/|  $$$$$$/|  $$$$$$/| $$ /$$$$$$$$                                                          #   
#                                                      \______/  \_______/ \______/  \____ $$$ \______/ |__/|________/                                                          #   
#                                                                                         \__/                                                                                  #             
import pygame
import tkinter as tk
from tkinter import ttk
import csv
import random
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math
import time
from pathlib import Path

path = Path(__file__, '..').resolve()           # Récupère le chemin du dossier contenant le fichier main.py (permet d'éviter certaines erreurs lors de l'imporation de fichiers)

class Fenetre():                                # Classe principale de l'application
    
    def __init__(self):                         # Constructeur de la classe Fenetre
        
        ####################################### Création de la fenêtre principale #######################################                                                          

        self.racine = tk.Tk()                                                               # Création de la fenêtre principale
        self.racine.title("GéoQuiz")                                                        # Titre de la fenêtre
        self.racine.resizable(width=False, height=False)                                    # On empêche le redimensionnement de la fenêtre graphique
        self.racine.protocol('WM_DELETE_WINDOW', self.fermerApp)                            # Fonction qui permet de fermer l'application proprement
        self.f_graph = None                                                                 # Variable qui contiendra la fenêtre de jeu             
        self.f_param = None                                                                 # Variable qui contiendra la fenêtre des paramètres
        self.f_graphPVC = None                                                              # Variable qui contiendra la fenêtre du problème du voyageur de commerce
        self.moniteurWidth = self.racine.winfo_screenwidth()                                # Récupère la largeur de l'écran
        self.moniteurHeight = self.racine.winfo_screenheight()                              # Récupère la hauteur de l'écran
        self.racine.geometry(f"+{self.moniteurWidth//2-550}+{self.moniteurHeight//2-400}")  # Positionne la fenêtre au centre de l'écran

        #################################################################################################################

        ############################################# Gestion de la musique #############################################

        pygame.init()                                                                       # Initialisation de pygame                                     
        self.clickSound = pygame.mixer.Sound(path.joinpath("clickSound.wav"))               # Chargement des différents sons      
        self.clickOnMap = pygame.mixer.Sound(path.joinpath("clickOnMap.wav"))               # utilisé dans l'application
        self.fiveSecLeft = pygame.mixer.Sound(path.joinpath("5secLeft.wav"))                #
        self.timesOut = pygame.mixer.Sound(path.joinpath("timesOut.wav"))                   #
        self.clickOnMapReverse = pygame.mixer.Sound(path.joinpath("clickOnMapReverse.wav")) #
        pygame.mixer.music.load(path.joinpath('backgroundMusic.wav'))                       # Chargement de la musique de fond
        pygame.mixer.music.set_volume(0.7)                                                  # Réglage du volume de la musique
        pygame.mixer.music.play(-1)                                                         # Joue la musique en boucle

        #################################################################################################################

        ##############################################  Variables globales  #############################################

        self.getParametres()                        # Récupère les paramètres de la partie
        self.joueurActuel = 1                       # Joueur qui doit jouer
        self.nbRoundRestant = self.nbRound - 1      # Nombre de manches restantes          
        self.displayTime = True                     # Booléen qui permet d'afficher ou non le temps restant
        self.perdu = False                          # Booléen qui permet de savoir si le joueur a perdu ou non

        self.dicoVilles = {}                        # Dico des villes avec leur position et leur continent
        self.randomCapitale = ""                    # Capitale qu'il faudra trouver lors de la manche
        self.randomCapitaleList = []                # Liste des capitales qui ont déjà été utilisé lors de la partie
        self.dicoPositionsJoueurs = {}              # Dictionnaire qui enregistre les positions choisi par les joueurs lors des différentes manches 
        self.positionsPoints = []                   # Liste qui enregistre les points placés pour l'algo du PVC

        self.carte_width = 8                        # Longueur de la carte (6,8,10) en pouces
        self.carte_height = 6                       # Largeur de la carte (4,6,8) en pouces

        self.colors = ["#00B2FF","#FF4200","#46FF00","#FFD100","#FF9700","#B600FF", "#FF96BC", "#AF96FF"] # Couleur des marqueurs des différents joueurs
        
        self.fichier = 'capitales-du-monde.csv'     # Fichier csv avec toutes les villes, leurs positions et le continent associé
        
        self.creerDico()                            # Créer le dictionnaire de ville à partir du fichier csv
        self.creerWidgets()                         # Création des widgets de la fenêtre

        #################################################################################################################
        
        ############################################  Variables liés à la carte  ########################################

        self.map = ''                               # Map qui sera généré par Basemap
        self.plotSizeX = 40030154.742486            # Taille de la carte en X sur le matplotlib créer par Basemap (permet de faire les conversions de coordonnées)
        self.plotSizeY = 28339846.19933617          # Taille de la carte en Y sur le matplotlib créer par Basemap (permet de faire les conversions de coordonnées)
        self.xMapOffset = 0                         # Décalage de la postion de la carte sur le canva par rapport au bord gauche de la fenêtre en pixel
        self.maxMapSizeX = 800                      # Longueur de la carte sur le canva en pixel + décalage
        self.minMapSizeY = 0                        # Décalage de la postion de la carte sur le canva par rapport au bord haut de la fenêtre en pixel
        self.maxMapSizeY = 567                      # Largeur de la carte sur le canva en pixel + décalage

        #################################################################################################################

        # Style du combobox (liste déroulante utilisé dans le menu paramètre), purement esthétique
        self.combostyle = ttk.Style()                    
        self.combostyle.theme_create('combostyle', parent='alt', settings = {'TCombobox':{'configure':{'selectbackground': '#1F2E57','fieldbackground': '#1F2E57','background': '#1A1A2E','foreground': '#FFFFFF', 'relief' : 'flat', 'bd' : '0', 'highlightthickness' : '0'}}})
        self.combostyle.theme_use('combostyle') 

    def fermerApp(self, *event):
        """
        Ferme l'application
        :paramètres: self : la fenêtre racine
        :return:
        """
        pygame.mixer.music.stop()           # Arrête la musique de fond
        self.racine.destroy()               # Détruit la fenêtre racine

    def creerWidgets(self):
        """
        crée les widgets de l'application
        :paramètres: self : la fenêtre racine
        :return:
        """

        self.background = tk.PhotoImage(file = path.joinpath("ggearth.ppm"))                        # Image de fond de la fenêtre     
        self.imageParametre = tk.PhotoImage(file = path.joinpath("settings.ppm"))                   # Image du bouton paramètre}
        self.imageCroix = tk.PhotoImage(file = path.joinpath("quitter.ppm"))                        # Image du bouton quitter

        backgroundImage = tk.Label(self.racine, image = self.background, bd = 0)                    # Label qui contient l'image de fond
        self.boutonJouer = tk.Button(self.racine, text = "JOUER", cursor="hand2", font = "Lucida 20 bold", bd = 0, bg = '#35529F', fg= '#FFFFFF')   # Bouton jouer
        boutonParametre = tk.Button(self.racine, image = self.imageParametre, cursor="hand2", bd = 0, bg = "#1A1A2E")                               # Bouton paramètre
        boutonQuitter = tk.Button(self.racine, image = self.imageCroix, cursor="hand2", bd = 0, bg = "#1A1A2E")                                     # Bouton quitter

        self.boutonJouer.bind('<Button-1>', self.ouvrirFenGraphique)                                # Lorsque l'on clique sur le bouton jouer, on ouvre la fenêtre de jeu
        self.boutonJouer.bind('<Enter>', lambda event: self.boutonJouer.configure(bg="#4A78AE"))    # Lorsque la souris passe sur le bouton jouer, on change la couleur du bouton
        self.boutonJouer.bind('<Leave>', lambda event: self.boutonJouer.configure(bg="#35529F"))    # Lorsque la souris quitte le bouton jouer, on change la couleur du bouton
        boutonParametre.bind('<Button-1>',self.ouvrirFenParam)                                      # Lorsque l'on clique sur le bouton paramètre, on ouvre la fenêtre de paramètre
        boutonParametre.bind('<Enter>', lambda event: boutonParametre.configure(bg="#4A78AE"))      # Lorsque la souris passe sur le bouton paramètre, on change la couleur du bouton       
        boutonParametre.bind('<Leave>', lambda event: boutonParametre.configure(bg="#1A1A2E"))      # Lorsque la souris quitte le bouton paramètre, on change la couleur du bouton
        boutonQuitter.bind('<Button-1>',self.fermerApp)                                             # Lorsque l'on clique sur le bouton quitter, on ferme l'application
        boutonQuitter.bind('<Enter>', lambda event: boutonQuitter.configure(bg="#4A78AE"))          # Lorsque la souris passe sur le bouton quitter, on change la couleur du bouton
        boutonQuitter.bind('<Leave>', lambda event: boutonQuitter.configure(bg="#1A1A2E"))          # Lorsque la souris quitte le bouton quitter, on change la couleur du bouton

        if self.activerAlgoPVC.get():                                                                      # Si l'algorithme du problème du voyageur de commerce est activé

            self.boutonJouer.configure(text = "Problème du voyageur de commerce")                   # On change le texte du bouton jouer
            self.boutonJouer.bind('<Button-1>', self.ouvrirFenGraphiquePVC)                         # Lorsque l'on clique sur le bouton jouer, on ouvre la fenêtre de jeu du problème du voyageur de commerce
        # On place les différents widgets sur la fenêtre
        backgroundImage.pack()                                          
        boutonParametre.pack(side=tk.LEFT)
        boutonQuitter.pack(side=tk.RIGHT) 
        self.boutonJouer.pack(fill='x')     

        self.racine.iconbitmap(path.joinpath("icon.ico"))                   # On change l'icône de la fenêtre (à la fin pour éviter les bugs)
    
    def creerDico(self):
        """
        Crée un dictionnaire avec toutes les villes du fichier csv et initialise les distances et les scores des joueurs à 0
        :paramètres: self : la fenêtre racine
        :return:
        """
        with open(path.joinpath(self.fichier), newline = "") as csvfile:    # On ouvre le fichier csv

            reader = csv.reader(csvfile, delimiter=",")                     # On lit le fichier csv
            next(reader)                                                    # On passe la première ligne qui contient les noms des colonnes
            villes = {}                                                     # On crée un dictionnaire qui contiendra toutes les villes
            id = 1                                                          # On crée un id qui sera la clé du dictionnaire

            for ville in reader:                                            # Pour chaque ville dans le fichier csv
                    
                country = ville[0]                                          # On récupère les informations de la ville
                capital = ville[1]                                          #
                lat = float(ville[2])                                       #
                lon = float(ville[3])                                       #
                continent = ville[5]                                        #

                if country != "N/A":                                        # Si le pays n'est pas "N/A" (Not Available) afin d'éviter de devoir chercher N/A sur la carte...

                    villes[id] = {                                          # On ajoute la ville au dictionnaire
                        'country' : country,
                        'capital' : capital,
                        'lat' : float(lat),
                        'lon' : float(lon),
                        'continent' : continent
                    }

                    id+=1                                                   # On incrémente l'id       

        self.dicoVilles = villes                                            # On stocke le dictionnaire dans une variable de la classe
        self.dicoDistancesJoueurs = {}                                      # On crée un dictionnaire qui contiendra les distances des joueurs
        self.dicoScore = {}                                                 # On crée un dictionnaire qui contiendra les scores des joueurs
        
        for i in range(1, self.nbJoueur + 1):                               # Pour chaque joueur

            self.dicoDistancesJoueurs[i] = 0                                # On initialise sa distance à 0
            self.dicoScore[i] = 0                                           # On initialise son score à 0

    def fermetureFenetreParam(self, *event):
        """
        Ferme la fenêtre de paramètre
        :paramètres: self : la fenêtre racine, event : l'évènement (ici le clic sur la croix rouge de la fenêtre)
        :return:       
        """
        self.clickSound.play()                                              # On joue le son du clic
        self.racine.deiconify()                                             # On réaffiche la fenêtre principale

        if self.activerAlgoPVC.get():

            self.boutonJouer.configure(text = "Problème du voyageur de commerce")   # On change le texte du bouton jouer
            self.boutonJouer.bind('<Button-1>', self.ouvrirFenGraphiquePVC)         # Lorsque l'on clique sur le bouton jouer, on ouvre la fenêtre de jeu du problème du voyageur de commerce

        else:

            self.boutonJouer.configure(text = "JOUER")                              # On change le texte du bouton jouer
            self.boutonJouer.bind('<Button-1>', self.ouvrirFenGraphique)            # Lorsque l'on clique sur le bouton jouer, on ouvre la fenêtre de jeu


        self.f_param.destroy()                                              # On détruit la fenêtre de paramètre
        self.f_param = None                                                 # On réinitialise la variable de la classe qui contient la fenêtre de paramètre

    def getParametres(self):
        """
        Récupère les paramètres du fichier parametres.csv
        :paramètres: self : la fenêtre racine
        :return:
        """
        try :                                                       # On essaye d'ouvrir le fichier parametres.csv     

            fichier = open("parametres.csv", "r+")                  # 

        except FileNotFoundError:                                   # Si le fichier n'existe pas

            fichier = open("parametres.csv", "w+")                  # On le crée
            fichier.close()                                         # On le ferme
            fichier = open("parametres.csv", "r+")                  # On le réouvre en lecture

        parametres = fichier.read().split(";")                      # On lit le fichier et on récupère les paramètres
        fichier.close()                                             # On ferme le fichier

        if parametres == ['']:                                      # Si le fichier est vide
            
            parametres = ["2", "3", "Europe", "7", "0", "1", "0"]   # On initialise les paramètres

        try:                                                        # On essaye de convertir les paramètres en entier

            self.nbJoueur = int(parametres[0])                          # On récupère les paramètres
            self.nbRound = int(parametres[1])                           #
            self.modeDeJeu = parametres[2]                              #
            pygame.mixer.music.set_volume(float(parametres[3])/10)      #    
            self.vueSatellite = tk.IntVar(value = parametres[4])        #
            self.afficherFrontiere = tk.IntVar(value = parametres[5])   #
            self.activerAlgoPVC = tk.IntVar(value = parametres[6])             #
        
        except Exception as erreur:                                 # Si les paramètres ne sont pas des entiers
            
            print("Erreur : le fichier parametres.csv est corrompu, les paramètres ont été réinitialisés\nDétail de l'erreur : ", erreur)   # On affiche un message d'erreur
            parametres = ["2", "3", "Europe", "7", "0", "1", "0"]   # On initialise les paramètres
            fichier = open("parametres.csv", "w+")                  # On ouvre le fichier en écriture
            fichier.write(";".join(parametres))                     # On écrit les paramètres dans le fichier
            fichier.close()                                         # On ferme le fichier
            self.getParametres()                                    # On rappelle la fonction pour récupérer les paramètres

    def ouvrirFenParam(self, event):
        """
        Ouvre la fenêtre de paramètre   
        :paramètres: self : la fenêtre racine, event : l'évènement qui a déclenché la fonction (ici le clic sur le bouton paramètre)
        :return:
        """
        self.clickSound.play()                                              # On joue le son du clic

        if self.f_param == None:                                            # Si la fenêtre de paramètre n'est pas déjà ouverte

            self.racine.withdraw()                                          # On cache la fenêtre principale

            ############################## Création de la fenêtre ##############################

            self.f_param = tk.Toplevel(self.racine, bg = "#1A1A2E")                                     # On crée une fenêtre de paramètre
            self.f_param.title("Paramètre")                                                             # On lui donne un titre
            self.f_param.geometry(f"700x650+{self.moniteurWidth//2-350}+{self.moniteurHeight//2-325}")  # On définit sa taille et sa position
            self.f_param.protocol("WM_DELETE_WINDOW",self.fermetureFenetreParam)                        # On définit la fonction à appeler lorsque l'on ferme la fenêtre
            self.f_param.wait_visibility()                                                              # On attend que la fenêtre soit visible
            self.f_param.grab_set()                                                                     # On empêche l'accès aux autres fenêtres
            self.f_param.focus_force()                                                                  # On met le focus sur la fenêtre

            ####################### Définition des fonctions callback ##########################

            def setNbJoueurs(*event):   
                """
                Met à jour le nombre de joueurs en fonction de la valeur du scale
                :paramètres: event l'évènement qui a déclenché la fonction (ici le changement de valeur du scale)
                :return:
                """
                self.clickSound.play()                          # On joue le son du clic
                self.nbJoueur = nbJoueurScale.get()             # On récupère la valeur du scale     
                self.creerDico()                                # On recrée le dictionnaire des villes

            def setNbmanche(*event):   
                """
                Met à jour le nombre de manche en fonction de la valeur du scale    
                :paramètres: event l'évènement qui a déclenché la fonction (ici le changement de valeur du scale)
                :return:
                """
                self.clickSound.play()                          # On joue le son du clic
                self.nbRound = nbMancheScale.get()              # On récupère la valeur du scale
                self.nbRoundRestant = self.nbRound - 1          # On réinitialise le nombre de manche restant

            def setZoneGeo(*event): 
                """
                Met à jour la zone géographique en fonction de la valeur du combobox (liste déroulante)
                :paramètres: event l'évènement qui a déclenché la fonction (ici le changement de valeur dans le combobox)
                :return:
                """
                self.clickSound.play()                          # On joue le son du clic
                self.modeDeJeu = zoneGeoSelect.get()            # On récupère la valeur du combobox

            def setVolume(*event):
                """
                Met à jour le volume en fonction de la valeur du scale
                :paramètres: event l'évènement qui a déclenché la fonction (ici le changement de valeur du scale)
                :return:
                """
                self.clickSound.play()                          # On joue le son du clic
                newVolume = float(volumeScale.get()) / 10       # On récupère la valeur du scale et on la divise par 10 pour avoir une valeur entre 0 et 1
                pygame.mixer.music.set_volume(newVolume)        # On met à jour le volume de la musique

            def saveSettings(*event):
                """
                Sauvegarde les paramètres dans le fichier parametres.csv
                :paramètres:
                :return:"""
                fichier = open("parametres.csv", "w+")          # On ouvre le fichier parametres.csv en écriture et on le crée s'il n'existe pas et on écrit les paramètres dedans
                fichier.write("{NbJoueurs};{NbManches};{ZoneGeo};{Volume};{VueSatellite};{AfficherFrontiere};{AlgoPVC}".format(NbJoueurs = nbJoueurScale.get(), 
                                                                                                                               NbManches = nbMancheScale.get(), 
                                                                                                                               ZoneGeo = menuDeroulantZoneGeo.get(), 
                                                                                                                               Volume = volumeScale.get(), 
                                                                                                                               VueSatellite = self.vueSatellite.get(), 
                                                                                                                               AfficherFrontiere = self.afficherFrontiere.get(), 
                                                                                                                               AlgoPVC = self.activerAlgoPVC.get()))
                fichier.close()                                 # On ferme le fichier
                self.fermetureFenetreParam()                    # On ferme la fenêtre de paramètre

            def loadSettings(*event):
                """
                Charge les paramètres depuis le fichier parametres.csv
                :paramètres:
                :return:
                """
                fichier = open("parametres.csv", "r+")          # On ouvre le fichier parametres.csv en lecture et on le crée s'il n'existe pas
                parametres = fichier.read().split(";")          # On lit le fichier et on récupère les paramètres
                fichier.close()                                 # On ferme le fichier
                nbJoueurScale.set(int(parametres[0]))           # On met à jour le scale du nombre de joueurs
                nbMancheScale.set(int(parametres[1]))           # On met à jour le scale du nombre de manches
                menuDeroulantZoneGeo.set(parametres[2])         # On met à jour le combobox de la zone géographique
                volumeScale.set(int(parametres[3]))             # On met à jour le scale du volume
                pygame.mixer.music.set_volume(float(volumeScale.get())/10)  # On met à jour le volume de la musique
                self.vueSatellite.set(int(parametres[4]))       # On met à jour la variable de la vue satellite
                self.afficherFrontiere.set(int(parametres[5]))  # On met à jour la variable de l'affichage des frontières
                self.activerAlgoPVC.set(int(parametres[6]))     # On met à jour la variable de l'algorithme du PVC
                self.nbJoueur = nbJoueurScale.get()             # On récupère la valeur du scale
                self.nbRound = nbMancheScale.get()              # On récupère la valeur du scale
                self.nbRoundRestant = self.nbRound - 1          # On réinitialise le nombre de manche restant
                self.modeDeJeu = menuDeroulantZoneGeo.get()     # On récupère la valeur du combobox

                self.creerDico()                                # On recrée le dictionnaire des villes

                self.clickSound.play()                          # On joue le son du clic

            ######################## Variable utiles pour les widgets ##########################

            zonesGeo = ['Monde', 'Europe', 'Afrique', 'Asie', 'Amérique du Nord', 'Amérique du Sud', 'Amérique Centrale']   # Liste des zones géographiques disponibles
            zoneGeoSelect = tk.StringVar()                                                                                  # Variable qui contiendra la valeur du combobox

            ############################ Implémentation des widgets ############################

            titleLabel = tk.Label(self.f_param, text="Options du jeu", font="Lucida 24 bold", bg = '#0F3460', fg= '#FFFFFF', pady=20)                                                            
            nbJoueurLabel = tk.Label(self.f_param, text="Nombre de joueurs:", font="Lucida 18 bold", bg = '#1A1A2E', fg= '#FFFFFF')                                                              
            nbJoueurScale = tk.Scale(self.f_param, cursor="hand2", from_=1, to=8, orient='horizontal', font="Lucida 14 bold", bg = '#1A1A2E', fg= '#FFFFFF', relief='flat', highlightthickness=0, troughcolor='#111111', bd = 0)
            nbMancheLabel = tk.Label(self.f_param, text="Nombre de manches:", font="Lucida 18 bold", bg = '#1A1A2E', fg= '#FFFFFF')
            nbMancheScale = tk.Scale(self.f_param, cursor="hand2", from_=1, to=10, orient='horizontal', font="Lucida 14 bold", bg = '#1A1A2E', fg= '#FFFFFF', relief='flat', highlightthickness=0, troughcolor='#111111', bd = 0)
            labelZoneGeo = tk.Label(self.f_param, text="Zone géographique:", font="Lucida 18 bold", bg = '#1A1A2E', fg= '#FFFFFF')
            menuDeroulantZoneGeo = ttk.Combobox(self.f_param, cursor="hand2", textvariable = zoneGeoSelect, values = zonesGeo, state = 'readonly', font="Lucida 18 bold", justify="center")
            volumeLabel = tk.Label(self.f_param, text="Volume de la musique:", font="Lucida 18 bold", bg = '#1A1A2E', fg= '#FFFFFF')
            volumeScale = tk.Scale(self.f_param, cursor="hand2", from_=0, to=10, orient='horizontal', font="Lucida 14 bold", bg = '#1A1A2E', fg= '#FFFFFF', relief='flat', highlightthickness=0, troughcolor='#111111', bd = 0, command = setVolume)
            carteSatelliteCheckButton = tk.Checkbutton(self.f_param, cursor="hand2", text='Vue satellite', variable=self.vueSatellite, onvalue=1, offvalue=0, font="Lucida 16 bold", bg = '#1A1A2E', fg= '#FFFFFF', selectcolor="#0F3460",  bd = 0, activebackground="#262642", activeforeground="#DEDEDE", command=self.clickSound.play)
            showFrontiereCheckButton = tk.Checkbutton(self.f_param, cursor="hand2", text='Afficher frontière', variable=self.afficherFrontiere, onvalue=1, offvalue=0, font="Lucida 16 bold", bg = '#1A1A2E', fg= '#FFFFFF', selectcolor="#0F3460",  bd = 0, activebackground="#262642", activeforeground="#DEDEDE", command=self.clickSound.play)
            launchAlgoPVC = tk.Checkbutton(self.f_param, cursor="hand2", text='Lancer l\'algorithme du problème du voyageur de commerce', variable=self.activerAlgoPVC, onvalue=1, offvalue=0, font="Lucida 16 bold", bg = '#1A1A2E', fg= '#FFFFFF', selectcolor="#0F3460",  bd = 0, activebackground="#1A1A2E", activeforeground="#DEDEDE", command=self.clickSound.play)
            saveButton = tk.Button(self.f_param, cursor="hand2", text="Enregistrer", bg = '#0F3460', fg= '#FFFFFF', bd=0, height=2, font ='Lucida 16 bold')
            loadButton = tk.Button(self.f_param, cursor="hand2", text="Charger", font = 'Lucida 16 bold', height = 2, bg = '#243E82', fg= '#FFFFFF', bd=0)
            
            ############################ Mise à jour des widgets ###############################
            
            nbJoueurScale.set(self.nbJoueur)                                    # On met à jour la valeur du scale
            nbMancheScale.set(self.nbRound)                                     #
            volumeScale.set(int(round(pygame.mixer.music.get_volume(),1) * 10)) #
            zoneGeoSelect.set(self.modeDeJeu)                                   # On met à jour la valeur du combobox

            ############################## Liaison des widgets #################################

            nbJoueurScale.bind('<ButtonRelease-1>', setNbJoueurs)                           # On lie la fonction setNbJoueurs à l'évènement "relachement du clic gauche"
            nbMancheScale.bind('<ButtonRelease-1>', setNbmanche)                            # On lie la fonction setNbmanche à l'évènement "relachement du clic gauche"
            menuDeroulantZoneGeo.bind('<<ComboboxSelected>>', setZoneGeo)                   # On lie la fonction setZoneGeo à l'évènement "changement de valeur dans le combobox"
            saveButton.bind('<ButtonRelease-1>', saveSettings)                              # On lie la fonction saveSettings à l'évènement "relachement du clic gauche"
            saveButton.bind('<Enter>', lambda event: saveButton.configure(bg="#4A78AE"))    # On lie la fonction hoverSound.play à l'évènement "entrée de la souris sur le bouton"
            saveButton.bind('<Leave>', lambda event: saveButton.configure(bg="#0F3460"))    # On lie la fonction hoverSound.play à l'évènement "sortie de la souris du bouton"
            loadButton.bind('<ButtonRelease-1>', loadSettings)                              # On lie la fonction loadSettings à l'évènement "relachement du clic gauche"
            loadButton.bind('<Enter>', lambda event: loadButton.configure(bg="#4A78AE"))    # On lie la fonction hoverSound.play à l'évènement "entrée de la souris sur le bouton"
            loadButton.bind('<Leave>', lambda event: loadButton.configure(bg="#243E82"))    # On lie la fonction hoverSound.play à l'évènement "sortie de la souris du bouton"

            ############################## Placement des widgets ###############################

            titleLabel.pack(side=tk.TOP, fill='x')
            nbJoueurLabel.pack(side=tk.TOP, fill='x', padx=20, pady=(10,0))
            nbJoueurScale.pack(side=tk.TOP, fill='x', padx=20)
            nbMancheLabel.pack(side=tk.TOP, fill='x', padx=20, pady=(10,0))
            nbMancheScale.pack(side=tk.TOP, fill='x', padx=20)
            labelZoneGeo.pack(side=tk.TOP, fill='x', padx=20, pady=(10,0))
            menuDeroulantZoneGeo.pack(side=tk.TOP, fill='x', padx=20, pady=(10,0))
            volumeLabel.pack(side=tk.TOP, fill='x', padx=20, pady=(10,0))
            volumeScale.pack(side=tk.TOP, fill='x', padx=20)   
            carteSatelliteCheckButton.pack(side=tk.TOP, pady=(10,0)) 
            showFrontiereCheckButton.pack(side=tk.TOP)
            launchAlgoPVC.pack(side=tk.TOP)
            saveButton.pack(side=tk.BOTTOM, fill='x')
            loadButton.pack(side=tk.BOTTOM, fill='x')

    def fermetureFenetreGraph(self, *event):
        """
        Fonction qui permet de fermer la fenêtre graphique et de réinitialiser les variables du jeu quand on clique sur la croix rouge de la fenêtre graphique
        :paramètre: self : la fenetre racine, event : l'évènement (ici le clic sur la croix rouge de la fenêtre)
        :return: None
        """
        self.fiveSecLeft.stop()                             # Si le son du compte à rebours est en train de jouer, on l'arrête             
        self.clickSound.play()                              # On joue le son du clic
        self.displayTime = False                            # On arrête le compte à rebours
        self.randomCapitale = ""                            # On réinitialise la capitale aléatoire
        self.dicoPositionsJoueurs = {}                      # On réinitialise les positions des joueurs
        self.joueurActuel = 1                               # On réinitialise le joueur actuel
        self.randomCapitaleList = []                        # On réinitialise la liste des capitales
    
        for i in range(1, self.nbJoueur + 1):               # On réinitialise les scores et les distances des joueurs

            self.dicoDistancesJoueurs[i] = 0                #
            self.dicoScore[i] = 0                           #

        self.nbRoundRestant = self.nbRound - 1              # On réinitialise le nombre de manches restantes

        plt.close('all')                                    # On ferme toutes les plots ouverts

        for widget in self.racine.winfo_children():         # On parcourt tous les widgets de la fenêtre racine

            if isinstance(widget,tk.Toplevel):              # Si le widget est une fenêtre toplevel, on la détruit

                widget.destroy()                            #
                
        self.f_graph = None                                 # On réinitialise la fenêtre graphique
        self.racine.deiconify()                             # On réaffiche la fenêtre racine

    def fermetureFenetreGraphPVC(self, *event):
        """
        Fonction qui permet de fermer la fenêtre graphique du PVC et de réinitialiser les variables du jeu quand on clique sur la croix rouge de la fenêtre graphique du PVC
        :paramètre: self : la fenetre racine, event : l'évènement (ici le clic sur la croix rouge de la fenêtre)
        :return: None
        """ 
        self.clickSound.play()                              # On joue le son du clic

        plt.close('all')                                    # On ferme toutes les plots ouverts

        for widget in self.racine.winfo_children():         # On parcourt tous les widgets de la fenêtre racine

            if isinstance(widget,tk.Toplevel):              # Si le widget est une fenêtre toplevel, on la détruit

                widget.destroy()                            #
                
        self.f_graphPVC = None                              # On réinitialise la fenêtre graphique
        self.racine.deiconify()                             # On réaffiche la fenêtre racine

    def ouvrirFenGraphiquePVC(self, *event):
        """
        Fonction qui permet d'ouvrir la fenêtre graphique du problème du voyageur de commerce quand on clique sur le bouton "Problème du voyageur de commerce" de la fenêtre principale
        :paramètre: self : la fenetre racine, event : l'évènement (ici le clic sur le bouton "Problème du voyageur de commerce")
        :return:
        """
        if self.f_graphPVC == None:                                                    # Si la fenêtre graphique du PVC n'est pas déjà ouverte, on l'ouvre
            
            ######################################### Création de la fenêtre #########################################

            self.clickSound.play()                                                     # On joue le son du clic
            self.racine.withdraw()                                                     # On cache la fenêtre racine
            self.f_graphPVC = tk.Toplevel(self.racine, bg="#1A1A2E")                   # On crée une fenêtre toplevel qui sera la fenêtre graphique
            self.f_graphPVC.title("GeoQuiz (PVC)")                                     # On donne un titre à la fenêtre graphique
            self.f_graphPVC.geometry(f"+{self.moniteurWidth//2-400*self.carte_width//8}+{self.moniteurHeight//2-350*self.carte_height//6}")    # On place la fenêtre graphique au centre de l'écran
            self.f_graphPVC.resizable(width=False, height=False)                       # On empêche le redimensionnement de la fenêtre graphique
            self.f_graphPVC.protocol("WM_DELETE_WINDOW",self.fermetureFenetreGraphPVC) # On associe la fonction fermetureFenetreGraph à la croix rouge de la fenêtre graphique
            self.f_graphPVC.wait_visibility()                                          # On attend que la fenêtre soit visible
            self.f_graphPVC.grab_set()                                                 # On empêche l'accès aux autres fenêtres
            self.f_graphPVC.focus_force()                                              # On met le focus sur la fenêtre

            ###################################### Implémentation des widgets ########################################

            self.buttonFrame = tk.Frame(self.f_graphPVC, bg="#1A1A2E")                 # Frame qui contiendra les boutons
            self.validateButton = tk.Button(self.buttonFrame, cursor="arrow", state="disabled", width = 13, text="Valider", bg = '#0F3460', fg= '#FFFFFF', bd=0, height=2, font ='Lucida 16 bold')
            self.undoButton = tk.Button(self.buttonFrame, cursor="arrow", state="disabled", width = 13, text="Annuler", bg = '#0F3460', fg= '#FFFFFF', bd=0, height=2, font ='Lucida 16 bold')
            self.consigneLabel = tk.Label(self.buttonFrame, text="   Cliquez sur la carte pour placer un marqueur   ", bg="#16213E", fg="#FFFFFF", font="Lucida 16 bold")

            ######################################## Placement des widgets ###########################################

            self.dessineCarte()  
            self.f_graphPVC.canevas.bind("<Button-1>",self.ajouterMarqueurPVC)          # On associe la fonction ajouterMarqueurPVC() au clic gauche sur la carte
            self.f_graphPVC.canevas.pack(side=tk.TOP)                                   # Créer un canva et place la carte crée par Basemap dessus)
            self.buttonFrame.grid(column=0, row=1, sticky="nsew")                       # Place la frame des boutons en dessous de la carte
            self.undoButton.grid(column=0, row=0, sticky="nsew")                        # Place le bouton "Annuler" en dessous de la carte
            self.consigneLabel.grid(column=1, row=0, sticky="nsew")                     # Place le bouton "Enlever dernier marqueur" en dessous de la carte
            self.validateButton.grid(column=2, row=0, sticky="nsew")                    # Place le bouton "Valider" en dessous de la carte            
            self.positionsPoints = []                                                   # On réinitialise la liste des positions des points
            self.f_graphPVC.iconbitmap(path.joinpath("icon.ico"))                       # On change l'icône de la fenêtre graphique (à la fin pour éviter les bugs)

    def ouvrirFenGraphique(self, event):
        """
        Fonction qui permet d'ouvrir la fenêtre graphique quand on clique sur le bouton "Jouer" de la fenêtre principale 
        :paramètre: self : la fenetre racine, event : l'évènement (ici le clic sur le bouton "Jouer")
        :return:
        """
        if self.f_graph == None:                                    # Si la fenêtre graphique n'est pas déjà ouverte, on l'ouvre

            self.choisirCapitale()                                  # Choisis aléatoirment une capitale

            ######################################### Création de la fenêtre #########################################

            self.clickSound.play()                                                  # On joue le son du clic
            self.racine.withdraw()                                                  # On cache la fenêtre racine
            self.f_graph = tk.Toplevel(self.racine, bg="#1A1A2E")                   # On crée une fenêtre toplevel qui sera la fenêtre graphique
            self.f_graph.title("GeoQuiz")                                           # On donne un titre à la fenêtre graphique
            self.f_graph.geometry(f"+{self.moniteurWidth//2-500*self.carte_width//8}+{self.moniteurHeight//2-350*self.carte_height//6}")    # On place la fenêtre graphique au centre de l'écran
            self.f_graph.resizable(width=False, height=False)                       # On empêche le redimensionnement de la fenêtre graphique
            self.f_graph.protocol("WM_DELETE_WINDOW",self.fermetureFenetreGraph)    # On associe la fonction fermetureFenetreGraph à la croix rouge de la fenêtre graphique
            self.f_graph.wait_visibility()                                          # On attend que la fenêtre soit visible
            self.f_graph.grab_set()                                                 # On empêche l'accès aux autres fenêtres
            self.f_graph.focus_force()                                              # On met le focus sur la fenêtre

            ###################################### Implémentation des widgets ########################################

            self.f_graph.mapFrame = tk.Frame(self.f_graph)          # On crée un frame qui contiendra la carte  
            self.f_graph.scoreFrame = tk.Frame(self.f_graph)        # On crée un frame qui contiendra les scores
            
            self.capitaleLabel = tk.Label(self.f_graph.mapFrame, text = self.randomCapitale['capital'], font='Lucida 15 bold', bg = '#35529F', fg= '#FFFFFF', height="2")
            self.validateButton = tk.Button(self.f_graph.mapFrame, cursor="arrow", state="disabled", text="Valider", bg = '#0F3460', fg= '#FFFFFF', activebackground = "#4A78AE", activeforeground = "#FFFFFF", bd=0, height=2, font ='Lucida 16 bold')
            self.labelTemps = tk.Label(self.f_graph.scoreFrame, text = 'Temps:', font = 'Lucida 16 bold', width=20, height = 2, bg = '#243E82', fg= '#FFFFFF', anchor= tk.CENTER)
            self.labelRoundActuel = tk.Label(self.f_graph.scoreFrame, text = f"Manche {self.nbRound - self.nbRoundRestant} / {self.nbRound}", font = 'Lucida 16 bold', bg = '#35529F', fg= '#FFFFFF', width=20, anchor= tk.N)
            self.labelJoueurActuel = tk.Label(self.f_graph.scoreFrame, text = f"Tour du Joueur {self.joueurActuel}", font = 'Lucida 16 bold', bg = '#262642', fg= '#FFFFFF', width=20, anchor= tk.N)
            self.score = tk.Label(self.f_graph.scoreFrame, text = 'Score:', font = 'Lucida 16 bold', bg = '#35529F', fg= '#FFFFFF', width=20, anchor= tk.CENTER)
            self.labelJoueur = tk.Label(self.f_graph.scoreFrame, text = self.afficherJoueurEtScore(), font = 'Lucida 14 bold', bg = '#262642', fg= '#FFFFFF', width=20, anchor= tk.N)

            ######################################### Liaison des widgets ############################################

            self.validateButton.bind("<Button-1>",self.afficherTourJoueurSuivant)   # On associe la fonction afficherTourJoueurSuivant() au clic gauche sur le bouton "Valider"
            self.f_graph.bind("<Return>",self.afficherTourJoueurSuivant)            # On associe la fonction afficherTourJoueurSuivant() à la touche "Entrée"

            ######################################## Placement des widgets ###########################################

            self.f_graph.mapFrame.pack(side=tk.LEFT)                    # On place le frame de la carte à gauche
            self.f_graph.scoreFrame.pack(side=tk.RIGHT, fill = 'y')     # On place le frame des scores à droite
            self.dessineCarte()                                         
            self.f_graph.canevas.bind("<Button-1>",self.ajouterMarqueur)                    # On associe la fonction ajouterMarqueur() au clic gauche sur la carte
            self.f_graph.canevas.pack(side=tk.TOP)                                          # Créer un canva et place la carte crée par Basemap dessus)
            self.capitaleLabel.grid(column=0,row=1, sticky="nsew")
            self.validateButton.grid(column=0,row=2, sticky="nsew")
            self.labelTemps.pack(side=tk.TOP, fill='x')
            self.labelRoundActuel.pack(side=tk.TOP, fill='x')
            self.labelJoueurActuel.pack(side=tk.TOP, fill='x')
            self.score.pack(side=tk.TOP, fill='x')
            self.labelJoueur.pack(side=tk.TOP, expand=True, fill='both')
            
            self.f_graph.iconbitmap(path.joinpath("icon.ico"))          # On change l'icône de la fenêtre graphique (à la fin pour éviter les bugs)

            if self.nbJoueur == 1:                                      # Si le mode de jeu est solo, on lance le timer
                
                self.validateButton.bind("<Button-1>",self.afficherResultatManche)
                self.labelTemps.configure(text = f"Temps: infini")

            else:                                                    

                self.afficherTourJoueurUn()                             # On affiche que c'est au tour du joueur 1

    def dessineCarte(self):
        """
        Dessine la carte sur un canva
        :paramètre: self : la fenetre racine
        :return:
        """
        # Selon le mode de jeu sélectionné, il faut mettre à jour les dimensions de la carte
        if self.modeDeJeu == "Monde":                   

            self.distance_max = 2000                                                                                            # Distance max entre la capitale et le point cliqué permettant de gagner des points
            self.map = Basemap(llcrnrlon=-180, llcrnrlat=-60, urcrnrlon=180, urcrnrlat=85, resolution='c', projection='merc')   # On crée la carte avec les coordonnées de la zone à afficher
            self.plotSizeX = 40030154.742486                                                                                    # On récupère la taille de la carte sur le matplotlib créer par Basemap (sert à convertir les coordonnées en pixels sur le canva)
            self.plotSizeY = 28339846.19933617                                                                                  #
            self.xMapOffset = 0                                                                                                 # On récupère le décalage de la carte par rapport à la fenêtre graphique en x
            self.maxMapSizeX = 800                                                                                              # On récupère la taille de la carte en pixels sur x
            self.minMapSizeY = 0                                                                                                # On récupère le décalage de la carte par rapport à la fenêtre graphique en x
            self.maxMapSizeY = 567                                                                                              # On récupère la taille de la carte en pixels sur y                                                

        elif self.modeDeJeu == "Europe":
            
            self.distance_max = 750
            self.map = Basemap(llcrnrlon=-25, llcrnrlat=30, urcrnrlon=45, urcrnrlat=70, resolution='l', projection='merc')
            self.plotSizeX = 7783641.199927683
            self.plotSizeY = 7556696.997484207
            self.xMapOffset = 108
            self.maxMapSizeX = 693
            self.minMapSizeY = 0
            self.maxMapSizeY = 567

        elif self.modeDeJeu == "Asie":

            self.distance_max = 2000
            self.map = Basemap(llcrnrlon=25, llcrnrlat=-10, urcrnrlon=180, urcrnrlat=75, resolution='l', projection='merc')
            self.plotSizeX = 17235205.51412558
            self.plotSizeY = 14035403.557954626
            self.xMapOffset = 52
            self.maxMapSizeX = 748
            self.minMapSizeY = 0
            self.maxMapSizeY = 567
            
        elif self.modeDeJeu == "Afrique":

            self.distance_max = 2000
            self.map = Basemap(llcrnrlon=-25, llcrnrlat=-40, urcrnrlon=60, urcrnrlat=40, resolution='l', projection='merc')
            self.plotSizeX = 9451564.3141979
            self.plotSizeY = 9720990.20917484
            self.xMapOffset = 124
            self.maxMapSizeX = 676
            self.minMapSizeY = 0
            self.maxMapSizeY = 567

        elif self.modeDeJeu == "Amérique du Nord":

            self.distance_max = 2000
            self.map = Basemap(llcrnrlon=-180, llcrnrlat=5, urcrnrlon=-30, urcrnrlat=80, resolution='l', projection='merc')
            self.plotSizeX = 16679231.142702177
            self.plotSizeY = 14964634.917103881
            self.xMapOffset = 84
            self.maxMapSizeX = 716
            self.minMapSizeY = 0
            self.maxMapSizeY = 567

        elif self.modeDeJeu == "Amérique du Sud":

            self.distance_max = 2000
            self.map = Basemap(llcrnrlon=-90, llcrnrlat=-60, urcrnrlon=-30, urcrnrlat=20, resolution='l', projection='merc')
            self.plotSizeX = 6671692.457080871
            self.plotSizeY = 10660821.194898266
            self.xMapOffset = 223
            self.maxMapSizeX = 577
            self.minMapSizeY = 0
            self.maxMapSizeY = 567

        elif self.modeDeJeu == "Amérique Centrale":

            self.distance_max = 1000
            self.map = Basemap(llcrnrlon=-120, llcrnrlat=0, urcrnrlon=-60, urcrnrlat=30, resolution='l', projection='merc')
            self.plotSizeX = 6671692.457080871
            self.plotSizeY = 3499627.79763383
            self.xMapOffset = 0
            self.maxMapSizeX = 800
            self.minMapSizeY = 74
            self.maxMapSizeY = 493
    
        self.map.drawcoastlines()                       # On dessine les côtes
        
        if self.afficherFrontiere.get():                # On dessine les frontières si l'option est activée

            self.map.drawcountries()                    # On dessine les frontières

        if self.vueSatellite.get():                     # On dessine la carte satellite si l'option est activée

            self.map.bluemarble()                       # On dessine la carte satellite

            if self.afficherFrontiere.get():

                self.map.drawcountries(color="#ffffff", linewidth=0.5)     # On dessine les frontières (en blanc pour qu'elles soient visibles sur la carte satellite)

        else:

            self.map.drawmapboundary(fill_color='#0056B1')                              # On dessine la mer  
            self.map.fillcontinents(color='#A58200', lake_color='#0056B1')              # On dessine les continents                                

        fig = plt.gcf()                                                                 # On récupère la figure 
        fig.set_size_inches(self.carte_width, self.carte_height)                        # On définit la taille de la figure
        fig.patch.set_facecolor('#1A1A2E')                                              # On définit la couleur de fond de la figure
        plt.tight_layout()                                                              # On supprime les marges de la figure
        plt.subplots_adjust(left=0, bottom=0.055, right=1, top=1, wspace=0, hspace=0)   # 

        if self.activerAlgoPVC.get():                                                          # Si l'option PVC est activée, on affiche la carte dans la fenêtre du PVC

            fenetre = self.f_graphPVC                                                   # On récupère la fenêtre du PVC
            fenetre.canevas = tk.Canvas(fenetre)                                        

        else:                                                                           # Sinon, on affiche la carte dans la fenêtre principale
            
            fenetre = self.f_graph                                                      # On récupère la fenêtre principale
            fenetre.canevas = tk.Canvas(fenetre.mapFrame)                               

        fenetre.canevas.grid(column=0,row=0)                                       
        fenetre.canevas = FigureCanvasTkAgg(fig, master=fenetre.canevas)      # On crée un canvas pour afficher la figure
        fenetre.canevas.draw()                                                # On affiche la figure dans le canvas
        fenetre.canevas = fenetre.canevas.get_tk_widget()                     # On récupère le canvas de la figure                                  

    def getPositionMarqeurOnMap(self, xCanva, yCanva):
        """
        Fonction qui retourne la position du marqueur sur la carte
        :param xCanva: int : position en x du marqueur sur le canvas
        :param yCanva: int : position en y du marqueur sur le canvas
        :return: tuple : position du marqueur sur la carte matplotlib créée par Basemap
        """
        xMap = ((xCanva - self.xMapOffset) * self.plotSizeX * 8) / (self.carte_width * (self.maxMapSizeX - self.xMapOffset))    # On calcule la position du marqueur sur la carte du matplotlib
        yMap = ((self.maxMapSizeY - yCanva) * self.plotSizeY * 6) / (self.carte_height * (self.maxMapSizeY - self.minMapSizeY)) #  
        return xMap, yMap
    
    def ajouterMarqueur(self, event):
        """
        Fonction qui ajoute un marqueur sur la carte du matplotlib à l'endroit du clic (à chaque fois qu'un nouveau marqueur est placé, on enlève le précédent)
        :param event: self : la fenetre racine, event : évènement du clic gauche sur la carte 
        :return: None
        """
        self.validateButton.config(bg='#224F84', cursor="hand2", state="normal")    # On change la couleur du bouton de validation
        self.validateButton.bind("<Enter>", lambda event: self.validateButton.config(bg='#4A78AE'))
        self.validateButton.bind("<Leave>", lambda event: self.validateButton.config(bg='#224F84'))
        self.clickOnMap.play()                                                  # On joue le son du clic sur la carte
        xCanva, yCanva = event.x, event.y                                       # On récupère les coordonnées du clic
        self.reinitialiserMap()                                                 # On réinitialise la carte
        self.f_graph.canevas.create_oval(xCanva - 2, yCanva - 2, xCanva + 2, yCanva + 2, fill = self.colors[self.joueurActuel - 1]) # On crée un marqueur à l'endroit du clic                                     # On crée un marqueur à l'endroit du clic
        xMap, yMap = self.getPositionMarqeurOnMap(xCanva, yCanva)                                                   # On récupère la position du marqueur sur la carte du matplotlib
        self.dicoPositionsJoueurs[self.joueurActuel] = ([xMap,xCanva],[yMap,yCanva])                                # On enregistre la position du marqueur dans le dictionnaire des positions des joueurs

    def undoMarqueur(self, *event):
        """
        Fonction qui supprime le dernier marqueur placé sur la carte du matplotlib
        :param event: self : la fenetre racine, event : évènement du clic gauche sur la carte
        :return: None
        """
        self.clickOnMapReverse.play()                                                              # On joue le son du clic sur la carte

        if len(self.f_graphPVC.canevas.find_all()) > 2:                                            # Si il y a au moins deux marqueurs sur la carte, on supprime le dernier                   
            
            self.f_graphPVC.canevas.delete(self.f_graphPVC.canevas.find_all()[-1])                 # On supprime le dernier marqueur placé sur la carte
            self.positionsPoints.pop(-1)                                                           # On supprime la dernière position enregistrée dans la liste des positions

            if len(self.f_graphPVC.canevas.find_all()) <= 2:                                       # Si il n'y a plus qu'un marqueur sur la carte, on désactive le bouton undo

                self.undoButton.config(bg='#0F3460', cursor="arrow", state="disabled")             # On change la couleur du bouton undo
                self.undoButton.unbind("<Button-1>")
                self.undoButton.unbind("<Enter>")
                self.undoButton.unbind("<Leave>")

        if len(self.f_graphPVC.canevas.find_all()) <= 4:                                           # Si il y a moins de 3 marqueurs sur la carte, on désactive le bouton de validation
            
            self.validateButton.config(bg='#0F3460', cursor="arrow", state="disabled")             # On change la couleur du bouton de validation
            self.validateButton.unbind("<Enter>")
            self.validateButton.unbind("<Leave>")
            self.validateButton.unbind("<Button-1>")
            self.f_graphPVC.unbind("<Return>")
        
    def ajouterMarqueurPVC(self, event):
        """
        Fonction qui ajoute un marqueur sur la carte du matplotlib à l'endroit du clic
        :param event: self : la fenetre racine, event : évènement du clic gauche sur la carte 
        :return: None
        """
        self.clickOnMap.play()                                                                                                  # On joue le son du clic sur la carte
        self.undoButton.config(bg='#224F84', cursor="hand2", state="normal")                                            
        self.undoButton.bind("<Enter>", lambda event: self.undoButton.config(bg='#4A78AE'))
        self.undoButton.bind("<Leave>", lambda event: self.undoButton.config(bg='#224F84'))
        self.undoButton.bind("<Button-1>",self.undoMarqueur)
        xCanva, yCanva = event.x, event.y                                                                                               # On récupère les coordonnées du clic                                                                                               # On récupère les coordonnées du clic
        self.f_graphPVC.canevas.create_oval(xCanva - 2, yCanva - 2, xCanva + 2, yCanva + 2, fill = 'red')                       # On crée un marqueur à l'endroit du clic                                     # On crée un marqueur à l'endroit du clic
        xMap, yMap = self.getPositionMarqeurOnMap(xCanva, yCanva)                                                               # On récupère la position du marqueur sur la carte du matplotlib
        lon, lat = self.map(xMap, yMap, inverse=True)                                                                           # On récupère la longitude et la latitude du marqueur
        self.positionsPoints.append([[xMap,xCanva,lon],[yMap,yCanva,lat]])                                                      # On enregistre la position du marqueur dans la liste des points

        if len(self.f_graphPVC.canevas.find_all()) > 4:                                                                         # Si il y a au moins trois marqueurs sur la carte, on active le bouton de validation
            
            self.validateButton.config(bg='#224F84', cursor="hand2", state="normal")
            self.validateButton.bind("<Enter>", lambda event: self.validateButton.config(bg='#4A78AE'))
            self.validateButton.bind("<Leave>", lambda event: self.validateButton.config(bg='#224F84'))
            self.validateButton.bind("<Button-1>",self.algoPVC)
            self.f_graphPVC.bind("<Return>",self.algoPVC)
    
    def buildGraph(self):
        """
        Fonction qui construit le graphe du problème du voyageur de commerce sous la forme d'un dictionnaire (clé : numéro du point, valeur : dictionnaire des distances entre le point et les autres points))
        :param: self : la fenetre racine
        :return: graph : le graphe du problème du voyageur de commerce sous la forme d'un dictionnaire
        """
        graph = {}                                                                 # On initialise le dictionnaire du graphe

        for i in range(len(self.positionsPoints)):                                 # On parcourt la liste des points

            graph[i] = {}                                                          # On initialise le dictionnaire des distances entre le point i et les autres points

            for j in range(len(self.positionsPoints)):                             # On parcourt la liste des points

                if i != j:                                                         # Si le point i est différent du point j

                    graph[i][j] = self.distanceKm(self.positionsPoints[i][1][2], self.positionsPoints[i][0][2],self.positionsPoints[j][1][2], self.positionsPoints[j][0][2])   # On calcule la distance entre le point i et le point j et on l'ajoute au dictionnaire des distances
  
        return graph                                                               # On retourne le dictionnaire du graphe

    def algoPVC(self, *event):
        """
        Fonction qui lance l'algorithme du problème du voyageur de commerce (approche par force brute qui génère toutes les permutations possibles des villes et calcule la distance totale pour chaque permutation)
        :param: self : la fenetre racine, event : évènement du clic sur le bouton "Valider"
        :return: None
        Remarque : Si il y a beaucoup de points, l'algorithme peut prendre beaucoup de temps à s'exécuter (complexité en O(n!)). 
                   A titre d'exemple, pour 10 points, il y a 10! = 3628800 permutations possibles. Au delà de 10 points, l'algorithme devient très lent.
                   Afin d'améliorer cela, on peut utiliser des algorithmes d'optimisation plus avancés tels que des algorithmes de recherche locale ou des algorithmes génétiques (population -> sélection -> croisement -> mutation -> nouvelle population -> etc...)
        """
        self.clickSound.play()                                                      # On joue le son du clic

        graph = self.buildGraph()                                                   # On construit le graphe du problème du voyageur de commerce
        listeNoeud = list(graph.keys())                                             # On récupère la liste des noeuds du graphe                                         
        self.meilleurChemin = None                                                  # On initialise le meilleur chemin                      
        self.distanceMinimale = float('inf')                                        # On initialise la distance minimale à l'infini
        
        permutations = self.permuter(listeNoeud)                                    # On génère toutes les permutations possibles des noeuds du graphe

        for permutation in permutations:                                            # On parcourt toutes les permutations possibles

            distanceTotale = 0                                                      # On initialise la distance totale à 0
            
            for i in range(len(permutation) - 1):                                   # On parcourt la permutation

                villeDepart = permutation[i]                                        # On récupère la ville de départ
                villeArrivee = permutation[i+1]                                     # On récupère la ville d'arrivée
                distance = graph[villeDepart][villeArrivee]                         # On récupère la distance entre la ville de départ et la ville d'arrivée
                distanceTotale += distance                                          # On ajoute la distance à la distance totale 

            if distanceTotale < self.distanceMinimale:                              # Si la distance totale est inférieure à la distance minimale

                self.distanceMinimale = distanceTotale                              # On met à jour la distance minimale
                self.meilleurChemin = permutation                                   # On met à jour le meilleur chemin
        
        self.afficherTrajetMinimal()                                                # On affiche le trajet minimal

    def permuter(self, listeNoeud):
        """
        Fonction qui génère toutes les permutations possibles d'une liste
        :param: self : la fenetre racine, listeNoeud : la liste à permuter
        :return: la liste des permutations
        """
        if len(listeNoeud) == 0:                                                                         # Si la liste est vide, on retourne une liste vide

            return []
        
        if len(listeNoeud) == 1:                                                                         # Si la liste ne contient qu'un élément, on retourne la liste

            return [listeNoeud]
        
        else:                                                                                            # Sinon, on parcourt la liste et on génère les permutations possibles
            
            permutationList = []                                                                         # On initialise la liste des permutations
            
            for i in range(len(listeNoeud)):                                                             # On parcourt la liste

                noeudCourant = listeNoeud[i]                                                             # On récupère l'élément courant
                reste = listeNoeud[:i] + listeNoeud[i+1:]                                                # On récupère le reste de la liste

                for permutationsRestantes in self.permuter(reste):                                       # On génère les permutations possibles du reste de la liste

                    permutationList.append([noeudCourant] + permutationsRestantes)                       # On ajoute l'élément courant à la permutation et on l'ajoute à la liste des permutations

            return permutationList                                                                       # On retourne la liste des permutations

    def afficherTrajetMinimal(self, *event):
        """
        Fonction qui affiche le trajet minimal calculé par l'algorithme du problème du voyageur de commerce
        :param: self : la fenetre racine, event : évènement du clic sur le bouton "Valider"
        :return: None
        """
        for i in range(len(self.meilleurChemin) - 1):                                                   # On parcourt le meilleur chemin et on affiche les lignes entre les points                                 
            
            self.f_graphPVC.canevas.create_line(self.positionsPoints[self.meilleurChemin[i]][0][1], self.positionsPoints[self.meilleurChemin[i]][1][1], self.positionsPoints[self.meilleurChemin[i + 1]][0][1], self.positionsPoints[self.meilleurChemin[i + 1]][1][1], fill = '#ff0000', width = 2)

        self.validateButton.config(text="Recommencer", bg="#224F84", fg="white")                        # On change le texte du bouton "Valider" et on change sa commande
        self.validateButton.unbind("<Button-1>")                                                        # On supprime l'évènement du clic sur le bouton "Valider"
        self.f_graphPVC.unbind("<Return>")                                                              # On supprime l'évènement de la touche "Entrée"
        self.f_graphPVC.canevas.unbind("<Button-1>")                                                    # On supprime l'évènement du clic sur le canevas
        self.undoButton.unbind("<Enter>")                                                               # On supprime l'évènement du survol du bouton "Annuler"
        self.undoButton.unbind("<Leave>")                                                               # On supprime l'évènement de la fin du survol du bouton "Annuler"                                     
        self.undoButton.unbind("<Button-1>")                                                            # On supprime l'évènement du clic sur le bouton "Annuler"
        self.undoButton.config(bg = "#0F3460", cursor="arrow", state="disabled")                                          # On désactive le bouton "Annuler"
        self.validateButton.bind("<Button-1>", self.recommencerPVC)                                     # On ajoute l'évènement du clic sur le bouton "Recommencer"
        self.f_graphPVC.bind("<Return>", self.recommencerPVC)                                           # On ajoute l'évènement de la touche "Entrée"
        self.validateButton.bind("<Enter>", lambda event : self.validateButton.config(bg = "#4A78AE"))  # On associe le survol du bouton à la fonction lambda
        self.validateButton.bind("<Leave>", lambda event : self.validateButton.config(bg = "#224F84"))  #

    def recommencerPVC(self, *event):
        """
        Fonction qui réinitialise l'affichage du problème du voyageur de commerce
        :param: self : la fenetre racine, event : évènement du clic sur le bouton "Recommencer"
        :return: None
        """          
        self.clickSound.play()                                                      # On joue le son du clic

        while len(self.f_graphPVC.canevas.find_all()) != 2:                         # On supprime les marqueurs de points et les lignes du canevas
                
            self.f_graphPVC.canevas.delete(self.f_graphPVC.canevas.find_all()[-1])
                
        self.validateButton.config(text="Valider", bg = '#0F3460', fg= '#FFFFFF', cursor="arrow", state="disabled")
        self.validateButton.unbind("<Button-1>")                                    # On supprime l'évènement du clic sur le bouton "Recommencer"
        self.f_graphPVC.unbind("<Return>")                                          # On supprime l'évènement de la touche "Entrée"
        self.validateButton.unbind("<Enter>")                                       # On supprime l'évènement du survol du bouton      
        self.validateButton.unbind("<Leave>")                                       #   
        self.f_graphPVC.canevas.bind("<Button-1>",self.ajouterMarqueurPVC)          # On réassocie la fonction ajouterMarqueurPVC() au clic gauche sur la carte
        self.positionsPoints = []                                                   # On réinitialise la liste des positions des points

    def choisirCapitale(self):
        """
        Fonction qui choisit une capitale aléatoirement dans le dictionnaire des capitales
        :param: self : la fenetre racine
        :return: None
        """
        randomId = random.randint(1,len(self.dicoVilles))                                               # On choisit un id aléatoire dans le dictionnaire des capitales

        continent = self.modeDeJeu                                                                      # On récupère le nom du continent sélectionné

        if self.modeDeJeu == "Asie":                                                                    # On convertit les nom des continents en anglais pour le dictionnaire des capitales

            continent = "Asia"

        elif self.modeDeJeu == "Afrique":

            continent = "Africa"

        elif self.modeDeJeu == "Amérique du Nord":

            continent = "North America"
        
        elif self.modeDeJeu == "Amérique du Sud":

            continent = "South America"

        elif self.modeDeJeu == "Amérique Centrale":

            continent = "Central America"

        while self.dicoVilles[randomId]["continent"] != continent and self.modeDeJeu != "Monde" or self.dicoVilles[randomId]['capital'] in self.randomCapitaleList:   # Tant que la capitale ne se trouve pas dans le continent sélectionné ou qu'elle à déjà été sélectionnée, on en choisit une autre

            randomId = random.randint(1,len(self.dicoVilles))                                           # On choisit un id aléatoire dans le dictionnaire des capitales

        self.randomCapitale = self.dicoVilles[randomId]                                                 # On enregistre la capitale choisie
        self.randomCapitaleList.append(self.randomCapitale['capital'])                                  # On enregistre la capitale choisie dans la liste des capitales choisies

    def afficherPositionCapitale(self):
        """
        Fonction qui affiche la position de la capitale sur la carte du matplotlib
        :param: self : la fenetre racine
        :return: None
        """
        xmap, ymap = self.map(self.randomCapitale["lon"], self.randomCapitale["lat"])                                                   # On récupère les coordonnées de la capitale sur la carte du matplotlib
        self.map.plot(xmap, ymap, 'ro', markersize=5)                                                                                   # On affiche la capitale sur la carte du matplotlib
        xCanvaCapital = ((self.maxMapSizeX - self.xMapOffset)*xmap/self.plotSizeX + self.xMapOffset) * self.carte_width/8               # On calcule la position de la capitale sur la carte du canvas
        yCanvaCapital = (self.maxMapSizeY - (self.maxMapSizeY - self.minMapSizeY)*ymap/self.plotSizeY) * self.carte_height/6            #
        self.f_graph.canevas.create_oval(xCanvaCapital - 5, yCanvaCapital - 5, xCanvaCapital + 5, yCanvaCapital + 5, fill = "#E94560")  # On affiche la capitale sur la carte du canvas
        self.afficherPositionJoueurs(xCanvaCapital, yCanvaCapital)                                                                      # On affiche la position des marqueurs de tous les joueurs sur la carte du canvas

    def afficherPositionJoueurs(self, xCanvaCapital, yCanvaCapital):
        """
        Fonction qui affiche la position des marqueurs de tous les joueurs sur la carte du canvas par rapport à la capitale 
        :param: self : la fenetre racine, xCanvaCapital : la position de la capitale sur la carte du canvas, yCanvaCapital : la position de la capitale sur la carte du canvas
        :return: None
        """
        for joueur in self.dicoPositionsJoueurs:                                                                            # On parcourt le dictionnaire des positions des joueurs

            x = self.dicoPositionsJoueurs[joueur][0][1]                                                                     # On récupère les coordonnées du marqueur du joueur
            y = self.dicoPositionsJoueurs[joueur][1][1]                                                                     #                                    
            xMap = self.dicoPositionsJoueurs[joueur][0][0]                                                                  # On récupère les coordonnées du marqueur du joueur sur la carte du matplotlib
            yMap = self.dicoPositionsJoueurs[joueur][1][0]                                                                  #                                         
            self.f_graph.canevas.create_oval(x - 2, y - 2, x + 2, y + 2, fill = self.colors[joueur - 1])                    # On affiche le marqueur du joueur sur la carte du canvas
            self.f_graph.canevas.create_line(x, y, xCanvaCapital, yCanvaCapital, fill = self.colors[joueur - 1], width=1)   # On affiche la ligne entre le marqueur du joueur et la capitale sur la carte du canvas
            self.calculerDistance(joueur, xMap, yMap)                                                                       # On calcule la distance entre le marqueur du joueur et la capitale

    def calculerDistance(self, joueur, xMap, yMap):
        """
        Fonction qui calcule la distance entre le marqueur du joueur et la capitale
        :param: self : la fenetre racine, joueur : le joueur actuel, xMap : la position du marqueur du joueur sur la carte du matplotlib, yMap : la position du marqueur du joueur sur la carte du matplotlib
        :return: None
        """
        lon, lat = self.map(xMap, yMap, inverse=True)                                                                   # On récupère les coordonnées du marqueur du joueur sur la carte du matplotlib
        lonCapital,latCapital = self.randomCapitale["lon"], self.randomCapitale["lat"]                                  # On récupère les coordonnées longitude et latitude de la capitale
        distance = self.distanceKm(lat, lon, latCapital, lonCapital)                                                    # On calcule la distance entre le marqueur du joueur et la capitale
        self.dicoDistancesJoueurs[joueur] += distance                                                                   # On enregistre la distance dans le dictionnaire des distances des joueurs

        if distance <= self.distance_max:                                                                               # Si la distance est inférieure à la distance maximale admissible pour avoir des points

            self.dicoScore[joueur] += self.distance_max - int(distance)                                                 # On ajoute des points au joueur en fonction de la distance (plus la distance est petite, plus le joueur a de points)

    def lancerManche(self, *event):
        """
        Fonction qui lance une manche
        :param: self : la fenetre racine
        :return: None
        """
        self.clickSound.play()
        self.f_joueurSuivant.destroy()    
        self.f_graph.deiconify()
        self.displayTime = True                                                                     # On affiche le temps
        self.ref = time.time()                                                                      # On enregistre le temps actuel
        self.afficherTemps()                                                                        # On affiche le temps

    def afficherTourJoueurUn(self, *event):                                         
        """
        Affiche que c'est au tour du joueur 1
        :param: self : la fenetre racine, event : l'évènement (clic sur le bouton)
        :return: None
        """
        self.clickSound.play()                                                                              # On joue le son du clic
        self.displayTime = False                                                                            # On arrête d'afficher le temps
        self.f_graph.withdraw()                                                                             # On cache la fenetre du graphique
        self.f_joueurSuivant = tk.Toplevel(self.racine, bg="#1A1A2E")                                       # On crée une fenetre qui indique que c'est au tour du joueur 1
        self.f_joueurSuivant.title(f"Tour du joueur {self.joueurActuel}")                                   # On change le titre de la fenetre           
        self.f_joueurSuivant.resizable(width=False, height=False)                                           # On empêche le redimensionnement de la fenetre
        self.f_joueurSuivant.geometry(f"500x500+{self.moniteurWidth//2-250}+{self.moniteurHeight//2-250}")  # On définit la taille et la position de la fenetre
        self.f_joueurSuivant.protocol("WM_DELETE_WINDOW",self.fermetureFenetreGraph)                        # On lie la fermeture de la fenetre à la fonction fermetureFenetreGraph
        self.f_joueurSuivant.wait_visibility()                                                              # On attend que la fenetre soit visible
        self.f_joueurSuivant.grab_set()                                                                     # On empêche l'accès à la fenetre principale
        self.f_joueurSuivant.focus_force()                                                                  # On met le focus sur la fenetre
        ### On crée les widgets ###
        self.joueurSuivantLabel = tk.Label(self.f_joueurSuivant, text = f"Tour du Joueur {self.joueurActuel}", font = "Lucida 18 bold", bg = '#1A1A2E', fg= '#FFFFFF')
        self.joueurSuivantButton = tk.Button(self.f_joueurSuivant, cursor="hand2", state="normal", text = "OK", font = "Lucida 16 bold", bg = '#224F84', fg= '#FFFFFF', height = 2, bd = 0)
        ### On lie les widgets à leur fonction ###
        self.joueurSuivantButton.bind("<Button-1>", self.lancerManche)
        self.f_joueurSuivant.bind("<Return>",self.lancerManche)
        self.joueurSuivantButton.bind("<Enter>", lambda event : self.joueurSuivantButton.config(bg = "#4A78AE"))
        self.joueurSuivantButton.bind("<Leave>", lambda event : self.joueurSuivantButton.config(bg = "#224F84"))
        ### On place les widgets ###
        self.joueurSuivantLabel.pack(fill="both", anchor="center", expand=True)
        self.joueurSuivantButton.pack(fill="x", anchor="s")

    def afficherTourJoueurSuivant(self, *event):                                  
        """
        Affiche que c'est au tour du joueur suivant
        :param: self : la fenetre racine, event : l'évènement (clic sur le bouton)
        :return: None
        """
        if len(self.f_graph.canevas.find_all()) > 2 or self.perdu:                  # Si le joueur a placé un marqueur ou si un joueur a perdu, on passe au joueur suivant
            
            self.clickSound.play()                                                  # On joue le son du clic
            self.fiveSecLeft.stop()                                                 # On arrête le compte à rebours                              
            self.joueurActuel += 1                                                  # On passe au joueur suivant

            if self.perdu:                                                          # Si un joueur a perdu

                self.f_timesOut.destroy()                                           # On ferme la fenêtre qui indique qu'un joueur a perdu
                self.perdu = False                                                  # On remet la variable perdu à False

            if self.joueurActuel <= self.nbJoueur:                                  # Si le joueur n'est pas le dernier joueur à jouer pour cette manche
      
                self.displayTime = False                                            # On arrête le décompte du temps
                self.f_graph.withdraw()                                             # On ferme la fenêtre du graphique
                self.f_joueurSuivant = tk.Toplevel(self.racine, bg="#1A1A2E")       # On crée une nouvelle fenêtre
                self.f_joueurSuivant.title(f"Tour du Joueur {self.joueurActuel}")   # On lui donne un titre
                self.f_joueurSuivant.resizable(width=False, height=False)           # On empêche le redimensionnement de la fenêtre
                self.f_joueurSuivant.geometry(f"500x500+{self.moniteurWidth//2-250}+{self.moniteurHeight//2-250}")  # On dimensionne la fenêtre et la place au centre de l'écran
                self.f_joueurSuivant.protocol("WM_DELETE_WINDOW",self.fermetureFenetreGraph)    # On associé la fermeture de la fenêtre à la fonction fermetureFenetreGraph
                self.f_joueurSuivant.wait_visibility()                              # On attend que la fenêtre soit visible
                self.f_joueurSuivant.grab_set()                                     # On empêche l'utilisateur d'intéragir avec les autres fenêtres
                self.f_joueurSuivant.focus_force()                                  # On met le focus sur la fenêtre
                ### On crée les widgets ###
                self.joueurSuivantLabel = tk.Label(self.f_joueurSuivant, text = f"Tour du Joueur {self.joueurActuel}", font = "Lucida 18 bold", bg = '#1A1A2E', fg= '#FFFFFF')  
                self.joueurSuivantButton = tk.Button(self.f_joueurSuivant, cursor="hand2", state="normal", text = "OK", font = "Lucida 16 bold", bg = '#224F84', fg= '#FFFFFF', height = 2, bd = 0)
                ### On lie les widgets à leur fonction ###
                self.joueurSuivantButton.bind("<Button-1>", self.passerJoueurSuivant) 
                self.joueurSuivantButton.bind("<Enter>", lambda event : self.joueurSuivantButton.config(bg = "#4A78AE"))
                self.joueurSuivantButton.bind("<Leave>", lambda event : self.joueurSuivantButton.config(bg = "#224F84"))  
                self.f_joueurSuivant.bind("<Return>",self.passerJoueurSuivant)          
                ### On place les widgets ###
                self.joueurSuivantLabel.pack(fill="both", anchor="center", expand=True)
                self.joueurSuivantButton.pack(fill="x", anchor="s")

            else:                                                                   # Sinon, on affiche la position des joueurs et de la capitale

                self.displayTime = False                                            # On arrête le décompte du temps
                self.afficherResultatManche()                                       # On affiche le résultat de la manche

    def reinitialiserMap(self):
        """
        Réinitialise la map en supprimant les marqueurs du joueur actuel
        :param: self : la fenêtre racine
        :return: None
        """
        if len(self.f_graph.canevas.find_all()) > 2:                                # Si le joueur a placé un marqueur, on le supprime

            while len(self.f_graph.canevas.find_all()) != 2:                        # On supprime les marqueurs du joueur actuel
                
                self.f_graph.canevas.delete(self.f_graph.canevas.find_all()[-1])

    def passerJoueurSuivant(self, *event):
        """
        Permet de passer au joueur suivant
        :param: self : la fenêtre racine
        :return: None
        """
        self.clickSound.play()                                                                              # On joue le son du clic
        self.f_joueurSuivant.destroy()                                                                      # On ferme la fenêtre du joueur suivant
        self.f_graph.deiconify()                                                                            # On affiche la fenêtre du graphique
        self.validateButton.unbind("<Enter>")                                                               # On désactive le survol du bouton
        self.validateButton.unbind("<Leave>")                                                               #
        self.validateButton.configure(bg = '#0F3460', cursor="arrow", state="disabled")                                                       
        self.labelTemps.configure(text = f"Temps: 15", fg = "#FFFFFF")                                      # On réinitialise le temps 

        if self.nbJoueur == 1:                                                                              # Si il y a plus d'un joueur, on enleve la fenetre qui affichait les tours des joueurs
                                                                        
            self.labelTemps.configure(text = f"Temps: infini", fg = "#FFFFFF")

        self.displayTime = True                                                                             # On relance le décompte du temps
        self.ref = time.time()                                                                              # On réinitialise la référence du temps
        self.afficherTemps()                                                                                # On affiche le temps
        self.reinitialiserMap()                                                                             # On réinitialise la map

        self.labelJoueurActuel.configure(text = f"Tour du Joueur {self.joueurActuel}", fg = "#FFFFFF")      # On affiche le joueur actuel

    def afficherResultatManche(self, *event):
        """
        Permet de passer à la manche suivante
        :param: self : la fenêtre racine
        :return: None
        """
        self.clickSound.play()                                                                              # On joue le son du clic
        self.perdu = False                                                                                  # On réinitialise la variable perdu
        self.f_graph.deiconify()                                                                            # On affiche la fenêtre du graphique
        self.labelTemps.configure(text = f"Temps: infini", fg = "#FFFFFF")       

        if self.nbJoueur != 1:                                                                              # Si il y a plus d'un joueur, on enleve la fenetre qui affichait les tours des joueurs
            
            self.f_joueurSuivant.destroy()                                                                  # On ferme la fenêtre du affichant que c'est le tour du joueur suivant
            self.labelTemps.configure(text = f"Temps: 15", fg = "#FFFFFF")                                  # On réinitialise le temps
  
        self.f_graph.canevas.unbind("<Button-1>")                                                           # On désactive le clic gauche sur la map
        self.afficherPositionCapitale()                                                                     # On affiche la position de la capitale
        self.labelJoueur.configure(text=self.afficherJoueurEtScore())                                       # On met à jour le label affichant les joueurs et leur score
        self.validateButton.unbind("<Button-1>")                                                            # On désactive le clic gauche sur le bouton
        self.f_graph.unbind("<Button-1>")                                                                   # On désactive le clic gauche sur la map
        
        if self.nbRoundRestant <= 0:                                                                        # Si le nombre de manche restante est égal à 0, on affiche le classement
            
            
            self.validateButton.configure(text = "Afficher le classement", bg="#E94560", fg="white", cursor="hand2", state="normal")        # On change le texte du bouton
            self.validateButton.bind("<Button-1>", self.afficherClassement)                                 # On associe le clic gauche à la fonction afficherClassement
            self.validateButton.bind("<Enter>", lambda event : self.validateButton.config(bg = "#FF738A"))  # On associe le survol du bouton à la fonction lambda
            self.validateButton.bind("<Leave>", lambda event : self.validateButton.config(bg = "#E94560"))  #
            self.f_graph.bind("<Return>",self.afficherClassement)                                           # On associe la touche entrée à la fonction afficherClassement

        else:                                                                                               # Sinon, on passe à la manche suivante

            self.validateButton.configure(text = "Manche suivante", bg="#E94560", fg="white", cursor="hand2", state="normal")               # On change le texte du bouton
            self.validateButton.bind("<Button-1>", self.passerMancheSuivante)                               # On associe le clic gauche à la fonction passerMancheSuivante  
            self.validateButton.bind("<Enter>", lambda event : self.validateButton.config(bg = "#FF738A"))  # On associe le survol du bouton à la fonction lambda
            self.validateButton.bind("<Leave>", lambda event : self.validateButton.config(bg = "#E94560"))  #
            self.f_graph.bind("<Return>",self.passerMancheSuivante)                                         # On associe la touche entrée à la fonction passerMancheSuivante
                    
    def passerMancheSuivante(self, event):
        """
        Permet de passer à la manche suivante
        :param: self : la fenêtre racine, event : l'évènement (clic gauche ou touche entrée)
        :return: None
        """
        self.clickSound.play()                                                                                  # On joue le son du clic	
        self.nbRoundRestant -= 1                                                                                # On décrémente le nombre de manche restante
        self.joueurActuel = 1                                                                                   # On réinitialise le joueur actuel
        
        if self.nbJoueur != 1:                                                                                  # Si il y a plus d'un joueur qui joue, on affiche le tour du joueur afin de mettre au courant les autres joueurs

            self.afficherTourJoueurUn()                                                                         # On affiche le tour du joueur

        self.choisirCapitale()                                                                                  # On choisit une nouvelle capitale
        self.labelJoueurActuel.configure(text = f"Tour du Joueur {self.joueurActuel}")                          # On affiche le joueur actuel
        self.labelRoundActuel.configure(text = f"Manche {self.nbRound - self.nbRoundRestant}/{self.nbRound}")   # On affiche le round actuel
        self.capitaleLabel.configure(text = self.randomCapitale['capital'])                                     # On affiche la capitale
        self.validateButton.configure(text = "Valider", bg = '#0F3460', fg= '#FFFFFF', cursor="arrow", state="disabled")          # On change le texte du bouton
        self.validateButton.unbind("<Button-1>")                                                                # On désactive le clic gauche sur le bouton
        self.f_graph.unbind("<Return>")                                                                         # On désactive la touche entrée sur la map
        self.validateButton.unbind("<Enter>")                                                                   # On désactive le survol du bouton
        self.validateButton.unbind("<Leave>")                                                                   #
        self.validateButton.bind("<Button-1>", self.afficherTourJoueurSuivant)                                  # On associe le clic gauche à la fonction afficherTourJoueurSuivant
        self.f_graph.bind("<Return>",self.afficherTourJoueurSuivant)                                            # On associe la touche entrée à la fonction afficherTourJoueurSuivant
        self.f_graph.canevas.bind("<Button-1>", self.ajouterMarqueur)                                           # On associe le clic gauche à la fonction ajouterMarqueur
        self.reinitialiserMap()                                                                                 # On réinitialise la map    

    def distanceKm(self, lat_a_degre, lon_a_degre, lat_b_degre, lon_b_degre):
        """
        Calculer la distance  en km entre deux lieux repérées par leurs coordonnées GPS 
        - lat_a_degre, lon_a_degre, lat_b_degre, lon_b_degre (float): les 4 coordonnées des deux emplacements en degrés (latitude, lonitude)
        Retour:
        - la valeur de la distance réelle ramenée à la surface de la terre (valeur approchée) en float
        """
        lat_a = math.pi*lat_a_degre/180                                                                    
        lon_a = math.pi*lon_a_degre/180                                                                        
        lat_b = math.pi*lat_b_degre/180                                                                         
        lon_b = math.pi*lon_b_degre/180
        rayonTerre = 6378.000
        distKm = rayonTerre * (math.pi/2 - math.asin(math.sin(lat_b) * math.sin(lat_a) + math.cos(lon_b - lon_a) * math.cos(lat_b) * math.cos(lat_a)))  # Calcul de la distance en km entre les deux points 
       
        return distKm

    def afficherClassementJoueur(self):
        """
        Permet d'afficher le classement des joueurs
        :param: self : la fenêtre racine
        :return: texte : le texte à afficher
        """
        texte = "\n"                                                            # On initialise le texte

        for id, score in self.sortedDicoScore.items():                          # Pour chaque joueur et son score

            texte += f"Joueur {id} : {score:.2F}\n\n"                           # On ajoute le joueur et son score au texte

        return texte                                                            # On retourne le texte

    def afficherClassement(self, event):
        """
        Permet d'afficher le classement des joueurs
        :param: self : la fenêtre racine, event : l'évènement (clic gauche ou touche entrée)
        :return: None
        """
        self.clickSound.play()                                                      # On joue le son du clic
        self.f_graph.withdraw()                                                     # On cache la fenêtre de la map
        self.f_classement = tk.Toplevel(self.racine, bg="#1A1A2E")                  # On crée une nouvelle fenêtre
        self.f_classement.title(f"Classement")                                      # On change le titre de la fenêtre
        self.f_classement.resizable(width=False, height=False)                      # On empêche le redimensionnement de la fenêtre
        self.f_classement.geometry(f"500x{100+self.nbJoueur*100}+{self.moniteurWidth//2-250}+{self.moniteurHeight//2-(100+self.nbJoueur*100)//2}")  # On change la taille de la fenêtre et on la centre
        self.f_classement.protocol("WM_DELETE_WINDOW",self.fermetureFenetreGraph)   # On associe la fermeture de la fenêtre à la fonction fermetureFenetreGraph
        self.f_classement.wait_visibility()                                         # On attend que la fenêtre soit visible
        self.f_classement.grab_set()                                                # On empêche l'accès aux autres fenêtres
        self.f_classement.focus_force()                                             # On met le focus sur la fenêtre
        ### On crée les widgets ###
        self.titleLabel = tk.Label(self.f_classement, text = f"Classement :", font = "Lucida 20 bold", height = 2, bg = '#224F84', fg= '#FFFFFF')
        self.classementLabel = tk.Label(self.f_classement, text = self.afficherClassementJoueur(), font = "Lucida 18 bold", bg = '#1A1A2E', fg= '#FFFFFF', anchor="center")
        self.quitterButton = tk.Button(self.f_classement, cursor="hand2", state="normal", text = "Quitter", font = "Lucida 18 bold", bg = '#224F84', fg= '#FFFFFF', height = 2, bd = 0)
        ### On associe les widgets aux fonctions ###
        self.quitterButton.bind("<Button-1>", self.fermetureFenetreGraph)
        self.quitterButton.bind("<Enter>", lambda event : self.quitterButton.configure(bg = "#4A78AE"))
        self.quitterButton.bind("<Leave>", lambda event : self.quitterButton.configure(bg = "#224F84"))
        self.f_classement.bind("<Return>",self.fermetureFenetreGraph)
        ### On place les widgets ###
        self.titleLabel.pack(side = "top", fill="x", anchor="n", expand=True)
        self.classementLabel.pack(side = "top", fill="x", anchor="n", expand=True)
        self.quitterButton.pack(side = "bottom", fill="x", anchor="s")

        if self.nbJoueur == 1:

            self.titleLabel.configure(text = f"Score :")
            self.classementLabel.configure(text = self.dicoScore[1], font = "Lucida 20 bold")

    def afficherJoueurEtScore(self):
        """
        Permet d'afficher les joueurs et leurs scores dans la fenêtre de jeu
        :param: self : la fenêtre racine
        :return: texte : le texte à afficher
        """
        texte = ""                                                                                                  # On initialise le texte
        self.sortedDicoScore = dict(sorted(self.dicoScore.items(), key=lambda item:item[1], reverse=True))          # On trie le dictionnaire des scores

        for i in self.sortedDicoScore:                                                                              # Pour chaque joueur

            texte += "\n\nJoueur " + f"{i}: {self.sortedDicoScore[i]:.3F}\n______________________________"          # On ajoute le joueur et son score au texte (et on ajoute des tirets pour séparer les joueurs, purement esthétique)
        
        texte = texte.replace('\n','',1)                                                                            # On enlève le premier retour à la ligne

        return texte                                                                                                # On retourne le texte
    
    def afficherFenetreTempsEcoulé(self):
        """
        Permet d'afficher la fenêtre de temps écoulé qui indique au joueur que le temps est écoulé et que c'est au tour du joueur suivant
        :param: self : la fenêtre racine
        :return: None
        """
        self.f_timesOut = tk.Toplevel(self.racine, bg="#1A1A2E")                                      # On crée une nouvelle fenêtre                                     
        self.f_timesOut.title("Perdu !")                                                              # On change le titre de la fenêtre
        self.f_timesOut.resizable(width=False, height=False)                                          # On empêche le redimensionnement de la fenêtre
        self.f_timesOut.geometry(f"500x500+{self.moniteurWidth//2-250}+{self.moniteurHeight//2-250}") # On change la taille de la fenêtre et on la centre
        self.f_timesOut.protocol("WM_DELETE_WINDOW",self.fermetureFenetreGraph)                       # On associe la fermeture de la fenêtre à la fonction fermetureFenetreGraph
        self.f_timesOut.wait_visibility()                                                             # On attend que la fenêtre soit visible
        self.f_timesOut.grab_set()                                                                    # On empêche l'accès aux autres fenêtres
        self.f_timesOut.focus_force()                                                                 # On met le focus sur la fenêtre
        ### On crée les widgets ###
        self.labelNoMoreTime = tk.Label(self.f_timesOut, text = f"Vous n'avez plus de temps !\n\n C'est mainteant au tour du Joueur {self.joueurActuel + 1}", font = "Lucida 18 bold", bg = '#1A1A2E', fg= '#FFFFFF') 

        if self.joueurActuel == self.nbJoueur:                                                          # Si le joueur actuel est le dernier joueur, on modifie le texte du label

            self.labelNoMoreTime.configure(text = f"Vous n'avez plus de temps !\n\n Les résultats de la manche\nvont être affichés", font = "Lucida 18 bold", bg = '#1A1A2E', fg= '#FFFFFF')

        self.buttonNoMoreTime = tk.Button(self.f_timesOut, cursor="hand2", state="normal", text = "OK", font = "Lucida 16 bold", bg = '#224F84', fg= '#FFFFFF', height = 2, bd = 0)
        ### On associe les widgets aux fonctions ###
        self.buttonNoMoreTime.bind("<Button-1>", self.afficherTourJoueurSuivant)
        self.buttonNoMoreTime.bind("<Enter>", lambda event : self.buttonNoMoreTime.configure(bg = "#4A78AE"))
        self.buttonNoMoreTime.bind("<Leave>", lambda event : self.buttonNoMoreTime.configure(bg = "#224F84"))
        self.f_timesOut.bind("<Return>",self.afficherTourJoueurSuivant)
        ### On place les widgets ###
        self.labelNoMoreTime.pack(fill="both", anchor="center", expand=True)
        self.buttonNoMoreTime.pack(fill="both", anchor="s")

    def afficherTemps(self):
        """
        Permet d'afficher le temps restant
        :param: self : la fenêtre racine
        :return: None
        """

        if self.nbJoueur != 1:                                                                                          # Si le nombre de joueur est différent de 1

            now = time.time()                                                                                           # On récupère le temps actuel

            if 15 - (now - self.ref) > 5 and self.displayTime:                                                          # Si le temps restant est supérieur à 5 secondes

                self.labelTemps.configure(text = f"Temps: {abs(15 - (now - self.ref)):.0F}")                            # On affiche le temps restant
                self.racine.after(10, self.afficherTemps)                                                               # On rappelle la fonction après 10 ms (la fonction est appelée toutes les 10 ms pour éviter les problèmes de latence)

            elif 15 - (now - self.ref) <= 5 and 15 - (now - self.ref) > 0 and self.displayTime:                         # Si le temps restant est inférieur à 5 secondes et supérieur à 0 secondes

                self.fiveSecLeft.play()                                                                                 # On joue le son des 5 dernières secondes
                self.labelTemps.configure(text = f"Temps: {abs(15 - (now - self.ref)):.1F}", fg = "#FF0000")            # On affiche le temps restant en rouge
                self.racine.after(10, self.afficherTemps)                                                               # On rappelle la fonction après 10 ms

            elif 15 - (now - self.ref) <= 0:                                                                            # Si le temps restant est inférieur ou égal à 0 secondes
                
                if self.joueurActuel in self.dicoPositionsJoueurs:                                                      # Si le joueur est dans le dictionnaire des positions des joueurs (si il a déjà placé son pion)

                    self.dicoPositionsJoueurs.pop(self.joueurActuel)                                                    # On le supprime du dictionnaire des positions des joueurs

                self.fiveSecLeft.stop()                                                                                 # On arrête le son des 5 dernières secondes
                self.timesOut.play()                                                                                    # On joue le son du temps écoulé
                self.f_graph.withdraw()                                                                                 # On cache la fenêtre de jeu
                self.perdu = True                                                                                       # On indique que le joueur a perdu
                self.labelTemps.configure(text = f"Temps: {abs(15 - (now - self.ref)):.0F}")                            # On affiche le temps restant
                self.afficherFenetreTempsEcoulé()                                                                       # On affiche la fenêtre de temps écoulé

        else:                                                                                                           # Si le nombre de joueur est égal à 1

            self.labelTemps.configure(text = f"Temps: infini")                                                          # On affiche que le temps est infini (pas de limite de temps en mode solo)

if __name__ == "__main__":  

    app = Fenetre()
    app.racine.mainloop()
