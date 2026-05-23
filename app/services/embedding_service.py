from __future__ import annotations

import pickle
import numpy as np
from sqlalchemy.orm import Session

_model = None
_cache: dict[int, np.ndarray] = {}

MODEL_NAME = "jhgan/ko-sroberta-multitask"


def load_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def build_corpus_text(
    title: str,
    description: str | None,
    tags: list[str] | None,
    location: str | None,
) -> str:
    parts = [title]
    if description:
        parts.append(description)
    if tags:
        parts.append(" ".join(tags))
    if location:
        parts.append(location)
    return " ".join(parts)


def embed_text(text: str) -> np.ndarray:
    model = load_model()
    vector = model.encode(text, convert_to_numpy=True)
    return vector.astype(np.float32)


def cosine_similarity(a: np.ndarray, b_matrix: np.ndarray) -> np.ndarray:
    a_norm = a / (np.linalg.norm(a) + 1e-10)
    norms = np.linalg.norm(b_matrix, axis=1, keepdims=True) + 1e-10
    b_norms = b_matrix / norms
    return b_norms @ a_norm


def index_video(video_id: int, db: Session) -> None:
    try:
        from app.models.video import Video
        from app.models.video_embedding import VideoEmbedding

        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            return

        tag_names = [t.name for t in video.tags] if video.tags else []
        corpus = build_corpus_text(
            title=video.title,
            description=video.description,
            tags=tag_names,
            location=video.filmed_location,
        )
        vector = embed_text(corpus)

        existing = db.query(VideoEmbedding).filter(VideoEmbedding.video_id == video_id).first()
        blob = pickle.dumps(vector)
        if existing:
            existing.embedding = blob
        else:
            emb = VideoEmbedding(video_id=video_id, embedding=blob)
            db.add(emb)
        db.commit()

        _cache[video_id] = vector
    except Exception as e:
        print(f"[embedding_service] index_video error for video_id={video_id}: {e}")


def load_cache(db: Session) -> None:
    try:
        from app.models.video_embedding import VideoEmbedding

        rows = db.query(VideoEmbedding).all()
        for row in rows:
            try:
                vector = pickle.loads(row.embedding)
                _cache[row.video_id] = vector
            except Exception as e:
                print(f"[embedding_service] load_cache skip video_id={row.video_id}: {e}")
        print(f"[embedding_service] loaded {len(_cache)} embeddings into cache")
    except Exception as e:
        print(f"[embedding_service] load_cache error: {e}")


def search_videos(query: str, db: Session, top_k: int = 10) -> list[dict]:
    if not _cache:
        return []

    query_vec = embed_text(query)

    video_ids = list(_cache.keys())
    matrix = np.stack([_cache[vid] for vid in video_ids], axis=0)

    scores = cosine_similarity(query_vec, matrix)

    ranked = sorted(zip(video_ids, scores.tolist()), key=lambda x: x[1], reverse=True)
    top = ranked[:top_k]

    from app.models.video import Video

    results = []
    for vid_id, score in top:
        video = db.query(Video).filter(Video.id == vid_id).first()
        if video:
            results.append({
                "id": video.id,
                "user_id": video.user_id,
                "title": video.title,
                "thumbnail_url": video.thumbnail_url,
                "views": video.views,
                "created_at": video.created_at,
                "score": float(score),
            })
    return results


def remove_from_cache(video_id: int) -> None:
    _cache.pop(video_id, None)
