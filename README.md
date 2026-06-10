# The Unofficial Guide — Project 1

---

## Domain

Student reviews of CS professors at Rutgers University - New Brunswick. This knowledge is valuable because official course descriptions say nothing about teaching style, exam difficulty, grading fairness, or actual workload. Students rely on word-of-mouth and Rate My Professors to make scheduling decisions, but that information is scattered across individual professor pages and impossible to query across multiple professors at once. This system makes it searchable.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Rate My Professors | Student reviews | https://www.ratemyprofessors.com/professor/2814183 → docs/abraham_gale.txt |
| 2 | Rate My Professors | Student reviews | https://www.ratemyprofessors.com/professor/600296 → docs/ana_centeno.txt |
| 3 | Rate My Professors | Student reviews | https://www.ratemyprofessors.com/professor/182646 → docs/sesh_venugopal.txt |
| 4 | Rate My Professors | Student reviews | https://www.ratemyprofessors.com/professor/2336289 → docs/david_menendez.txt |
| 5 | Rate My Professors | Student reviews | https://www.ratemyprofessors.com/professor/2414859 → docs/ananda_gunawardena.txt |
| 6 | Rate My Professors | Student reviews | https://www.ratemyprofessors.com/professor/2519830 → docs/samaneh_hamidi.txt |
| 7 | Rate My Professors | Student reviews | https://www.ratemyprofessors.com/professor/1580600 → docs/tomasz_imielinski.txt |
| 8 | Rate My Professors | Student reviews | https://www.ratemyprofessors.com/professor/1916642 → docs/bernhard_firner.txt |
| 9 | Rate My Professors | Student reviews | https://www.ratemyprofessors.com/professor/2980565 → docs/minesh_patel.txt |
| 10 | Rate My Professors | Student reviews | https://www.ratemyprofessors.com/professor/2702069 → docs/miranda_garcia.txt |

---

## Chunking Strategy

**Chunk size:** 400 characters

**Overlap:** 50 characters

**Why these choices fit your documents:** Each document is a collection of short student reviews, typically 2 to 5 sentences each. A 400-character chunk captures roughly one full review without cutting it in half or merging it with the next one. The 50-character overlap ensures that if a review happens to land on a chunk boundary, the key opinion still appears in at least one retrievable chunk. Chunks smaller than 300 characters would risk cutting individual reviews mid-sentence, which makes them too fragmented to carry semantic meaning. Chunks larger than 600 would start merging multiple reviews together and dilute the signal for retrieval. Before chunking, whitespace was normalized by collapsing multiple newlines and spaces using regex.

**Final chunk count:** 171

---

## Embedding Model

**Model used:** all-MiniLM-L6-v2 via sentence-transformers

**Production tradeoff reflection:** For a production system I would consider text-embedding-3-large from OpenAI or a similar model for higher accuracy on domain-specific text. The main tradeoffs are: all-MiniLM-L6-v2 is fast and completely free but has a 256-token context limit, which is fine for short reviews but would truncate longer documents. A production model would also need multilingual support if serving international students writing reviews in other languages. API-hosted models cost money per query but remove the need for local compute. For this project, local embedding was the right call since there are no rate limits, no cost, and the accuracy is sufficient for short English review text.

---

## Grounded Generation

**System prompt grounding instruction:**

"You are a helpful assistant that answers questions about Rutgers CS professors.
Answer the question using ONLY the information in the provided documents below.
Do not use any outside knowledge.
If the documents don't contain enough information to answer the question, say exactly:
"I don't have enough information on that in my documents."
Always cite which document(s) your answer comes from."

