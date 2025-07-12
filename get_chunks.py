import pandas as pd
from typing import List, Dict



def fuzzy_ranker(
    series: pd.Series,
    question: str,
    top_n: int = 3,
    min_score: int = 0
) -> List[Dict]:
    from rapidfuzz import fuzz, process
    texts = series.astype(str).tolist()
    candidates = process.extract(
        question,
        texts,
        scorer=fuzz.token_set_ratio,
        limit=top_n
    )
    results = []
    for val, score, idx in candidates:
        if score >= min_score:
            results.append({'val': val, 'score': score, 'index': idx})
    return results



def bm25_ranker(
    series: pd.Series,
    question: str,
    top_n: int = 3,
    min_score: float = 0.0
) -> List[Dict]:
    from bm25 import BM25 
    
    texts = series.astype(str).tolist()
    bm25_index = BM25(texts)
    ranked = bm25_index.rank(question) 
    
    results = []
    for idx, score in ranked[:top_n]:
        if score >= min_score:
            results.append({'val': texts[idx], 'score': score, 'index': idx})
    return results



def embedding_ranker(
    series: pd.Series,
    question: str,
    model,
    tokenizer,
    device,
    pooling,
    top_n: int = 3,
    min_score: float = 0.0
) -> list[dict]:
    import numpy as np
    from model_util import get_embeddings, device, model, tokenizer, pooling
    texts = series.astype(str).tolist()
    
    chunk_embs = get_embeddings(texts, model, tokenizer, device, pooling)  
    query_emb  = get_embeddings([question], model, tokenizer, device, pooling) 
    
    chunk_embs_np = chunk_embs.cpu().numpy()
    query_emb_np  = query_emb.cpu().numpy()[0]
    
    chunk_norms = np.linalg.norm(chunk_embs_np, axis=1)
    query_norm  = np.linalg.norm(query_emb_np)
    sims = (chunk_embs_np @ query_emb_np) / (chunk_norms * query_norm + 1e-8)
    
    scored = [(i, float(s)) for i, s in enumerate(sims) if s >= min_score]
    scored.sort(key=lambda x: x[1], reverse=True)

    top = scored[:top_n]
    return [
        {'val': texts[idx], 'score': score, 'index': idx}
        for idx, score in top
    ]



def find_top_chunks_for_series(
    series: pd.Series,
    question: str,
    ranker,
    top_n: int = 3,
    min_score = 0
) -> List[Dict]:
    
    return ranker(series, question, top_n=top_n, min_score=min_score)


def get_chunks(
    conn,
    table_name: str,
    question: str,
    cols: str = '*',
    where: str | None = None,
    mode: str = "bm25",  
    top_n: int = 3,
    min_score = 0
) -> Dict[str, List[Dict]]:
    
    if mode == "emb":
        ranker = lambda series, q, top_n, min_score: embedding_ranker(
            series, q,
            model, tokenizer, device, pooling,
            top_n=top_n,
            min_score=min_score
        )
    elif mode == "fuzzy":
        ranker = fuzzy_ranker
    else:
        ranker = bm25_ranker


    query = f'SELECT {cols} FROM "{table_name}"'
    if where:
        query += ' ' + where
    df = pd.read_sql_query(query, conn)

    result: Dict[str, List[Dict]] = {}
    for col in df.columns:
        result[col] = find_top_chunks_for_series(
            df[col],
            question,
            ranker=ranker,
            top_n=top_n,
            min_score=min_score
        )

    return result



if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    import psycopg2

    load_dotenv()

    db_params = {
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT")),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASS")
    }

    conn = psycopg2.connect(**db_params)


    cols = '"направление", "код", "профиль", "факультет", "описание"'
    table_name = "specialties"
    question = "Направление прикладная физика"
    where_query = None
    ranker_mode = "bert"

    print(get_chunks(conn, table_name, question, cols, where_query, ranker_mode))