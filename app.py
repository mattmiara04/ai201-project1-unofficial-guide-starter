import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

import gradio as gr
import chromadb
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer


DOCUMENTS_DIR = Path("documents")
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "unofficial_csi_cs_guide"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 4


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def extract_metadata(text: str, filename: str) -> Dict:
    professor_match = re.search(r"Professor:\s*(.+)", text)
    url_match = re.search(r"URL:\s*(.+)", text)

    professor = professor_match.group(1).strip() if professor_match else "Unknown"
    url = url_match.group(1).strip() if url_match else ""

    return {
        "source": filename,
        "professor": professor,
        "url": url,
    }


def split_long_text(text: str, chunk_size: int = 850, overlap: int = 150) -> List[str]:
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap

    return chunks


def split_into_review_chunks(text: str, metadata: Dict) -> List[Dict]:
    cleaned = clean_text(text)
    parts = re.split(r"\nReview\s+\d+:\s*\n", cleaned)

    chunks = []
    header = parts[0].strip()

    for i, part in enumerate(parts[1:], start=1):
        part = part.strip()

        if not part or "Paste review text here" in part:
            continue

        chunk_text = f"{header}\n\nReview {i}:\n{part}"
        chunk_text = clean_text(chunk_text)

        if len(chunk_text) > 1000:
            subchunks = split_long_text(chunk_text)
            for j, subchunk in enumerate(subchunks):
                chunk_meta = metadata.copy()
                chunk_meta["chunk_number"] = f"{i}.{j}"
                chunks.append({"text": subchunk, "metadata": chunk_meta})
        else:
            chunk_meta = metadata.copy()
            chunk_meta["chunk_number"] = str(i)
            chunks.append({"text": chunk_text, "metadata": chunk_meta})

    return chunks


def load_documents() -> List[Dict]:
    all_chunks = []
    txt_files = list(DOCUMENTS_DIR.glob("*.txt"))

    if not txt_files:
        print("No .txt files found in documents folder.")
        return []

    for file_path in txt_files:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        metadata = extract_metadata(text, file_path.name)
        chunks = split_into_review_chunks(text, metadata)
        all_chunks.extend(chunks)

    return all_chunks


def build_vector_store(chunks: List[Dict]):
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)

    try:
        chroma_client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = chroma_client.create_collection(name=COLLECTION_NAME)

    ids = []
    documents = []
    metadatas = []
    embeddings = []

    for idx, chunk in enumerate(chunks):
        ids.append(f"chunk_{idx}")
        documents.append(chunk["text"])
        metadatas.append(chunk["metadata"])
        embeddings.append(model.encode(chunk["text"]).tolist())

    if documents:
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    return collection, model


def retrieve_chunks(question: str, collection, model, top_k: int = TOP_K) -> List[Dict]:
    query_embedding = model.encode(question).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    retrieved = []

    for doc, meta, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        retrieved.append({
            "text": doc,
            "metadata": meta,
            "distance": distance,
        })

    return retrieved


def format_context(retrieved_chunks: List[Dict]) -> str:
    context_parts = []

    for i, chunk in enumerate(retrieved_chunks, start=1):
        meta = chunk["metadata"]
        source = meta.get("source", "Unknown source")
        professor = meta.get("professor", "Unknown professor")
        url = meta.get("url", "")

        context_parts.append(
            f"Chunk {i}\n"
            f"Source: {source}\n"
            f"Professor: {professor}\n"
            f"URL: {url}\n"
            f"Text:\n{chunk['text']}"
        )

    return "\n\n---\n\n".join(context_parts)


def generate_answer(question: str, retrieved_chunks: List[Dict]) -> str:
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return (
            "GROQ_API_KEY is missing from the .env file. "
            "Retrieval worked, but generation cannot run until the API key is added."
        )

    client = Groq(api_key=api_key)
    context = format_context(retrieved_chunks)

    prompt = f"""
You are answering questions for an unofficial CSI Computer Science professor and course guide.

Use ONLY the retrieved context below.
Do not use outside knowledge.

If the retrieved context does not contain enough information, say:
"I do not have enough information in the collected documents to answer that."

When you answer, cite the source file names you used.

Retrieved context:
{context}

User question:
{question}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a careful RAG assistant that only answers using provided context.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=500,
    )

    return response.choices[0].message.content


def answer_question(question: str) -> Tuple[str, str]:
    if not question.strip():
        return "Please enter a question.", ""

    retrieved = retrieve_chunks(question, collection, embedding_model, TOP_K)
    answer = generate_answer(question, retrieved)

    sources = []
    for chunk in retrieved:
        meta = chunk["metadata"]
        sources.append(
            f"Source: {meta.get('source', 'Unknown')} | "
            f"Professor: {meta.get('professor', 'Unknown')} | "
            f"Distance: {chunk['distance']:.4f}"
        )

    return answer, "\n".join(sources)


print("Loading documents...")
chunks = load_documents()
print(f"Loaded {len(chunks)} chunks.")

print("\nSample chunks:")
for sample in chunks[:5]:
    print("=" * 80)
    print(sample["metadata"])
    print(sample["text"][:700])

print("\nBuilding vector store...")
collection, embedding_model = build_vector_store(chunks)
print("Vector store ready.")


with gr.Blocks() as demo:
    gr.Markdown("# Unofficial CSI CS Professor Guide")
    gr.Markdown("Ask a question about the collected CSI Computer Science professor reviews.")

    question_input = gr.Textbox(
        label="Your question",
        placeholder="Example: What do students say about Parziale's CSC 305 class?",
    )
    answer_output = gr.Textbox(label="Answer", lines=8)
    sources_output = gr.Textbox(label="Retrieved sources", lines=6)

    submit_button = gr.Button("Ask")
    submit_button.click(
        fn=answer_question,
        inputs=question_input,
        outputs=[answer_output, sources_output],
    )


if __name__ == "__main__":
    demo.launch()