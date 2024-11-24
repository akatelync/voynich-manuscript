import re
from collections import defaultdict


def tokenize(data, word_limit=None):
    index_str = defaultdict(str)
    index_arr = defaultdict(list)

    with open(data) as file:
        for line in file.read().splitlines():
            # pull out takahashi lines
            m = re.match(r'^<(f.*?)\..*;H> +(\S.*)$', line)
            if not m:
                continue

            transcription = m.group(2)
            pg = str(m.group(1))

            # ignore entire line if it has a {&NNN} or {&.} code
            if re.search(r'\{&(\d|\.)+\}', transcription):
                continue

            # remove extraneous chracters ! and %
            s = transcription.replace("!", "").replace("%", "")

            # delete all end of line {comments} (between one and three observed)
            # ...with optional line terminator
            # allow 0 occurences to remove end-of-line markers (- or =)
            s = re.sub(r'([-=]?\{[^\{\}]+?\}){0,3}[-=]?\s*$', "", s)

            # delete start of line {comments} (single or double)
            s = re.sub(r'^(\{[^\{\}]+?\}){1,2}', "", s)

            # simplification: tags preceeded by -= are word breaks
            s = re.sub(r'[-=]\{[^\{\}]+?\}', '.', s)

            # these tags are nulls
            # plant is a null in one case where it is just {plant}
            # otherwise (above) it is a word break
            # s = re.sub(r'\{(fold|crease|blot|&\w.?|plant)\}', "", s)
            # simplification: remaining tags in curly brackets
            s = re.sub(r'\{[^\{\}]+?\}', '', s)

            # special case .{\} is still a word break
            s = re.sub(r'\.\{\\\}', ".", s)

            # split on word boundaries
            # exclude null words ('')
            words = [str(w) for w in s.split(".") if w]
            if word_limit:
                words = words[:word_limit]

            # Concatenate words into a paragraph and store
            paragraph = ' '.join(words).lstrip()
            index_str[pg] += paragraph
            index_arr[pg] += words

    return index_str, index_arr


def tokenize_bible_en(data):
    # Initialize dictionaries to store results
    verse_text = defaultdict(str)
    verse_words = defaultdict(list)

    verse_pattern = r'(\d{2}:\d{3}:\d{3})\s+(.*)'

    current_verse = None
    current_text = []

    with open(data) as file:
        for line in file.read().splitlines():
            # Check if line starts with a verse number
            verse_match = re.match(verse_pattern, line)

            if verse_match:
                # If we were processing a previous verse, save it
                if current_verse and current_text:
                    verse_text[current_verse] = ' '.join(current_text)
                    verse_words[current_verse] = ' '.join(current_text).split()

                # Start new verse
                current_verse = verse_match.group(1)
                current_text = [verse_match.group(2).strip()]
            else:
                # This is a continuation of the previous verse
                if current_verse and line.strip():
                    current_text.append(line.strip())

        # Don't forget to save the last verse
        if current_verse and current_text:
            verse_text[current_verse] = ' '.join(current_text)
            verse_words[current_verse] = ' '.join(current_text).split()

    return verse_text, verse_words


def tokenize_bible_sp(data):
    verse_text = defaultdict(str)
    verse_words = defaultdict(list)
    verse_annotations = defaultdict(list)

    with open(data) as file:
        for line in file.read().splitlines():
            # Match verse numbers and text, including bracketed annotations
            # Matches formats like "1 No [1] principio..." or simple "1 En el principio..."
            match = re.match(r'(\d+)\s+(.+)', line)
            if match:
                verse_num = match.group(1)
                content = match.group(2)

                # Extract bracketed annotations
                annotations = re.findall(r'\[(\d+)\]', content)
                verse_annotations[verse_num] = annotations

                # Clean the text by removing bracketed numbers and underscores
                # Remove [1], [2], etc.
                clean_text = re.sub(r'\[\d+\]', '', content)
                # Remove underscores around words
                clean_text = re.sub(r'_(\w+)_', r'\1', clean_text)
                clean_text = clean_text.strip()

                # Store the full text
                verse_text[verse_num] = clean_text

                # Split into words and store as array
                words = clean_text.split()
                verse_words[verse_num] = words

    return verse_text, verse_words
