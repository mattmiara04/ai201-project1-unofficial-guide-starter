# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

My project covers unofficial student knowledge about Computer Science professors and courses at the College of Staten Island. The system is meant to answer questions about what students say regarding teaching style, difficulty, grading, exams, workload, attendance, and advice for doing well.

This knowledge is valuable because official course descriptions only explain what a class is supposed to cover. They do not usually explain what the professor is like, how hard the exams feel, whether grading is fair, or what students wish they knew before taking the class. That kind of information is usually scattered across student reviews and word of mouth, so my system collects it into a searchable RAG guide.
---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

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

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**
Most chunks are one student review each. For longer reviews, the system splits text into chunks of about 850 characters.
**Overlap:**
For longer chunks, I used an overlap of about 150 characters. This helps avoid cutting off important context if a useful sentence is near the boundary between two chunks.
**Why these choices fit your documents:**
My documents are mostly short student reviews, not long articles or textbooks. Because of that, splitting by individual review makes more sense than blindly splitting every fixed number of characters. A single review usually contains one complete student opinion about a professor or class. If chunks were too small, they might only say something vague like “good professor” without enough explanation. If chunks were too large, they might mix too many different opinions together and make retrieval less precise.

Before chunking, the system cleans the text by normalizing line breaks and removing extra whitespace. I also manually avoided copying page navigation, ads, buttons, and unrelated website text into the document files.
**Final chunk count:**
The system loaded approximately one chunk per review from the files in the documents/ folder. In my run, the app printed the loaded chunk count in the terminal when python app.py started.
---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**
I used all-MiniLM-L6-v2 from sentence-transformers.
**Production tradeoff reflection:**
I chose this model because it runs locally, is fast, does not require a paid API key, and works well for a small class project. It is also the recommended embedding model for this project.

If I were deploying this for real users and cost was not a constraint, I would compare stronger embedding models for better accuracy on short opinion-based text. I would also consider context length, latency, multilingual support, and whether the model handles messy student language well. I would also consider hybrid retrieval with keyword search because exact course numbers like CSC 305, CSC 332, or CSC 211 may be important and semantic search may not always prioritize exact matches.
---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**
My system sends the retrieved chunks to the Groq LLM with a prompt that tells it to answer only from the provided context. The prompt includes this instruction:
"Use ONLY the retrieved context below. Do not use outside knowledge. If the retrieved context does not contain enough information, say: "I do not have enough information in the collected documents to answer that." When you answer, cite the source file names you used."
This is meant to prevent the LLM from guessing about professors or courses that are not actually covered in the retrieved reviews.
**How source attribution is surfaced in the response:**
Each chunk is stored with metadata including the source filename, professor name, and URL. When the system returns an answer, the interface also displays the retrieved sources below the answer. For example, when I asked about Cong Chen, the retrieved sources were all from rmp_chen.txt, which made the answer easy to verify.

The app has two output boxes: one for the generated answer and one for retrieved sources. The retrieved sources box shows the source file, professor name, and similarity distance score.
---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question                                                            | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|---------------------------------------------------------------------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about Cong Chen’s grading or difficulty?       | Mention whether reviews describe the class as difficult, fair, point-based, exam-heavy, or manageable.| The system said student opinions were mixed. Some reviews said Cong Chen’s grading was clear and point-based, while another review said the class was difficult, exams had low averages, and extra points were needed for many students to pass.| Relevant| Accurate
| 2 | What do students say about Jonathan Parziale?                       | Summarize student comments about Parziale’s teaching style, coursework, and class experience based on the reviews.| The system said students described Jonathan Parziale as a great professor who gives challenging but worthwhile labs, has clear grading criteria, and is helpful and understanding.|Relevant | Accurate|
| 3 | What do students say about Ali Mohamed?                             | Mention what students say about his teaching style, difficulty, assignments, exams, or upper-level CS courses.|The system said students had a very positive opinion of Ali Mohamed. It described him as a great, chill, and hands-on professor who explains concepts clearly, is helpful with lectures, gives similar exams and homework, and is a generous grader. | Relevant| Accurate|
| 4 | What advice do students give for doing well in Ping Shi’s classes?  | Mention advice such as studying, doing homework, attending class, paying attention to examples, or preparing for quizzes/tests if those appear in the reviews.|The system said students recommend asking questions, doing the homework, and putting in effort to learn the material. It cited reviews from rmp_shi.txt. |Relevant |Accurate |
| 5 | What do students say about Anthony Catalano?                        | Summarize student opinions about Catalano’s teaching style, workload, grading, and whether students found the class useful or easy.| The system said students describe Anthony Catalano as easy-going, laid-back, cool, and an easy grader. It also noted that some students said he does not really teach much in class and may not be best for students who want to learn deeply.| Relevant|Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**
What do students say about Jonathan Parziale’s CSC 305 class structure?
**What the system returned:**
The system said it did not have enough information in the collected documents to answer. It noted that the retrieved Parziale source mentioned CSC 332, not CSC 305.
**Root cause (tied to a specific pipeline stage):**
This was mainly a document coverage issue, not a generation issue. My collected Parziale reviews did not include enough information about CSC 305 specifically. Retrieval found a related Parziale document, but the context did not contain the exact course information asked for. Because the prompt told the LLM not to use outside knowledge, the model refused instead of making up an answer.
**What you would change to fix it:**
I would collect more course-specific reviews for Jonathan Parziale, especially reviews that mention CSC 305 directly. I would also improve metadata extraction so that course numbers are stored more clearly with each chunk. That would make it easier to filter or retrieve chunks by exact course number.
---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**
The planning document helped me stay focused on the required RAG pipeline instead of jumping straight into the interface. I already knew my domain, documents, chunking strategy, retrieval approach, and evaluation questions before writing the app. That made it easier to check whether each part of the code matched the project requirements.
**One way your implementation diverged from the spec, and why:**
The spec also helped with debugging because I knew what each stage was supposed to do. When the system retrieved a related professor but not the exact CSC 305 information, I could identify that as a document coverage and retrieval limitation instead of just saying the answer was wrong.
---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*I gave the AI my project domain, which was CSI Computer Science professor reviews, and explained that my documents were mostly short RateMyProfessors-style reviews instead of long articles or PDFs.
- *What it produced:*The AI helped me think through why review-based text should be chunked differently from long documents. It suggested that individual reviews should usually stay together because each review often contains one complete student opinion.
- *What I changed or overrode:*I decided to keep the chunking simple and based mostly on review boundaries. I did not use a random fixed-size split as my main strategy because that could cut a student review in half and make the retrieved context harder to understand. For longer reviews, I kept the character-based backup split with overlap.

**Instance 2**

- *What I gave the AI:*After running the system, I gave the AI examples of my actual questions, system answers, and retrieved sources. For example, I shared that the Parziale CSC 305 question returned a refusal because my collected documents only mentioned CSC 332.
- *What it produced:*The AI helped me interpret whether each result should be considered accurate, partially accurate, or a failure case. It pointed out that the CSC 305 question was not a bad hallucination; it was a document coverage limitation because my documents did not contain the exact course information.
- *What I changed or overrode:*I used the actual outputs from my own system instead of inventing perfect results. I marked the Jonathan Parziale general question as partially accurate because retrieval included some unrelated professor documents, even though the final answer was still mostly useful. I also used the CSC 305 question as my honest failure case.
