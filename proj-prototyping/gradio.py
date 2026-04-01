import gradio as gr

def process_file(input_file, action):
    # 'input_file' is a temp file object
    # 'action' is the string selected from the dropdown
    if input_file is None:
        return "No file uploaded!"
    
    file_name = input_file.name
    return f"Action '{action}' applied to file: {file_name}"

demo = gr.Interface(
    fn=process_file,
    inputs=[
        gr.File(label="Upload your Document"), 
        gr.Dropdown(
            choices=["Analyze", "Summarize", "Convert to PDF"], 
            label="Choose Action"
        )
    ],
    outputs="text",
    title="File Processor 1.0"
)

demo.launch()