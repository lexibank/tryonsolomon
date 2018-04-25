# coding=utf-8
from __future__ import unicode_literals, print_function
import re
import sqlite3

from clldutils.path import Path
from clldutils.misc import slug

from pylexibank.dataset import Metadata
from pylexibank.dataset import Dataset as BaseDataset

IS_DIGIT = re.compile(r"""\([12]\)""")
QUERY = """
SELECT language, gloss, lexeme FROM lexemes ORDER BY language, gloss, lexeme
"""
# order by in the above query is just to get ordering consistent so we can use
# the sequence position as an id

# DATABASE SCHEMA:
# 
# CREATE TABLE lexemes (
#   language TEXT,   -- Language name
#   gloss TEXT,      -- English gloss
#   lexeme TEXT,     -- Unicode lexical form
#   location TEXT,   -- Location code for language
#   note TEXT,       -- Footnote
#   page INTEGER     -- Page number in Tryon and Hackman
# );


class Dataset(BaseDataset):
    dir = Path(__file__).parent

    def cmd_download(self, **kw):
        pass

    def cmd_install(self, **kw):
        concept_map = {
            c.english: c.concepticon_id for c in self.conceptlist.concepts.values()}

        source = self.raw.read_bib()[0]
        languages = {l['NAME']: l for l in self.languages}

        conn = sqlite3.connect(self.raw.posix('tryon.db'))
        cursor = conn.cursor()
        cursor.execute(QUERY)

        with self.cldf as ds:
            ds.add_sources(source)
            for i, (lang, param, value) in enumerate(cursor.fetchall(), 1):
                # rename languages with (1) and (2) to better dialect names
                lname = lang
                if languages[lang]['DIALECT']:
                    lname = IS_DIGIT.sub("(%s)" % languages[lang]['DIALECT'], lang)

                ds.add_language(
                    ID=slug(lang),
                    Name=lname,
                    ISO639P3code=languages[lang]['ISO'],
                    Glottocode=languages[lang]['GLOTTOCODE'])
                ds.add_concept(
                    ID=slug(param),
                    Name=param,
                    Concepticon_ID=concept_map[param])

                if value:
                    ds.add_lexemes(
                        Language_ID=slug(lang),
                        Parameter_ID=slug(param),
                        Value=value,
                        Source=[source.id])
        conn.close()
