import gradio as gr
from query import ask

def handle_query(question):
    if not question.strip():
        return "Please enter a question.", ""
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources

with gr.Blocks(title="Rutgers CS Professor Guide") as demo:
    gr.Markdown("# 🎓 Rutgers CS Professor Unofficial Guide")
    gr.Markdown("Ask anything about Rutgers CS professors based on real student reviews.")
    
    inp = gr.Textbox(label="Your question", placeholder="e.g. Is Sesh Venugopal good for CS213?")
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Sources", lines=3)
    
    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

demo.launch()