# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain
I chose to build an unofficial CSI Computer Science professor and course survival guide. The system will answer questions about what students say about specific CS professors, course difficulty, grading style, attendance expectations, exams, homework, workload, and general advice for doing well.

This knowledge is valuable because official course catalogs only explain what a course is supposed to cover. They do not tell students what the class actually feels like, whether grading is strict, whether attendance matters, whether exams are difficult, or what students wish they knew before taking the class. That kind of information is usually scattered across RateMyProfessors reviews, Reddit posts, Discord messages, and word of mouth, so a searchable RAG guide makes it easier to find and cite.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source          | Description                                | URL or location                                                                  |
|---|-----------------|--------------------------------------------|----------------------------------------------------------------------------------|
| 1 | RateMyProfessors|Student reviews for Jonathan Parziale at CSI|https://www.ratemyprofessors.com/professor/2702929    documents/rmp_parziale.txt  |
| 2 | RateMyProfessors|Student reviews for Sarah Zelikovitz at CSI |https://www.ratemyprofessors.com/professor/857604     documents/rmp_zelikovitz.txt|
| 3 | RateMyProfessors|Student reviews for Cong Chen at CSI        |https://www.ratemyprofessors.com/professor/2805649    documents/rmp_chen.txt      |
| 4 | RateMyProfessors|Student reviews for Ali Mohamed at CSI      |https://www.ratemyprofessors.com/professor/2604940    documents/rmp_mohamed.txt   |
| 5 | RateMyProfessors|Student reviews for Jun Rao at CSI          |https://www.ratemyprofessors.com/professor/2714425    documents/rmp_rao.txt       |
| 6 | RateMyProfessors|Student reviews for Ping Shi at CSI         |https://www.ratemyprofessors.com/professor/2498365    documents/rmp_shi.txt       |
| 7 | RateMyProfessors|Student reviews for Orit Gruber at CSI      |https://www.ratemyprofessors.com/professor/1485282    documents/rmp_gruber.txt    | 
| 8 | RateMyProfessors|Student reviews for Joseph Tooker at CSI    |https://www.ratemyprofessors.com/professor/2880338    documents/rmp_tooker.txt    |
| 9 | RateMyProfessors|Student reviews for Richard Weir at CSI     |https://www.ratemyprofessors.com/professor/2197959    documents/rmp_weir.txt      |
| 10 |RateMyProfessors|Student reviews for Anthony Catalano at CSI |https://www.ratemyprofessors.com/professor/1690938    documents/rmp_catalano.txt  |
|-----------------------------------------------------------------------------------------------------------------------------------------------------|
---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**
About 600–900 characters per chunk
**Overlap:**
About 100–150 characters of overlap when a long review or long page section must be split
**Reasoning:**
Because most of my documents are student reviews instead of long textbook-style documents, I will not split blindly every 500 characters. I will try to chunk by individual review first because each review usually contains one complete student opinion about a professor or course.

If a review is very short, I may group two or three reviews from the same professor into one chunk so the embedding has enough context. If a review or page section is too long, I will split it at paragraph or sentence boundaries instead of cutting randomly in the middle of an idea.

This strategy fits my documents because review-based text is usually short, opinion-heavy, and tied to one professor or course. Chunks that are too small may only say vague things like “great professor” without explaining why. Chunks that are too large may mix different courses or conflicting opinions, which could make retrieval less accurate.

Each chunk will keep metadata including the source filename, professor name, chunk number, and course number if available
---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**
I will use all-MiniLM-L6-v2 from sentence-transformers.
**Top-k:**
I will retrieve the top 4 chunks for each query.
**Production tradeoff reflection:**
I chose all-MiniLM-L6-v2 because it runs locally, is fast, does not require an API key, and is recommended for this project. I chose top-k = 4 because one review may not be enough to answer a question fairly, but retrieving too many chunks could introduce unrelated or conflicting reviews.

