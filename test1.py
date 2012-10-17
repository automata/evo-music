# -*- coding: utf-8 -*-

from music21 import *

#motivo = converter.parse("scores/motivo.mid")
bach = corpus.parse("bach/bwv10.7.mxl")
viaro = converter.parse("scores/viaro.xml")

# pegando apenas soprano
soprano = bach.getElementById('Soprano')

# pegando as medidas
for measure in soprano[1:]:
    print [(note.name, note.fullName) for note in measure.notes]

