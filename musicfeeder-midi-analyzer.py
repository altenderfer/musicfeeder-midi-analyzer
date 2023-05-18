import os
import json
import argparse
import copy
from music21 import converter, midi, roman, tempo, instrument, analysis, chord, pitch, percussion, note, key

class CustomKrumhanslSchmuckler(analysis.discrete.KrumhanslSchmuckler):
    def __init__(self):
        super().__init__()

    def _getPitchClassDistribution(self, sStream):
        pcDist = [0] * 12
        print("Custom Function")
        for n in sStream.recurse().notes:
            length = n.quarterLength

            if isinstance(n, percussion.PercussionChord):
                print("Skip percussion chords")
                continue  # Skip percussion chords

            if is_percussion_element(n):
                print("Skip percussion notes")
                continue  # Skip percussion notes

            if isinstance(n, note.Note):
                try:
                    pcDist[n.pitch.pitchClass] += length
                except AttributeError:
                    pass
            elif isinstance(n, chord.Chord):
                for pitch_obj in n.pitches:
                    try:
                        pcDist[pitch_obj.pitchClass] += length
                    except AttributeError:
                        pass

        return pcDist


def get_tempo_changes(score):
    tempo_changes = []
    for mark in score.recurse().getElementsByClass(tempo.MetronomeMark):
        tempo_changes.append((mark.offset, mark.number))
    return tempo_changes


def get_elapsed_beats(offset, tempo_changes):
    elapsed_beats = 0
    previous_offset = 0
    previous_bpm = 120  # Default to 120 BPM
    for change_offset, bpm in tempo_changes:
        if change_offset > offset:
            break
        elapsed_beats += (change_offset - previous_offset) * (previous_bpm / 60)
        previous_offset = change_offset
        previous_bpm = bpm
    elapsed_beats += (offset - previous_offset) * (previous_bpm / 60)
    return elapsed_beats


def round_offset(offset, tempo_changes, resolution=8):
    elapsed_beats = get_elapsed_beats(offset, tempo_changes)
    return round(elapsed_beats * resolution) / resolution


def extract_roman_numerals(part, key_changes, tempo_changes, resolution):
    roman_numerals = {}
    rn = roman.romanNumeralFromChord
    for measure in part.getElementsByClass("Measure"):
        for chord in measure.getElementsByClass("Chord"):
            current_key = part.analyze('key')
            if chord.offset in key_changes:
                current_key = key_changes[chord.offset]
                current_key = key.Key(current_key)
            rn_obj = rn(chord, current_key)
            rn_key = current_key.tonic.name + current_key.mode.capitalize()
            roman_numerals[round_offset(chord.offset, tempo_changes, resolution)] = {"key": rn_key, "roman_numeral": rn_obj.figure}
    return roman_numerals


def is_percussion_element(element):
    if isinstance(element, note.Note):
        if element.pitch.pitchClass == 10:  # Check if the note is a percussion note
            return True
    elif isinstance(element, note.Unpitched):
        return True
    return False


def is_percussion_part(part):
    for inst in part.recurse().getElementsByClass(instrument.Instrument):
        if isinstance(inst, instrument.Percussion):
            return True
    return False


def extract_key_changes(part, tempo_changes, resolution):
    print("Extracting key changes")
    key_changes = {}
    prev_key = None
    for k in part.getElementsByClass("Key"):
        if prev_key is None or prev_key != str(k):
            key_changes[round_offset(k.offset, tempo_changes, resolution)] = str(k)
    return key_changes


def extract_time_signatures(part, tempo_changes):
    time_signatures = {}
    prev_ts = None
    for ts in part.getTimeSignatures():
        if prev_ts is None or prev_ts != f"{ts.numerator}/{ts.denominator}":
            time_signatures[round_offset(ts.offset, tempo_changes)] = f"{ts.numerator}/{ts.denominator}"
            prev_ts = f"{ts.numerator}/{ts.denominator}"
    return time_signatures


