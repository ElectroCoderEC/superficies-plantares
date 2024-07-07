from pygame import mixer

audio_intro = "static/sonidos/intro.mp3"
audio_registro = "static/sonidos/registro.mp3"
audio_bien = "static/sonidos/bien.mp3"
audio_coloquese = "static/sonidos/coloquese.mp3"
audio_medicion = "static/sonidos/medicion.mp3"
audio_error = "static/sonidos/error.mp3"


class Reproductor:

    def __init__(self):
        self.sonido = None

    def play_intro(self):
        mixer.init()
        mixer.music.load(audio_intro)
        mixer.music.play()

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

    def play_registro(self):
        mixer.init()
        mixer.music.load(audio_registro)
        mixer.music.play()

    def play_error(self):
        mixer.init()
        mixer.music.load(audio_error)
        mixer.music.play()
