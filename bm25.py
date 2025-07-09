import inspect
if not hasattr(inspect, "getargspec"):
    def getargspec(func):
        spec = inspect.getfullargspec(func)
        return spec.args, spec.varargs, spec.varkw, spec.defaults
    inspect.getargspec = getargspec

try:
    import pkg_resources
except ImportError:
    raise ImportError(
        "Требуется pkg_resources (из setuptools). "
        "Установите: pip install setuptools"
    )

import math
import re
from collections import Counter, defaultdict

import pymorphy2
from stop_words import get_stop_words


morph = pymorphy2.MorphAnalyzer()
russian_stopwords = set(get_stop_words("ru"))

def preprocess(text: str) -> list[str]:
    """
    1. Приводим в нижний регистр
    2. Регекспом выдираем только русские слова
    3. Лемматизируем pymorphy2
    4. Удаляем стоп‑слова
    """
    tokens = re.findall(r"[а-яё]+", text.lower())
    lemmas = [morph.parse(tok)[0].normal_form for tok in tokens]
    return [lemma for lemma in lemmas if lemma not in russian_stopwords]

class BM25:
    def __init__(self, corpus: list[str], k1: float=1.5, b: float=0.75):
        """
        corpus — список документов (строк).
        k1, b   — гиперпараметры BM25.
        """
        self.k1 = k1
        self.b  = b

        self.docs     = [preprocess(doc) for doc in corpus]
        self.doc_lens = [len(d) for d in self.docs]
        self.avgdl    = sum(self.doc_lens) / len(self.doc_lens)
        self.N        = len(self.docs)

        self.df = defaultdict(int)
        self.f  = []
        for doc in self.docs:
            freqs = Counter(doc)
            self.f.append(freqs)
            for term in freqs:
                self.df[term] += 1

        # Вычисляем IDF
        self.idf = {
            term: math.log((self.N - df + 0.5)/(df + 0.5) + 1)
            for term, df in self.df.items()
        }

    def score(self, query: str, idx: int) -> float:
        """
        BM25‑скор документа idx по запросу query.
        """
        terms = preprocess(query)
        score = 0.0
        freqs = self.f[idx]
        dl = self.doc_lens[idx]

        for term in terms:
            if term not in freqs:
                continue
            tf = freqs[term]
            idf = self.idf.get(term, 0.0)
            denom = tf + self.k1*(1 - self.b + self.b*dl/self.avgdl)
            score += idf * tf*(self.k1 + 1)/denom

        return score

    def rank(self, query: str) -> list[tuple[int, float]]:
        """
        Возвращает [(idx, score), …] всех документов, 
        отсортированный по убыванию score.
        """
        scores = [(i, self.score(query, i)) for i in range(self.N)]
        return sorted(scores, key=lambda x: x[1], reverse=True)


if __name__ == "__main__":
    docs = [
        "Кошка сидит на окне и смотрит на улицу.",
        "Собака гуляет по парку и лает на птиц.",
        "На улице весна, солнце светит и птицы поют."
    ]

    bm25 = BM25(docs)
    query = "кошка на улице"
    results = bm25.rank(query)

    print(f"Запрос: «{query}»\n")
    for idx, score in results:
        print(f"{idx} (score={score:.3f}): {docs[idx]}")
