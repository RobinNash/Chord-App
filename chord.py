'''
Chord module
July 6, 2020
By Robin Nash

This module contains a Chord class, Instrument class, note functions, and musical and chord data.

The Chord class holds a name of a chord and has functions to return the notes that make up the chord,
how to play the chord on different instruments, and more.
The Instrument class holds data on an instrument.
This module contains information on musical instruments.


Definitions
Simplified form: can be sharp or flat; each section is of the proper dictionary form
Sharp form: simplified form and tonic is always expressed as a sharp
Flat form: simplified form and tonic is always expressed as a flat
'''

class Chord:
    '''
    Holds the data for a chord.
    Finds the notes and qualities that make up a chord based on its name.
    Can transpose the chord by any number of half steps.
    Can map the fingering for a chord on ukulele, guitar, or banjo.
    Currently supports chords of type major, minor, sus, sus2, aug, dim, and
    a maj7, dom7, or maj6 can be added to any to add an extra interval.
    '''
    
    def __init__(self,chordName):
        self.originalName = chordName
        self.name = chordName
        self.qualities = []
        self.tonic = ""
        # Simplifys chord name and sets chord qualities
        self.setNameAndQual()

    def __repr__(self):
        return self.name


    def setNameAndQual(self, flat = True):
        '''Helper function to set chord name in simplified form and set chord qualities'''
        name = self.name

        # Get valid tonic
        parts = [name[0].upper()]
        name = name[1:]
        last = None
        
        # Checks for extra (fourth) intervals (ex. Maj7)
        for extra in extraInts:
            for crappy in [q for q in extraInts[extra] if len(q)<=len(name)]:
                # Replaces the end of the name if it ends with the extraInt
                if name[-len(crappy):] == crappy:
                    name = name[:-len(crappy)]
                    last = extra
                    break
                
        # Checks for flat or sharp
        for crappy in [q for q in accidentals['b'] if len(q)<=len(name)]:
            if crappy == name[:len(crappy)]:
                name = name[len(crappy):]
                parts[0]+='b'
                break
        for crappy in [q for q in accidentals['#'] if len(q)<=len(name)]:
            if crappy == name[:len(crappy)]:
                name = name[len(crappy):]
                parts[0]+='#'
                break
            
        # Fixes potentially strange enharmonic equivalents of tonic (ex Cb -> B)
        parts[0] = validify(parts[0])
        
        # Checks for the main chord quality
        for qual in qualities:
            for crappy in qualities[qual]:
                if crappy == name:
                    parts.append(qual)
                    name = ''
                    break
            # in case of 'aug' or something, it will be an empty string then it will think there's also a Major
            if len(parts) == 2:
                break

        # add fourth to list
        if last:
            parts.append(last)

        # make sure name string is empty
        if name!= "" or parts[0][0] not in "ABCDEFG":
            raise ValueError ('Invalid Chord Name:', self.name)

        # Set the variables
        self.name = "".join(parts)
        self.tonic = parts.pop(0)
        self.qualities = parts

    def getName(self, flat = True):
        '''Returns the name of the chord'''
        name = self.name
        if self.tonic.endswith("#") and flat:
            name = flatten(self.tonic) + name[2:]
            
        if self.tonic.endswith("b") and not flat:
            name = sharpen(self.tonic) + name[2:]
            
        return name
    
    def getIntervals(self):
        '''Converts the qualities into intervals. Intergers represent # of half steps from tonic'''
        intervals = ()
        for qual in self.qualities:
            intervals += qualityIntervals[qual]
        return intervals

    def getNotes(self, flat = True):
        '''Returns the notes the chord is made of'''
        
        # Picks flats or sharps list depending on tonic and flat argument
        tonic = flatten(self.tonic) if flat else sharpen(self.tonic)
        if len(self.tonic) == 1:
            notes = flats if flat else sharps
        else:
            notes = flats if isFlat(tonic) else sharps
            
        chordNotes = [tonic]
        start = notes.index(tonic)
        for interval in self.getIntervals():
            chordNotes.append(notes[(start+interval)%len(notes)])
        return chordNotes


    def getTabs(self, instrument, tab = [], tabs = []):
        '''Returns many fingerings for the chord on a given instrument'''
        notes = self.getNotes(flat = False)
        
        # List of lists that each hold where the first occurance of all notes in the chord is played on each string
        stringTabs = [sorted([instrument.notes[note][string] for note in notes]) for string in range(instrument.strings)]

        # Makes every combo of tabs for chord (does not ensure all notes are being played)
        if len(tab) < instrument.strings:
            for i in range(len(notes)):
                self.getTabs(instrument, tab[:]+[stringTabs[len(tab)][i]], tabs)
                
        # Adds the tab if it contains all notes and fingering is close enough together   
        else:
            # accomodate banjo
            if instrument.name == 'banjo':
                if [] not in [[tab[i] for i in range(len(tab)) if tab[i]==instrument.notes[note][i]] for note in notes if note!="G"] and greatestDistance(tab) <= instrument.fingerDistance:
                    tab.append(0 if 'G' in notes else 'x')
                    tabs.append(tab[:])
            else:
                if [] not in [[tab[i] for i in range(len(tab)) if tab[i]==instrument.notes[note][i]] for note in notes] and greatestDistance(tab) <= instrument.fingerDistance:
                    tabs.append(tab[:])

        return tabs

    def getTransposed(self, halfSteps):
        '''Returns a transposed chord object transposed by halfSteps half steps'''
        notes = flats if isFlat(self.tonic) else sharps
        tonic = notes[(notes.index(self.tonic) + halfSteps)%len(notes)]
        return Chord("".join([tonic] +self.qualities))
    
    def isSharp(self):
        '''Returns if the tonic is not flat'''
        return isSharp(self.tonic)
    
    def isFlat(self):
        '''Returns if the tonic is not sharp'''
        return isFlat(self.tonic)
    
