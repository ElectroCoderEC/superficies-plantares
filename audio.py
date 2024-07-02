from pygame import mixer

audio_bien = "static/sonidos/bien.mp3"
# sound1 = pygame.mixer.Sound(audio_file1)
# colocarse correctamente
audio_coloquese = "static/sonidos/coloquese.mp3"
# sound2 = pygame.mixer.Sound(audio_file2)
# Calculo
audio_medicion = "static/sonidos/medicion.mp3"


class Reproductor:

    def __init__(self):
        self.sonido = None

    def play_audio(self, path):
        mixer.init()
        mixer.music.load(path)
        mixer.music.play()

    def play_bien(self):
        mixer.init()
        mixer.music.load(audio_bien)
        mixer.music.play()

    def play_coloquese(self):
        mixer.init()
        mixer.music.load(audio_coloquese)
        mixer.music.play()

    def play_medicion(self):
        mixer.init()
        mixer.music.load(audio_medicion)
        mixer.music.play()
