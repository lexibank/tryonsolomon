import sqlite3
from pathlib import Path

import attr
from clldutils.misc import slug
from pylexibank import Dataset as BaseDataset
from pylexibank import Language as BaseLanguage
from pylexibank import FormSpec


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
QUERY = """
SELECT language, gloss, lexeme FROM lexemes
ORDER BY language, gloss, lexeme
"""
# order by in the above query is just to get ordering consistent


@attr.s
class Language(BaseLanguage):
    Dialect = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "tryonsolomon"
    language_class = Language

    form_spec = FormSpec(
        brackets={"(": ")"},
        separators=";/,",
        missing_data=('?', '-', '', ''),
        strip_inside_brackets=True
    )
    
    def cmd_download(self, args):
        pass

    def cmd_makecldf(self, args):
        conn = sqlite3.connect((self.raw_dir / "tryon.db").as_posix())
        cursor = conn.cursor()
        cursor.execute(QUERY)
        
        args.writer.add_sources()
        languages = args.writer.add_languages(lookup_factory="Name")
        concepts = args.writer.add_concepts(
            id_factory=lambda c: c.id.split('-')[-1] + '_' + slug(c.english),
            lookup_factory="Name"
        )
        
        for lang, param, value in cursor.fetchall():
            if value:
                args.writer.add_forms_from_value(
                    Language_ID=languages[lang],
                    Parameter_ID=concepts[param],
                    Value=self.lexemes.get(value, value).strip(),
                    Source=['Tryon1983'],
                )
        conn.close()