#### Instrument Class #######################################################################
class Instrument:
    def __init__(self, name, tuning, fingerDistance = 4):
        self.name = name
        self.fingerDistance = fingerDistance
        #Tuning should be first string up (ex for guitar: ["E","B","G","D","A","E"])
        self.tuning = tuning
        self.strings = len(tuning)
        # Tuple of first occurance of each note on each string as sharps
        self.notes = {note : tuple(getDistance(sharps, sharpen(n), note) for n in tuning) for note in sharps}
        if name == 'banjo':
            for note in self.notes:
                self.notes[note] = self.notes[note][:-1] + ((0,) if note == "G" else (self.notes[note][-1]+5,))
                
# modified for 5th string
class Banjo(Instrument):
    def __init__(self, fingerDistance = 4):
        super().__init__("banjo", ["D","B","G","D","G"], fingerDistance = 4)
        self.strings = 4 # not true, but we want to mostly ignore the last string
        self.notes_full = {}
        for note in self.notes:
            self.notes_full[note] = self.notes[note][:-1] + ((0,) if note == "G" else (self.notes[note][-1]+5,))
            self.notes[note] = self.notes[note][:-1]

   
#### Note functions #####################################################################################

def validify(note):
    '''Fixes strange enharmonic equivalents. For example turns a note like Cb into B.
    However if note is invalid like "H#", it will return the original note "H#"'''
    bad = ['B#','E#','Cb','Fb']
    good = ['C','F','B','E']
    if note in bad:
        note = good[bad.index(note)]
    return note


def isSharp(note):
    '''Returns Boolean variable for if a given note name is sharp'''
    return True if (note+" ")[1] == "#" else False

def isFlat(note):
    '''Returns Boolean variable for if a given note name is flat'''
    return True if (note+" ")[1] == "b" else False

def sharpen(note):
    '''Returns sharp equivilent of a note, note must be inputted in simplified form'''
    if note in flats:
        note = sharps[flats.index(note)]
    return note

def flatten(note):
    '''Returns flat equivilent of a note, note must be inputted in simplified form'''
    if note in sharps:
        note = flats[sharps.index(note)]
    return note

def getDistance(s, a, b):
    '''Returns the round-about distance between 2 items in a list'''
    A = s.index(a)
    B = s.index(b)
    if A<=B:
        return B-A
    else:
        return len(s)-(A-B)
    
def greatestDistance(tab):
    '''Returns the greatest distance between 2 intergers in a list of intergers (expect 0 because open string)'''
    return max([i for i in tab if i != 0]) - min([i for i in tab if i != 0])

