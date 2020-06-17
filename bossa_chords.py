#https://www.oolimo.com/guitarchords/find

import glob
import time
import pygame as pg

#os.chdir('all_the_chords')
#playsound('a2_1.wav')
#playsound('a2_2.wav')
#playsound('e2_1.wav')



# Universal Constants
NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F',
              'F#', 'G', 'G#', 'A', 'A#', 'B']
OCTAVES = [1, 2, 3, 4, 5, 6, 7, 8]
ALL_NOTES = [i + str(j) for j in OCTAVES for i in NOTES]
SOUND_DIR = 'C:\\Users\\Brian\\all_the_chords'
TEMPO_MULT = 1

# Guitar Defaults
TUNING = ['E2', 'A2', 'D3', 'G3', 'B3', 'E4']
FRETS = 10
MAX_GAP = 4 # Max fret gap for single chords - can be decreased further later.



# Pygame for sound effects must be initialized
pg.mixer.init(buffer = 16, channels = 50)
pg.init()

# Define Key Classes
class Note:
    def __init__(self, name, string_num, guitar, get_fret = True):
        self.string = string_num # 1 for lowest, 6 for highest
        self.guitar = guitar
        self.name = name.replace('b','#').upper()
        if self.name != 'MUTE':
            self.type = self.name[:-1]
            self.oct = int(self.name[-1])
            self.fret = self.get_fret_num() if get_fret else 'NA'
            assert self.name in ALL_NOTES
            if self.name != 'NULL':
                self.get_sound()

    def __repr__(self):
        return str({'name':self.name,
                    'string':self.string,
                    'fret':self.fret})

    def __str__(self):
        return self.name + ", string " + str(self.string)

    def half_step(self, n):
        """Takes an integer, n. Returns another note n half steps above or
        below (if n is negative) the current note. Doesn't modify in place."""
        return Note(ALL_NOTES[ALL_NOTES.index(self.name) + n],
                    self.string, self.guitar, True)

    def higher_than(self, note):
        """Returns True if note is higher in pitch than the comparison note."""
        if ALL_NOTES.index(self.name) > ALL_NOTES.index(note.name):
            return True
        else:
            return False

    def get_fret_num(self):
        """Returns integer corresponding to fret number. Only called if note
        was found to be valid."""
        low_note = Note(self.guitar.tuning[self.string], self.string,
                        self.guitar, False)
        self.fret = (ALL_NOTES.index(self.name) -
                     ALL_NOTES.index(low_note.name))
        return self.fret

    def get_sound(self):
        if self.name not in ['MUTE','NULL']:
            self.sound_file = glob.glob(SOUND_DIR + "\\" + \
                                        self.type.replace('#','s').lower() + \
                                        str(self.oct) + '_*.wav')[0]
            self.sound = pg.mixer.Sound(self.sound_file)
            self.sound.set_volume(.35)

    def play(self, fadeout_ms=4000):
        if hasattr(self, 'sound'):
            self.sound.play()
            self.sound.fadeout(fadeout_ms)

    def stop(self):
        if hasattr(self, 'sound'):
            self.sound.stop()



class MuteNote(Note):
    def __init__(self, string_num, guitar):
        super().__init__('mute', string_num, guitar, False)
        self.name = 'MUTE'
        self.type, self.oct, self.fret = 'NA', 'NA', 'NA'


class NullNote(Note):
    def __init__(self, note_name, string_num, guitar):
        super().__init__(note_name, string_num, guitar, True)
        self.name = 'NULL'
        self.type, self.oct = 'NA', 'NA'


