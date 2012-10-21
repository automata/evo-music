# -*- coding: utf-8 -*-

from test2 import *

pai = Individuo()
filho = Individuo()
neto = Individuo()

filho.copia_de(pai)
neto.copia_de(filho)

a = stream.Part([pai.dna])
b = stream.Part([filho.dna])
c = stream.Part([neto.dna])

peca = stream.Score()
peca.append(a)
peca.append(b)
peca.append(c)
peca.show('text')
#peca.show('midi')
