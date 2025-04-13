import gradio as gr
import os
from ltx_integration import LTXVideoProcessor
from openshot_api import OpenShotAPI
import threading
import queue

class GradioInterface:
    def __init__(self):
        self.ltx_processor = LTXVideoProcessor()
        self.openshot = OpenShotAPI()
        self.processing_queue = queue.Queue()
        self.processing_thread = None

    def start_processing_thread(self):
        """Start background processing thread"""
        if self.processing_thread is None or not self.processing_thread.is_alive():
            self.processing_thread = threading.Thread(target=self._process_queue)
            self.processing_thread.daemon = True
            self.processing_thread.start()

    def _process_queue(self):
        """Process items from the queue"""
        while True:
            try:
                task = self.processing_queue.get()
                if task is None:
                    break
                task()
            except Exception as e:
                print(f"Error processing task: {e}")
            finally:
                self.processing_queue.task_done()

    def create_ai_interface(self):
        """Create Gradio interface for AI features"""
        with gr.Blocks(title="Flux58 AI Tools") as interface:
            gr.Markdown("# Flux58 AI Video Tools")
            
            with gr.Tab("Style Transfer"):
                with gr.Row():
                    with gr.Column():
                        input_video = gr.Video(label="Input Video")
                        style_image = gr.Image(label="Style Image")
                        strength = gr.Slider(0, 1, value=0.5, label="Style Strength")
                    with gr.Column():
                        output_video = gr.Video(label="Output Video")
                        progress = gr.Textbox(label="Progress", interactive=False)
                
                style_btn = gr.Button("Apply Style")
                style_btn.click(
                    fn=self._style_transfer,
                    inputs=[input_video, style_image, strength],
                    outputs=[output_video, progress]
                )

            with gr.Tab("Video Enhancement"):
                with gr.Row():
                    with gr.Column():
                        enhance_video = gr.Video(label="Input Video")
                        enhancement_type = gr.Dropdown(
                            choices=["upscale", "denoise", "stabilize"],
                            label="Enhancement Type"
                        )
                    with gr.Column():
                        enhanced_output = gr.Video(label="Enhanced Video")
                        enhance_progress = gr.Textbox(label="Progress", interactive=False)
                
                enhance_btn = gr.Button("Enhance Video")
                enhance_btn.click(
                    fn=self._enhance_video,
                    inputs=[enhance_video, enhancement_type],
                    outputs=[enhanced_output, enhance_progress]
                )

            with gr.Tab("Text to Video"):
                with gr.Row():
                    with gr.Column():
                        prompt = gr.Textbox(label="Video Description")
                        duration = gr.Slider(1, 60, value=5, label="Duration (seconds)")
                    with gr.Column():
                        generated_video = gr.Video(label="Generated Video")
                        gen_progress = gr.Textbox(label="Progress", interactive=False)
                
                generate_btn = gr.Button("Generate Video")
                generate_btn.click(
                    fn=self._generate_video,
                    inputs=[prompt, duration],
                    outputs=[generated_video, gen_progress]
                )

        return interface

    def _style_transfer(self, video_path, style_image, strength):
        """Apply style transfer to video"""
        def process():
            try:
                # Add video to processing queue
                self.processing_queue.put(lambda: self.ltx_processor.apply_style(
                    video_path, 
                    style_image, 
                    strength
                ))
                return "Processing started..."
            except Exception as e:
                return f"Error: {str(e)}"
        
        self.start_processing_thread()
        return None, process()

    def _enhance_video(self, video_path, enhancement_type):
        """Enhance video quality"""
        def process():
            try:
                # Add video to processing queue
                self.processing_queue.put(lambda: self.openshot.enhance_video(
                    video_path,
                    enhancement_type
                ))
                return "Processing started..."
            except Exception as e:
                return f"Error: {str(e)}"
        
        self.start_processing_thread()
        return None, process()

    def _generate_video(self, prompt, duration):
        """Generate video from text"""
        def process():
            try:
                # Add video generation to queue
                self.processing_queue.put(lambda: self.ltx_processor.generate_video(
                    prompt,
                    duration
                ))
                return "Generation started..."
            except Exception as e:
                return f"Error: {str(e)}"
        
        self.start_processing_thread()
        return None, process()

# Create and launch the interface
if __name__ == "__main__":
    interface = GradioInterface()
    gradio_app = interface.create_ai_interface()
    gradio_app.launch(share=True) 