class Chord:
    def __init__(self, note_list, target, gap, lowest_fret, guitar):
        self.notes = note_list
        self.target = target
        self.gap = gap
        if gap and lowest_fret:
            self.lowest_fret = lowest_fret
            self.highest_fret = gap + lowest_fret
        else:
            self.lowest_fret = None
            self.highest_fret = None
        self.guitar = guitar

    def __repr__(self):
        names = [i.name.center(5, '-') for i in self.notes]
        return "-".join(names) + ' | LF: ' + str(self.lowest_fret) + \
            ' | HF: ' + str(self.highest_fret) + ' | G: ' + str(self.gap)

    def __str__(self):
        names = [i.name.center(5, '-') for i in self.notes]
        return "-".join(names) + ' | LF: ' + str(self.lowest_fret) + \
            ' | HF: ' + str(self.highest_fret) + ' | G: ' + str(self.gap)

    def display(self):
        new_guitar = Guitar(tuning = self.guitar.tuning,
                            frets = self.guitar.frets)
        new_guitar.filter_guitar(self.target)
        for i in range(len( self.guitar.tuning)):
            for j in range(self.guitar.frets + 1):
                if self.notes[i].fret == j:
                    new_guitar.filtered_notes[i][j] = self.notes[i]
                else:
                    new_guitar.filtered_notes[i][j] = NullNote(self.notes[i].name,
                                                               i, self.guitar)
        new_guitar.display('filtered')

    def downstrum(self, delay=150, sustain=4000):
        for note in self.notes:
            if note.name in ['NULL', 'MUTE']:
                continue
            note.play(sustain)
            time.sleep(delay/1000)

    def upstrum(self, delay=150, sustain=4000):
        for note in self.notes[::-1]:
            if note.name in ['NULL', 'MUTE']:
                continue
            note.play(sustain)
            time.sleep(delay/1000)

    def strum(self, sustain=4000):
        for note in self.notes[::-1]:
            if note.name in ['NULL', 'MUTE']:
                continue
            note.play(sustain)

    def bossa_strum(self, delay=150, sustain=4000):
        bass_note_plucked = False
        for note in self.notes:
            if note.name in ['NULL', 'MUTE']:
                continue
            note.play(sustain)
            if not bass_note_plucked:
                time.sleep(delay/1000)
                bass_note_plucked = True

    def mute_strings(self):
        for note in self.notes:
            if note.name in ['NULL', 'MUTE']:
                continue
            note.stop()


    def is_strummable(self):
        """1-2-3-4-5-6, 2-3-4-5-6, 3-4-5-6, 4-5-6 are considered "strummable"
        on a 6-string, since they can be picked without muting any strings."""
        strummable = True
        start_string = -1
        for i in range(0, len(self.notes)):
            if self.notes[i].name not in ['NULL', 'MUTE']:
                start_string = i
                break
        if start_string == -1:
            self.strummable = False
            return False
        for i in range(start_string + 1, len(self.notes)):
            if self.notes[i].name in ['NULL', 'MUTE']:
                strummable = False
        self.strummable = strummable
        return strummable

    def find_root(self):
        """Identifies and returns the root note."""
        indices = []
        for i in self.notes:
            if i.name in ['MUTE', 'NULL']:
                indices += [999]
            else:
                indices += [ALL_NOTES.index(i.name)]
        if len(indices) > 0:
            self.root = self.notes[indices.index(min(indices))]
            return self.root
        else:
            self.root = 'NA'
            return self.root

    def has_correct_root(self):
        root = self.find_root()
        if root == 'NA':
            self.correct_root = False
            return False
        elif self.target.root == root.type:
            self.correct_root = True
            return True
        else:
            self.correct_root = False
            return False

    def has_nth(self, interval):
        for i in self.notes:
            if i.type == getattr(self.target, interval):
                setattr(self, interval, True)
                return True
        setattr(self, interval, False)
        return False

    def is_bossa_nova(self, strict = False):
        """Bossa Nova here just means four strings at a time being plucked.
        strict will force 1 chunk and 3 chunks (which can be adjacent), essent-
        ially preventing 2-2 or 1-1-2 setups. """
        strings_binary = []
        for i in self.notes:
            if i.name in ['MUTE','NULL']:
                strings_binary += [0]
            else:
                strings_binary += [1]
        result = True if sum(strings_binary) == 4 else False
        if strict and result:
            valid_patterns = [
                [1,1,1,1,0,0],
                [1,0,1,1,1,0],
                [1,0,0,1,1,1],
                [0,1,1,1,1,0],
                [0,1,0,1,1,1],
                [0,0,1,1,1,1]
                ]
            result = True if strings_binary in valid_patterns else False
        self.bossa_nova = result
        return self.bossa_nova

    def has_small_enough_gaps(self, n):
        result = False if self.gap > n else True
        return result

    def in_fret_range(self, limits):
        if (self.lowest_fret >= limits[0] and
            self.gap + self.lowest_fret <= limits[1]):
            return True
        return False

    def fits_target(self, target):
        mapping = {
            'root': self.has_nth('root'),
            'third': self.has_nth('third'),
            'fifth': self.has_nth('fifth'),
            'seventh': self.has_nth('seventh'),
            'ninth': self.has_nth('ninth'),
            'thirteenth': self.has_nth('thirteenth'),
            'correct_root': self.has_correct_root(),
            'max_gap': self.has_small_enough_gaps(target.max_gap),
            'fret_limits': self.in_fret_range(target.fret_limits),
            'strummable': self.is_strummable(),
            'bossa': self.is_bossa_nova(),
            #'ref':True,
        }
        valid = True
        for attr, value in target.__dict__.items():
            if value is None:
                continue
            if attr in mapping:
                valid = valid if mapping[attr] else False
        return valid



class ChordTarget:
    def __init__(self, root, third = None, fifth = None, seventh = None,
                 ninth = None, eleventh = None, thirteenth = None,
                 correct_root = True, max_gap = MAX_GAP,
                 fret_limits = (0, FRETS), strummable = None, bossa = None):
        self.root = root
        self.third = third
        self.fifth = fifth
        self.seventh = seventh
        self.ninth = ninth
        self.eleventh = eleventh
        self.thirteenth = thirteenth
        self.correct_root = correct_root
        self.max_gap = max_gap
        self.fret_limits = fret_limits
        self.strummable = strummable
        self.bossa = bossa
        self.ref = [root, third, fifth, seventh, ninth, eleventh, thirteenth]
        self.ref_types = [i for i in [root, third, fifth, seventh, ninth,
                                      eleventh, thirteenth] if i != 'NA']
        self.dict = dict(zip(['root','third','fifth','seventh','ninth',
                              'eleventh','thirteenth'], self.ref))


