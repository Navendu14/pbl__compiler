from transformers import AutoTokenizer, T5ForConditionalGeneration
import torch
import re

model_path = 'codecompiler/model/codefix-model'  # your unzipped folder

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = T5ForConditionalGeneration.from_pretrained(model_path)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def format_c_code(code):
    # Temporarily protect `for (...)` statements
    for_statements = re.findall(r'for\s*\(.*?\)', code)
    protected = {}

    for i, stmt in enumerate(for_statements):
        key = f"__FOR_STMT_{i}__"
        protected[key] = stmt
        code = code.replace(stmt, key)

    # Add newlines after semicolons, braces
    code = re.sub(r'\s*;\s*', ';\n', code)
    code = re.sub(r'\s*{\s*', ' {\n', code)
    code = re.sub(r'\s*}\s*', '\n}\n', code)

    # Restore protected `for` statements
    for key, stmt in protected.items():
        code = code.replace(key, stmt)

    # Optional: Basic indentation
    lines = code.splitlines()
    formatted_lines = []
    indent = 0
    for line in lines:
        line = line.strip()
        if line == '}':
            indent -= 1
        formatted_lines.append('    ' * indent + line)
        if line.endswith('{'):
            indent += 1

    return '\n'.join(formatted_lines)

def fix_code(buggy_code):
    model.eval()
    inputs = tokenizer(buggy_code, return_tensors="pt", truncation=True, padding=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=256)

    output = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return format_c_code(output)

