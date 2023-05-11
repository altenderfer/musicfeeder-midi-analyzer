![Mindfeeder 2 Logo](https://mindfeederllc.com/musicfeeder.png)

# Musicfeeder - MIDI Analyzer

MusicFeeder is a MIDI file analyzer specifically designed for extracting detailed musical structures within MIDI files. It's a fundamental part of a broader project aiming at training a large language model (LLM) on musical chord progressions and other relevant musical characteristics. The tool uses the music21 toolkit, a Python-based framework for computer-aided musicology, to perform a comprehensive analysis of MIDI files.

## Installation
1. Install Python 3.7 or higher.

2. Clone this repository:

```
git clone https://github.com/altenderfer/musicfeeder-midi-analyzer.git
cd musicfeeder-midi-analyzer
```
3. Install the required Python libraries:
```
pip install music21
```

# Usage

The MIDI Analyzer can be used via the command line with several arguments.

```
python main.py -i <input_directory> -o <output_file> -r <resolution>
```

### Arguments:
```
-i, --input_dir : Input directory containing MIDI files (default: current directory)
-o, --output_file : Output JSON file (default: output.json)
-r, --resolution : Resolution for rounding beat offsets (default: 4 for quarter notes)
```

## Output

The output is a structured JSON file. Each entry in the JSON file corresponds to an analyzed MIDI file and includes:

- song_name: The name of the MIDI file.
- key: The overall key of the song.
- tempo: The overall tempo of the song.
- score_analysis: A structured analysis of the song, including key changes, time signature changes, and roman numeral analysis corresponding to chord progressions.

See below example:

```
[
  {
    "song_name": "Beethoven - Moonlight Sonata",
    "key": "C#Minor",
    "tempo": 50.0,
    "score_analysis": {
      "0.0": {
        "time_signature": "4/4"
      },
      "9.75": {
        "key": "C#Minor",
        "roman_numeral": "vi"
      },
      "10.5": {
        "key": "C#Minor",
        "roman_numeral": "iv"
      },
      "29.75": {
        "key": "C#Minor",
        "roman_numeral": "vii"
      },
      "31.75": {
        "key": "C#Minor",
        "roman_numeral": "vii"
      },
      "32.25": {
        "key": "C#Minor",
        "roman_numeral": "iii"
      },
      "32.75": {
        "key": "C#Minor",
        "roman_numeral": "v"
      }
    }
  }
]
```

This output is intended for further processing and training of large language models for music analysis and composition.

## Contribution

Contributions are welcome! Feel free to submit a Pull Request.

## FAQ

### What does this program do?

MusicFeeder MIDI Analyzer is a tool designed to extract a structured analysis from MIDI files. This includes information about key changes, tempo changes, time signatures, and Roman numeral analysis. The extracted data is intended to be used for training a large language model on musical chord progressions.

### How does the program handle percussion elements?

During the analysis, percussion parts and percussion notes are skipped as they don't contribute to the harmonic analysis which is the primary focus of this tool.

### How does the "resolution for rounding beat offsets" work?

The resolution for rounding beat offsets determines the granularity of temporal analysis. For example, a resolution of 4 (quarter notes) means events are aligned to the nearest quarter note beat.

### What if there are no tempo indications in the MIDI file?

If there are no explicit tempo markings in the MIDI file, the program will assume a default tempo of 120 BPM.

### How do I interpret the Roman numeral analysis?

The Roman numeral analysis is a representation of the chords in the song relative to the current key. For example, in the key of C major, a C major chord is represented as I, a D minor chord as ii, and so on. This representation allows for analysis of chord progressions independent of the key.


# Credits
Developed by Kyle Altenderfer ```altenderfer@gmail.com```

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