**How source attribution is surfaced in the response:** Source filenames are pulled programmatically from the ChromaDB metadata attached to each retrieved chunk. They are collected into a deduplicated list and displayed in the UI under a separate "Sources" field, independent of what the LLM writes. The LLM is also instructed in the prompt to cite sources inline in its answer, so attribution happens at two levels: structurally from metadata and in the generated text.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about Sesh Venugopal's exams? | Exams are hard, graded harshly, no curve, inconsistent with lecture material | Correctly identified exams as brutal with dense questions and poor prep; missed no-curve and lecture inconsistency details | Partially relevant (Hamidi chunks slipped in at results 2, 3, 5) | Partially accurate |
| 2 | Is Ana Centeno a good professor for CS111? | Generally yes, engaging lectures, cares about students, extra credit, sometimes goes off topic | Correctly said she is a good professor, great for beginners, engaging, walks through topics carefully | Relevant (all top results from ana_centeno.txt) | Accurate |
| 3 | How is grading in Hamidi's class? | Very strict, quiz-heavy, attendance mandatory, exams pulled from practice problems | Correctly identified quiz-heavy grading, attendance mandatory, exams from practice problems, skip-final option | Mostly relevant (one Menendez chunk appeared but answer handled it) | Accurate |
| 4 | What courses does David Menendez teach and how hard are they? | CS211 and CS214, very hard projects, slow grading, generous curve | Correctly listed CS211, CS214, CS314; missed slow grading and generous curve details | Partially relevant (chunks from unrelated professors appeared) | Partially accurate |
| 5 | What do students say about Minesh Patel's lectures in CS211? | Clear, organized, recorded, explains well, mostly positive with some Spring 2026 disorganization | Correctly identified recorded lectures, organized, explains from different angles; missed Spring 2026 disorganization note | Partially relevant (Venugopal and Gunawardena chunks appeared) | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** What do students say about Sesh Venugopal's exams?

**What the system returned:** The system correctly identified that exams are brutal and dense, but retrieved three chunks from samaneh_hamidi.txt alongside the two relevant Venugopal chunks. The answer missed key details like the lack of a curve and the disconnect between lectures and exam content.

**Root cause (tied to a specific pipeline stage):** This is a retrieval stage failure caused by semantic overlap between documents. Both Venugopal and Hamidi reviews use language like "brutal" and "difficult exams," so the embedding model scored Hamidi chunks as similar to the query even though they describe a different professor entirely. With top-k set to 5 and only 2 truly relevant chunks retrieved, the LLM had limited Venugopal-specific context to draw from. The 400-character chunk size also means some reviews about Venugopal's grading and lecture inconsistency were split across boundaries, so those specific details never appeared in any single retrieved chunk.

**What you would change to fix it:** Adding professor name as a metadata filter would let retrieval restrict results to the correct source file when the query names a specific professor. Alternatively, increasing chunk size slightly to 500 or 600 characters would reduce the number of split reviews and give each chunk more semantic specificity, making it less likely to match on a single shared word like "brutal."

---

## Spec Reflection

**One way the spec helped you during implementation:** Writing the chunking strategy in planning.md before touching any code forced a concrete decision about chunk size early. When the ingest.py output showed 171 chunks and the sample chunks looked like complete reviews, it was easy to verify the implementation matched the spec. Without that upfront decision written down, I would have just picked a number arbitrarily and had no way to evaluate whether it was working correctly.

**One way your implementation diverged from the spec, and why:** The planning.md anticipated professor nicknames like "Menny" and "Guna" as a major retrieval failure, but that failure never came up during testing because all eval questions used full professor names. The actual failure that surfaced was semantic overlap between professors, which the spec did not anticipate. The mixed-sentiment challenge was predicted but turned out to be less of a problem than expected since the LLM handled synthesizing mixed reviews reasonably well.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* The Chunking Strategy and Documents sections from planning.md, plus the requirement to load .txt files from docs/, clean whitespace, split into 400-character chunks with 50-character overlap, and print 5 sample chunks for verification.
- *What it produced:* A complete ingest.py with load_documents(), clean_text(), chunk_text(), and build_vector_store() functions that matched the spec exactly.
- *What I changed or overrode:* Nothing needed to change. I ran it, checked the 5 sample chunks looked like real reviews and not fragments or HTML, confirmed 171 total chunks, and moved on.

**Instance 2**

- *What I gave the AI:* The Retrieval Approach section, the grounding requirement (answer only from retrieved context, cite sources), and the Gradio skeleton from the project spec.
- *What it produced:* query.py with a retrieve() function using ChromaDB and all-MiniLM-L6-v2, an ask() function with a Groq API call and a system prompt enforcing grounding, and app.py with a working Gradio interface showing answer and sources separately.
- *What I changed or overrode:* I tested retrieval on 3 eval queries before wiring in generation, which the AI did not suggest. After seeing Hamidi chunks slip into Venugopal results, I kept top-k at 5 rather than increasing it, since adding more chunks would have brought in even more off-topic results.