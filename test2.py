# -*- coding: utf-8 -*-

# ag para geração de frases

from music21 import *
import random as rand
import copy

#motivo = converter.parse("scores/motivo.mid")
#bach = corpus.parse("bach/bwv10.7.mxl")
#viaro = converter.parse("scores/viaro.xml")

# pegando apenas soprano
#soprano = bach.getElementById('Soprano')

# pegando as medidas
#for measure in soprano[1:]:
#    print [(note.name, note.fullName) for note in measure.notes]

#######

# possíveis parâmetros:
# - probabilidade de ser nota ou pausa
# - quais características (de protótipo) utilizar para gerar novos indivíduos

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
                # TODO: decide se será nota ou pausa na moeda
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
        frase = []
        for i in xrange(self.num_compassos()):
            compasso = []
            qtd_notas = len(self.dna[i])
            pos = zip(range(qtd_notas-1), range(1, qtd_notas))
            dna = self.dna[i]
            compasso = [interval.notesToInterval(dna[x],dna[y]) for x,y in pos]
            frase.append(compasso)
        return frase

    def nomes_intervalos(self):
        frase = []
        for i in xrange(self.num_compassos()):
            compasso = []
            qtd_notas = len(self.dna[i])
            pos = zip(range(qtd_notas-1), range(1, qtd_notas))
            dna = self.dna[i]
            compasso = [interval.notesToInterval(dna[x],dna[y]).simpleName for x,y in pos]
            frase.append(compasso)
        return frase

    def direcao_intervalos(self):
        frase = []
        for i in xrange(self.num_compassos()):
            compasso = []
            qtd_notas = len(self.dna[i])
            pos = zip(range(qtd_notas-1), range(1, qtd_notas))
            dna = self.dna[i]
            compasso = [interval.notesToInterval(dna[x],dna[y]).direction for x,y in pos]
            frase.append(compasso)
        return frase

    def direcao_duracoes(self):
        def comp(dur1, dur2):
            if dur1 < dur2:
                return -1
            elif dur1 > dur2:
                return 1
            else:
                return 0
            
        frase = []
        for i in xrange(self.num_compassos()):
            compasso = []
            qtd_notas = len(self.dna[i])
            pos = zip(range(qtd_notas-1), range(1, qtd_notas))
            dna = self.dna[i]
            compasso = [comp(dna[x].duration.quarterLength,
                             dna[u].duration.quarterLength) for x,y in pos]
            frase.append(compasso)
        return frase

    def notas(self):
        frase = []
        for i in xrange(self.num_compassos()):
            qtd_notas = len(self.dna[i])
            compasso = [nota for nota in self.dna[i]]
            frase.append(compasso)
        return frase

    def duracoes(self):
        frase = []
        for parte in self.notas():
            durs = [nota.duration for nota in parte]
            frase.append(durs)
            
        return frase

    def ambito(self):
        #return self.dna.analyze('ambitus').chromatic.directed
        return self.dna.analyze('ambitus')

    def tonica(self):
        tom = self.dna.analyze('key')
        return tom.tonic

    # TODO: talvez a classe Contour esteja apenas no fork do genos (marcos)
    #def contorno(self):
    #    return contour.Contour(self.dna)

    def modo(self):
        tom = self.dna.analyze('key')
        return tom.mode

    def num_notas(self):
        return sum([len(x.getElementsByClass(note.Note)) for x in self.dna])

    def num_compassos(self):
        return len(self.dna)
    #########################################################################
    
    def partitura(self):
        self.dna.show('musicxml')

    def toca(self):
        self.dna.show('midi')

    # cria indivíduos a partir de uma característica ########################
    def copia_de(self, outro):
        # começamos com intervalos
        intervalos = outro.intervalos()
        nova_frase = stream.Stream()
        i = 0
        for compasso in intervalos:
            novas_notas = intervalos_para_notas(compasso)
            # e também copiamos as durações
            for j in xrange(len(novas_notas)):
                novas_notas[j].duration = outro.dna[i][j].duration
            nova_frase.append(novas_notas)
            i += 1
        self.dna = nova_frase

def intervalos_para_notas(intervalos):
    # parte de uma altura aleatória e vai seguindo transpondo
    alturas = 'c c# d d# e f f# g g# a a# b'.split()
    nova_altura = rand.choice(alturas) + str(rand.randint(0, 8))
    nota1 = note.Note(nova_altura)
    novo_compasso = stream.Measure([nota1])
    for intervalo in intervalos:
        nota2 = nota1.transpose(intervalo)
        nota1 = copy.deepcopy(nota2)
        novo_compasso.append(nota2)
    return novo_compasso

    
