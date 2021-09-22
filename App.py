'''
Chord app
May 24, 2021
By Robin Nash

This app allows users to input chord names and it will display
the names of the chords in flats or sharps representation depending on the user's input.
It will also display how to play those chords on the
instrument the user selects (ukulele, guitar, or banjo).
The user can then transpose the chords by any number of halfsteps
'''

from chord import *

def display_tabs(instrument,chord):
    '''Displays the tabs for a chord on a given instrument
    instruction on how to read these tabs are found in help.txt'''
    if instrument != None:
        print(str(chord.getTabs(instrument, [], []))[1:-1].replace(', ',' ').replace("'",""))

def display_notes(chord,flats):
    '''Displays the chord name then the notes that make up the chord'''
    notes = chord.getNotes(flats)
    name = chord.getName(flats)
    print(name+":"," ".join(notes))
        
# so user can switch instruments with one key
short = {'g':'guitar','u':'ukulele','b':'banjo','n':'no instrument'}
# add None to instruments
instruments['no instrument'] = None

# get info for the top
info_file = open("info.txt")
info = info_file.read()
info_file.close()

# get help_info
help_file = open("help.txt")
help_info = help_file.read()
help_file.close()

# default will present as flats
flats = True

instrument = None

chords = []

# print info
print(info)

# Ask User for prompts

intros = ['Do you want flats or sharps representaion? Enter f/s: ',\
          'Do you want the chords to be shown on ukulele, guitar, banjo, or no instrument?\nEnter u/g/b/n:',\
          'Enter chords each separated by a space: ',\
          'Enter chords or a transpose value: ']

valid = [False for i in intros]

for i in range(len(intros)):
    while not valid[i]:
        print()
        inp = input(intros[i])

        # quit app
        if inp.lower() == 'q':
            print('Thanks for using the chord app by Robin Nash')
            break

        # flats or sharps
        elif inp in ['f','s']:
            flats = inp == 'f'
            print('Representation changed to ' + ('flats' if flats else 'sharps'))
            valid[0] = True

        # help
        elif inp == 'help':
            print(help_info)

        # set instrument
        elif inp in short.keys():
            instrument = instruments[short[inp]]
            print("Instrument set to", short[inp])
            valid[1] = True
            
        # chords
        else:
            current_chords = []
            
            # Transpose
            if valid[2] and inp.replace('-','').replace('+','').isdigit():
                current_chords = [c.getTransposed(int(inp)) for c in chords]
                
            # Set new chords
            else:
                chordNames = inp.split()
                chordNames = [name for name in chordNames if isValid(name)]
                if chordNames != []:
                    chords = [Chord(name) for name in chordNames]
                    current_chords = chords.copy()
                    valid[2] = True
            
            ### Display the info! ###
            for chord in current_chords:
                # notes in chord
                display_notes(chord,flats)
                # tabs
                display_tabs(instrument,chord)
                
