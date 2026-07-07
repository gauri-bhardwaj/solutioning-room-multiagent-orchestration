import os 

def load_guardrails(folder="guardrails"):
    
    if not os.path.exists(folder):
        return ""
    
    markdown_files = [f for f in os.listdir(folder) if f.endswith(".md")]
    markdown_files.sort()  # Ensure stable order
    
    concatenated = []
    for filename in markdown_files:
        with open(os.path.join(folder, filename), "r") as f:
            concatenated.append(f.read() + "\n\n")

    return "".join(concatenated)
