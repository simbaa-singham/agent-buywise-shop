-- agent database: RAG knowledge chunks (ADR-011, ADR-034). Moved out of buywise_agent/rag/ingest.py (ADR-046).
-- Needs the pgvector extension, created once by the admin in buywise-db/cluster/01-databases.sh (the agent user cannot).
-- IF NOT EXISTS: databases that already have rag.chunks from the old ingest code are left unchanged.
CREATE SCHEMA IF NOT EXISTS rag;

CREATE TABLE IF NOT EXISTS rag.chunks (
    id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_id   text   NOT NULL,
    title         text   NOT NULL,
    doc_type      text,
    location      text,
    content       text   NOT NULL,
    embedding     vector(1024) NOT NULL,                -- bge-m3 embedding (1024 numbers)
    model_version text   NOT NULL                       -- which embedding model made it
);
-- HNSW index: fast nearest-neighbour search by cosine distance (the <=> operator)
CREATE INDEX IF NOT EXISTS chunks_embedding_idx ON rag.chunks USING hnsw (embedding vector_cosine_ops);
