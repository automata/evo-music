# -*- coding: utf-8 -*-

# ag para geração de frases

from music21 import *
import random as rand

#motivo = converter.parse("scores/motivo.mid")
#bach = corpus.parse("bach/bwv10.7.mxl")
#viaro = converter.parse("scores/viaro.xml")

# pegando apenas soprano
#soprano = bach.getElementById('Soprano')

# pegando as medidas
#for measure in soprano[1:]:
#    print [(note.name, note.fullName) for note in measure.notes]

#######

class Individuo(object):
    def __init__(self, num_compassos=4):
        # geramos N notas com altura e duração aleatórias, volume padrão
        frase = stream.Stream()

        alturas = 'c c# d d# e f f# g g# a a# b'.split()
        # TODO: podemos trabalhar com qualquer número!
        duracoes = [4., 2., 1., .5, .25, .125, .0625]

        for i in xrange(num_compassos):
            compasso = stream.Measure()

            soma_duracoes = 0.
            while soma_duracoes < 4.:
                nova_altura = rand.choice(alturas) + str(rand.randint(0, 8))
                nova_dur = rand.choice(duracoes)
                # persiste até encontrar uma duração que feche o compasso
                while (nova_dur+soma_duracoes) > 4.:
                    nova_dur = rand.choice(duracoes)
                nova_nota = note.Note(nova_altura)
                nova_nota.duration = duration.Duration(nova_dur)
                compasso.append(nova_nota)
                soma_duracoes += nova_dur
            frase.append(compasso)
        self.dna = frase

    # características que podem ser usadas para gerar novos #################
    def intervalos(self):
        pass

    def asc_desc_intervalar(self):
        pass

    def asc_desc_ritmico(self):
        pass

    def ambito(self):
        return self.dna.analyze('ambitus')

    def escala(self):
        pass

    def num_notas(self):
        return sum([len(x.getElementsByClass(note.Note)) for x in self.dna])
    #########################################################################
    
    def partitura(self):
        self.dna.show('musicxml')

    def toca(self):
        self.dna.show('midi')
    