class ChordPattern:
    """Transforms a string "Cmaj7/E" into something sensible."""
    def __init__(self, chord_string):
        self.root = chord_string[0]
        if chord_string[1] in ['#','b']:
            self.root += chord_string[1]


class Guitar:
    def __init__(self, tuning = TUNING, frets = FRETS, max_gap = MAX_GAP):
        self.tuning = tuning
        self.frets = frets
        self.notes = {}
        self.chords = []
        self.max_gap = max_gap
        for num, string in enumerate(tuning):
            self.notes[num] = [Note(string, num, self, True)]
            for fret in range (1, frets + 1):
                self.notes[num] += [self.notes[num][0].half_step(fret)]
    def __repr__(self):
        return 'Guitar object with tuning ' + str(self.tuning)

    def __str__(self):
        return 'Guitar object with tuning ' + str(self.tuning)

    def display(self, display_type='full'):
        attribute = 'notes' if display_type == 'full' else 'filtered_notes'
        fill, blank = '-', ' '
        full_str = '\n'
        for i in range(self.frets + 1):
            fret_row = blank + str(i) + ''.center(6 * 6 + 0, fill) + '\n'
            letter_row = '  '
            for j in range(len(self.tuning)):
                note = getattr(self, attribute)[j][i]
                if note.name == 'NULL':
                    letter_row += ''.center(6, blank)
                else:
                    letter_row += note.name.center(6, blank)
            letter_row += 2 * blank + '\n'
            full_str += letter_row
            full_str += fret_row
        print(full_str)

    def get_note(self, string, fret, return_nulls = True):
        note = self.notes[string][fret]
        if note.name == 'NULL' and return_nulls:
            return note
        elif note.name != 'NULL':
            return note

    def filter_guitar(self, target):
        self.filtered_notes = {}
        for i in self.notes:
            self.filtered_notes[i] = []
            for j in self.notes[i]:
                if j.type in target.ref_types:
                    self.filtered_notes[i] += [j]
                else:
                    self.filtered_notes[i] += [NullNote(j.name, j.string, self)]

    def remove_null_notes(self):
        self.minimal_notes = {}
        for i in self.filtered_notes:
            self.minimal_notes[i] = []
            for j in self.filtered_notes[i]:
                if j.name != "NULL":
                    self.minimal_notes[i] += [j]

    def find_gap(self, chord):
        """Note: chord here is just a list of notes, rather than a standard
        chord object (of class Chord). This is to avoid creating chords with
        fewer notes than strings on the instrument, incl. nulls/mutes."""
        fret_list = [note.fret for note in chord]
        fret_list_no_null = [x for x in fret_list if isinstance(x, int)]
        if not fret_list_no_null:
            return (0, 0)
        return (min(fret_list_no_null),
                max(fret_list_no_null) - min(fret_list_no_null))

    def generate_chord_candidates(self, target, chord_so_far = [], current_string = 0):
        """Warning: recursion!"""
        final = []
        for i in (self.minimal_notes[current_string] +
                  [MuteNote(current_string, self)]):
            lowest_fret, gap = self.find_gap(chord_so_far + [i])
            if gap > self.max_gap:
                continue
            if current_string == 5:
                final += [Chord(chord_so_far + [i], target, gap,
                                lowest_fret, self)]
            else:
                final += self.generate_chord_candidates(target, chord_so_far + [i],
                                              current_string + 1)
        return final

    def formalize_chords(self, target):
        chord_list = self.generate_chord_candidates(target)
        self.chords = chord_list

    def filter_chords(self, target):
        new_chords = []
        for chord in self.chords:
            if chord.fits_target(target):
                new_chords += [chord]
        self.chords = new_chords

    def generate_chords(self, target):
        self.filter_guitar(target)
        self.remove_null_notes()
        self.formalize_chords(target)
        self.filter_chords(target)




# Scripty STuff
def root_extractor(chord_string):
    if chord_string[1] in ['b','#']:
       root = chord_string[0:2]
       remainder = chord_string[2:]
    else:
       root = chord_string[0]
       remainder = chord_string[1:]
    return root, remainder

def chord_viewer(chords):
    for chord in chords:
        print(str(round(100 * chords.index(chord) / len(chords),2)) + "%")
        chord.display()
        entry = input()
        if entry != '' and entry[0] == 'q':
            break

a = Guitar()
target = ChordTarget('C', third='E', fifth='G', seventh = 'A#')
a.generate_chords(target)
chord = Chord([MuteNote(0, a), MuteNote(1, a), MuteNote(2, a), MuteNote(3, a),
              MuteNote(4, a), Note('C5', 5, a)],
              target = None, gap = None, lowest_fret = None, guitar = a)