def getIntName(halfSteps):
    '''Returns the name of an interval given the number of half steps from the tonic'''
    return intervalNames[halfSteps%len(intervalNames)]

def isValid(chordName):
    '''Returns if a given chord name is valid to create a chord object'''
    try:
        chord = Chord(chordName)
        return True
    except ValueError:
        return False


#### Music and Chord Data ####################################################################

# dictionaries for crappy parts
accidentals = {'#':['#','sharp'],'b':['flat','f','b','♭']}#,'s'
qualities = {'dim':['dim','-','diminished'],'aug':['aug','augmented','+'],'sus2':['Sus2','sus2'],'sus':['Sus4','sus4','sus','Sus'],'':['M','Maj','maj','major',''],'m':['minor','min','m']}
extraInts = {'Maj7':['Maj7','maj7','major7'],'7':['7','dom7','7th'],'6':['6','maj6','Maj6']}
parts = [extraInts, qualities]

# List of intervals from tonic in semitones that are associated with each chord quality
qualityIntervals = {'m': (3, 7), 'dim': (3, 6), 'aug': (4, 8), 'sus': (5, 7), 'sus2': (2, 7), '': (4, 7),   'Maj7': (11,), '7': (10,), '6': (9,)}
                 
intervalNames = ['P1','m2','M2','m3','M3','P4','Tri','P5','m6','M6','m7','M7','P8']

sharps= ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
flats = ['C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B']

############## Instrument Data ##############################################

# Ukulele
ukuleleNotes = {'C':(3,8,0,5), 'C#':(4,9,1,6), 'D':(5,10,2,7), 'D#':(6,11,3,8), 'E':(7,0,4,9), 'F':(8,1,5,10), 'F#':(9,2,6,11), 'G':(10,3,7,0), 'G#':(11,4,8,1), 'A':(0,5,9,2), 'A#':(1,6,10,3), 'B':(2,7,11,4)}
ukuStrings = [[sharps[i%12] for i in range(i,19+i)] for i in [9,4,0,7]]
ukulele_ = {'name':'ukulele','notes':ukuleleNotes,'fingerDistance':4 ,'strings':4}
ukulele = Instrument("ukulele", ["A","E","C","G"], 4)

# Banjo
banjoNotes = {'C':(10,10,5,1,10), 'C#':(11,11,6,2,11), 'D':(12,0,7,3,0), 'D#':(13,1,8,4,1), 'E':(14,2,9,5,2), 'F':(15,3,10,6,3), 'F#':(16,4,11,7,4), 'G':(0,5,0,8,5), 'G#':(6,6,1,9,6), 'A':(7,7,2,10,7), 'A#':(8,8,3,11,8), 'B':(9,9,4,0,9)}
banjoStrings = [['G' for i in range(6)]+[sharps[i%12] for i in range(8,25)]]+[[sharps[i%12] for i in range(i,23+i)] for i in [sharps.index(note) for note in ('D','G','B','D')]]
banjo_ = {'name':'banjo','notes':banjoNotes,'fingerDistance':3 ,'strings':5}
##banjo = Instrument("banjo", ["D","B","G","D","G"])# last string is G but the string starts up 5 semitones
banjo = Banjo()

# Guitar
guitarStrings = [[sharps[i%12] for i in range(ii,19+ii)] for ii in [sharps.index(note) for note in 'EBGDAE']]
guitarNotes = {note:tuple([guitarStrings[x].index(note) for x in range(6)]) for note in sharps}
guitar_ = {'name':'guitar','notes':guitarNotes, 'fingerDistance':2 ,'strings':6}
guitar = Instrument("guitar", ["E","B","G","D","A","E"], 2)

instruments = {'ukulele':ukulele, 'banjo':banjo, 'guitar':guitar}



# Tests #
if __name__ == "__main__":
    print(banjo.notes)
    for c in ["C","A","A7","Am7"]:
        c= Chord(c)
        print(c)
        print(c.getTabs(banjo,[],[]))
        
    # mini test app
    flat = False
    while True:
        c = input("Enter chord name: ")
        if c in ['f','s']:
            flat = c == 'f'
            continue
        c = Chord(c)
        print(c.getNotes(flat))#
        print(c.getName(flat))
##        print(c.getNotes(True))

        