If the answers seem too thin, I may increase top-k to 5. If the answers seem off-topic, I may lower it to 3 or improve the chunking strategy.
---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question                                                               | Expected answer |
|---|------------------------------------------------------------------------|-----------------|
| 1 | What do students say about Jonathan Parziale’s CSC 305 class structure?| The system should summarize what reviews say about the class structure, labs, workload, exams, or assignments. It should cite rmp_parziale.txt.
| 2 | What do students say about Cong Chen’s grading or difficulty?          | The system should mention whether reviews describe the course as difficult, fair, lecture-heavy, exam-heavy, or manageable. It should cite rmp_chen.txt.
| 3 | What do students say about Ali Mohamed’s upper-level CS courses?       | The system should mention what students say about the material, difficulty, assignments, exams, and teaching style. It should cite rmp_mohamed.txt.
| 4 | What advice do students give for doing well in Ping Shi’s classes?     | The system should mention advice from reviews, such as studying, doing homework, attending class, or preparing for quizzes/tests. It should cite rmp_shi.txt.
| 5 | What do students say about Joseph Tooker’s teaching style or workload? | The system should mention whether students describe him as approachable, chill, difficult, project-heavy, exam-heavy, or homework-heavy. It should cite rmp_tooker.txt.

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. A challenge is that student reviews may disagree with each other. One student might say a professor is helpful and fair, while another student might say the same professor is difficult or unclear. The system should not treat one review as the full truth. It should explain when opinions are mixed and summarize the overall pattern from the retrieved reviews

2. Another challenge is keeping the course context clear. A professor may teach different classes in very different ways, so a review for one course may not apply to another course. If the chunks lose course numbers or course names, the system might answer a question about one class using information from a different class.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->
     
A[Document Ingestion: load .txt files from documents folder] --> B[Cleaning: remove extra whitespace and page noise] 
B --> C[Chunking: split by review or paragraph] 
C --> D[Embedding: all-MiniLM-L6-v2 using sentence-transformers] 
D --> E[Vector Store: ChromaDB with chunk metadata]
F[User Question] --> G[Query Embedding: embed the user question]
G --> H[Retrieval: return top 4 relevant chunks]
E --> H 
H --> I[Generation: Groq LLM answers using retrieved context only] 
I --> J[Interface: Gradio or Streamlit answer and sources display]
---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**
I will use Claude or ChatGPT to help write the document loading and chunking code. I will give the AI my Domain, Documents, and Chunking Strategy sections from this planning document. I will also tell it that my files are plain .txt files inside the documents/ folder. I expect it to produce Python code that loads each document, cleans extra whitespace, removes obvious page noise, and splits the reviews into chunks by review or paragraph.

To verify the output, I will run the script and print several sample chunks. I will check that the chunks are readable, not too short, not too long, and still include useful context like the professor name, course number if available, and source file.

**Milestone 4 — Embedding and retrieval:**
I will use Claude or ChatGPT to help write the embedding and retrieval code. I will give the AI my Retrieval Approach section and Architecture section. I will ask it to use sentence-transformers with all-MiniLM-L6-v2 and ChromaDB to store the chunk embeddings with metadata.

I expect it to produce code that embeds each chunk, saves the embeddings in ChromaDB, embeds the user’s question, and retrieves the top 4 most relevant chunks. To verify it, I will test questions from my Evaluation Plan and check whether the retrieved chunks come from the correct professor document.

**Milestone 5 — Generation and interface:**
I will use Claude or ChatGPT to help create the grounded generation step and the user interface. I will give the AI my Evaluation Plan and tell it that the answer must be based only on the retrieved chunks. I expect it to write a prompt for the Groq LLM that tells the model to answer using only the provided context and to say it does not have enough information when the documents do not answer the question.

I will also ask the AI to help build a simple Gradio or Streamlit interface with a question input, answer output, and sources output. To verify it, I will ask the system both in-scope questions and an out-of-scope question. The in-scope answers should cite the right documents, and the out-of-scope answer should not make anything up.
