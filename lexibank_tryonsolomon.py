import re
import sqlite3

import attr
from clldutils.misc import slug
from clldutils.path import Path
from pylexibank.dataset import Dataset as BaseDataset, Language as BaseLanguage

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


@attr.s
class Language(BaseLanguage):
    Dialect = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "tryonsolomon"
    language_class = Language

    def cmd_download(self, **kw):
        pass

    def cmd_install(self, **kw):
        source = self.raw.read_bib()[0]

        conn = sqlite3.connect(self.raw.posix("tryon.db"))
        cursor = conn.cursor()
        cursor.execute(QUERY)

        with self.cldf as ds:
            ds.add_sources(source)
            ds.add_concepts(id_factory=lambda c: slug(c.label))
            ds.add_languages(id_factory=lambda l: slug(l["Name"]))
            for i, (lang, param, value) in enumerate(cursor.fetchall(), 1):
                if value:
                    ds.add_lexemes(
                        Language_ID=slug(lang),
                        Parameter_ID=slug(param),
                        Value=value,
                        Source=[source.id],
                    )
        conn.close()
