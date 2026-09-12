import re
from pathlib import Path
from stop_words import get_stop_words

STOP_WORDS = set(get_stop_words("english")) | {"user"}

class MarkdownMemoryStore:
    def __init__(self, filepath: str | Path) -> None:
        self.filepath = Path(filepath)

    def append(self, fact: str) -> None:
        """
        adds one single-line fact to markdown file
        """
        fact = fact.strip().replace("\n", " ")

        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write("- " + fact + "\n")

    def get_facts(self) -> list[str]:
        """
        returns list of facts as strings, each string being a single-line fact
        """
        facts = []

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.removeprefix("- ").strip()
                    facts.append(line)
        except FileNotFoundError:
            return []

        return facts

    def keyword_search(self, query: str) -> list[str]:
        """
        returns facts that share 1+ non-stopword token with query

        ordered (decreasing) by number of overlapping tokens
        """
        facts = self.get_facts()
        query_tokens = self._tokenize(query)

        facts_scored_by_keywords = [] # list of (fact, score) tuples

        for fact in facts:
            fact_tokens = self._tokenize(fact)
            shared_tokens = fact_tokens & query_tokens
            if len(shared_tokens) > 0:
                facts_scored_by_keywords.append((fact, len(shared_tokens)))

        sorted_facts = sorted(facts_scored_by_keywords, key=lambda x: x[1], reverse=True)
        facts_with_keywords = [fact for fact, score in sorted_facts]

        return facts_with_keywords


    def stats(self) -> dict:
        """
        returns basic size/health info about markdown store (num_facts, file_size, estimated_tokens)
        """
        try:
            file_size = self.filepath.stat().st_size
        except FileNotFoundError:
            file_size = 0

        facts = self.get_facts()
        num_facts = len(facts)
        total_chars = sum(len(fact) for fact in facts)
        estimated_tokens = total_chars // 4

        return {
            "num_facts": num_facts,
            "file_size": file_size,
            "estimated_tokens": estimated_tokens
        }

    def _tokenize(self, text: str) -> set[str]:
        """
        helper for keyword_search that processes fact and removes stopwords
        """
        text = text.lower()
        text = re.sub(r"[^\w\s']", " ", text) # replaces non-word chars, non-ws chars, and non apostrophes with spaces
        tokens = text.split()
        tokens = {t for t in tokens if t not in STOP_WORDS} # removes stop words from token list and creates a set
        
        return tokens
