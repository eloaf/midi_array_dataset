import os
import sys

import numpy as np

from scipy.sparse import csc_matrix
from scipy.sparse import save_npz
from mido import MidiFile
from glob import glob

def compute_note_positions(mid, verbose=False):
    """
    Each message in a MIDI file has a delta time, which tells how many ticks have passed since the last message.
    The length of a tick is defined in ticks per beat.
    This value is stored as ticks_per_beat in MidiFile objects and remains fixed throughout the song.
    """
    notes = []

    if verbose:
        print(len(mid.tracks))

    for i, track in enumerate(mid.tracks):
        current_tick = 0

        if verbose:
            print('Track {}: {}'.format(i, track.name))

        for msg in track:
            msg_data = msg.dict()
            event_type, time, note = msg_data['type'], msg_data['time'], msg_data.get('note', -1)
            current_tick += time

            if verbose:
                print("Event: {:10} Time: {:4}   AbsTime: {:6}  Note: {:3}".format(event_type, time, current_tick, note))

            if event_type.startswith('note'):
                notes.append((event_type, current_tick, note))


    # do we need to sort the notes if there are different channels?
    # notes = list(sorted(notes, key=lambda x: x[1]))
    return notes

def get_note_array(notes):
    """
    Given a list of midi notes (tuple of (event, current tick, note no.)),
    construct an array analogous to "piano roll representation"
    """
    max_tick = max([x[1] for x in notes]) + 1
    X = np.zeros((max_tick, 128))
    X_noteon  = np.zeros((max_tick, 128))
    X_noteoff = np.zeros((max_tick, 128))

    for event, tick, note in notes:

        if event == 'note_on':
            X[tick:, note] = 1
            X_noteon[tick, note] = 1

        if event == 'note_off':
            X[tick:, note] = 0
            X_noteoff[tick, note] = 1

    return X, X_noteon, X_noteoff

def note_array_to_midi(note_array):
    """
    Given a piano roll representation, reconstruct a midi file.
    """
    # TODO
    return

def midi_files_to_note_arrays(source_path, dest_path):
    """
    Reads all the .mid in the source_path, builds note arrays and
    saves them as sparse arrays in the dest_path
    """

    midi_files = glob(source_path + '/*.mid')

    for i, f in enumerate(midi_files):

        if i % 100 == 0:
            print(i)

        fname = f.split('/')[-1].split('.')[0]
        fname_array = fname + '.npz'
        try:
            mid = MidiFile(f)
            array, _, _ = get_note_array(compute_note_positions(mid))
            sparse_array = csc_matrix(array)
            #np.save(os.path.join(dest_path, fname_array), array)
            save_npz(os.path.join(dest_path, fname_array), sparse_array)
        except:
            print('Could not process %s' % f)

if __name__ == "__main__":

    source, dest = sys.argv[1:]

    if not os.path.exists(dest):
        os.makedirs(dest)

    midi_files_to_note_arrays(source, dest)
