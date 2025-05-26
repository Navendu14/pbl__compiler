from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .model_loader import fix_code
import subprocess


def index(request):
    output = ""
    fixed_code = ""
    input_code = ""

    if request.method == 'POST':
        input_code = request.POST['code']
        action = request.POST['action']

        if action == 'compile':
            # Save code to input.c
            with open("input.c", "w") as f:
                f.write(input_code)

            try:
                # Run compile.py and capture both stdout and stderr
                compile_process = subprocess.run(
                    ["python3", "compile.py"],
                    capture_output=True, text=True
                )

                if compile_process.returncode != 0:
                    output = f"🔴 Compilation failed:\n{compile_process.stderr}"
                else:
                    # Run the final executable
                    run_result = subprocess.run(["./output"], capture_output=True, text=True)
                    output = run_result.stdout or run_result.stderr

            except Exception as e:
                output = f"⚠️ Unexpected error:\n{str(e)}"


        elif action == 'fix':
            fixed_code = fix_code(input_code)

    return render(request, 'index.html', {
        'input_code': input_code,
        'output': output,
        'fixed_code': fixed_code
    })
