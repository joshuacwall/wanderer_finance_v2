from dotenv import load_dotenv
import gradio as gr
from app import current_picks, welcome, evaluation,current_passes
load_dotenv() 

def create_gradio_interface():
    with gr.Blocks() as demo:
        with gr.Tabs():
            welcome.create_tab(),
            current_picks.create_tab(),
            current_passes.create_tab(),
            evaluation.create_tab(),
    return demo

if __name__ == "__main__":
    demo = create_gradio_interface() # Create the interface
    demo.launch() # Launch the interface