def process_midi_file(filename, resolution):
    print(f"Processing MIDI file: {filename}")
    score = converter.parse(filename)

    # Make a deep copy of the score to create the non-percussion score
    non_percussion_score = copy.deepcopy(score)

    # Remove percussion parts from non_percussion_score
    for part in non_percussion_score.parts:
        if is_percussion_part(part):
            non_percussion_score.remove(part)

    # Get tempo changes
    print("Extracting tempo changes from the score")
    tempo_changes = get_tempo_changes(score)

    key_changes = {}
    roman_numerals = {}
    time_signatures = {}
    for part in score.parts:
        if is_percussion_part(part):
            continue  # Skip percussion parts

        print(f"Extracting key changes for part {part.id}")
        key_changes_part = extract_key_changes(part, tempo_changes, resolution)
        print(f"Extracting time signatures for part {part.id}")
        time_signatures_part = extract_time_signatures(part, tempo_changes)

        key_changes = {**key_changes, **key_changes_part}
        time_signatures = {**time_signatures, **time_signatures_part}

        print(f"Extracting roman numerals for part {part.id}")
        roman_numerals_part = extract_roman_numerals(part, key_changes, tempo_changes, resolution)
        roman_numerals = {**roman_numerals, **roman_numerals_part}

    score_analysis = {}
    all_changes = sorted(list(set(list(key_changes.keys()) + list(time_signatures.keys()))))

    # Initialize score_analysis with roman numerals
    score_analysis = roman_numerals.copy()

    # Update score_analysis with key and time signature changes
    for change in all_changes:
        if change in key_changes:
            if change in score_analysis:
                score_analysis[change].update({"key_change": key_changes[change]})
            else:
                score_analysis[change] = {"key_change": key_changes[change]}
        if change in time_signatures:
            if change in score_analysis:
                score_analysis[change].update({"time_signature": time_signatures[change]})
            else:
                score_analysis[change] = {"time_signature": time_signatures[change]}

    score_analysis = {float(k): v for k, v in sorted(score_analysis.items())}


    song_name = os.path.splitext(os.path.basename(filename))[0]

    krumhansl = CustomKrumhanslSchmuckler()
    key_obj = krumhansl.getSolution(non_percussion_score)

    # Extract tempo BPM
    tempo_objects = score.parts[0].recurse().getElementsByClass(tempo.TempoIndication)
    if len(tempo_objects) > 0:
        tempo_bpm = tempo_objects[0].getQuarterBPM()
    else:
        tempo_bpm = None

    # Convert the key_obj to a dictionary
    key_obj_str = key_obj.tonic.name + key_obj.mode.capitalize()

    return {
        "song_name": song_name,
        "key": key_obj_str,
        "tempo": tempo_bpm,
        "score_analysis": score_analysis,
    }


def main():
    parser = argparse.ArgumentParser(description="Analyze MIDI files and output Roman numeral analysis")
    parser.add_argument("-i", "--input_dir", default=".", help="Input directory containing MIDI files (default: current directory)")
    parser.add_argument("-o", "--output_file", default="output.json", help="Output JSON file (default: output.json)")
    parser.add_argument("-r", "--resolution", type=int, default=4, help="Resolution for rounding beat offsets (default: 4 for quarter notes)")

    args = parser.parse_args()

    midi_folder = args.input_dir
    output_file = args.output_file

    all_midi_analysis = []

    for filename in os.listdir(midi_folder):
        print(f"Processing file: {filename}")
        if filename.endswith(".mid"):
            input_file_path = os.path.join(midi_folder, filename)
            analysis = process_midi_file(input_file_path, args.resolution)
            all_midi_analysis.append(analysis)

    with open(output_file, "w") as outfile:
        json.dump(all_midi_analysis, outfile, indent=2, default=str)

if __name__ == "__main__":
    main()
