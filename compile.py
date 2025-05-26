import subprocess
import re
import os
import multiprocessing
import hashlib
import shutil

TEMP_DIR = "temp_files"
os.makedirs(TEMP_DIR, exist_ok=True)

CACHE_DIR = "obj_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

input_ll = os.path.join(TEMP_DIR, "input.ll")
subprocess.run(["clang", "-S", "-emit-llvm", "input.c", "-o", input_ll], check=True)
print("Step 1: input.c converted to", input_ll)

with open(input_ll, "r") as f:
    content = f.read()
func_names = re.findall(r"define\s+.*?\s+@(\w+)\(", content)
print("Step 2: Functions found:", func_names)

with open(input_ll, "r") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if line.strip().startswith("define"):
        break
globals_lines = lines[:i]
for j, line in enumerate(globals_lines):
    if line.strip().startswith("@"):
        globals_lines[j] = line.replace("private", "linkonce_odr")
globals_ll = os.path.join(TEMP_DIR, "globals.ll")
with open(globals_ll, "w") as f:
    f.writelines(globals_lines)
print("Step 3a: Extracted and modified", globals_ll, "with linkonce_odr linkage")

globals_o = os.path.join(TEMP_DIR, "globals.o")
subprocess.run(["clang", "-c", globals_ll, "-o", globals_o], check=True)
print("Step 3b: Compiled", globals_ll, "to", globals_o)

ll_files = []
if len(func_names) > 1:
    for func in func_names:
        bc_file = os.path.join(TEMP_DIR, f"{func}.bc")
        ll_file = os.path.join(TEMP_DIR, f"{func}.ll")
        
        subprocess.run(["llvm-extract", "-func", func, input_ll, "-o", bc_file], check=True)

        subprocess.run(["llvm-dis", bc_file, "-o", ll_file], check=True)
        
        ll_files.append(ll_file)
else:
    ll_files = [input_ll]
print("Step 4: Split input.ll into separate .ll files:", ll_files)

def normalize_ll_code(code: str) -> str:
    code = re.sub(r"^\s*;.*", "", code, flags=re.MULTILINE)
    code = re.sub(r'^\s*source_filename\s*=.*', '', code, flags=re.MULTILINE)
    code = re.sub(r'^\s*target datalayout\s*=.*', '', code, flags=re.MULTILINE)
    code = "\n".join(line.strip() for line in code.splitlines() if line.strip())
    
    declares = []
    defines = []
    for line in code.splitlines():
        if line.startswith("declare"):
            declares.append(line.strip())
        else:
            defines.append(line)

    declares = sorted(declares)
    triple_match = re.search(r'(target triple\s*=\s*".*?")', code)
    triple_line = triple_match.group(1) if triple_match else None

    normalized = []
    if triple_line:
        normalized.append(triple_line)
    normalized.extend(declares)
    normalized.extend(defines)

    return "\n".join(normalized)

def compute_file_hash(file_path):
    with open(file_path, 'r') as f:
        code = f.read()
    normalized_code = normalize_ll_code(code)
    return hashlib.sha256(normalized_code.encode('utf-8')).hexdigest()

def compile_to_o(ll_file)
    file_hash = compute_file_hash(ll_file)
    cached_obj = os.path.join(CACHE_DIR, f"{file_hash}.o")
    
    base_name = os.path.splitext(os.path.basename(ll_file))[0]
    o_file = os.path.join(TEMP_DIR, f"{base_name}.o")
    
    if os.path.exists(cached_obj):
        shutil.copyfile(cached_obj, o_file)
        print(f"Cache hit: {ll_file} → {o_file} (from {cached_obj})")
    else:
        subprocess.run(["clang", "-c", ll_file, "-o", o_file], check=True)
        print(f"Compiled {ll_file} to {o_file}")
        
        shutil.copyfile(o_file, cached_obj)
        print(f"Cached {o_file} as {cached_obj}")

with multiprocessing.Pool() as pool:
    pool.map(compile_to_o, ll_files)
print("Step 5: Compiled all .ll files to .o files with caching")

o_files = [os.path.join(TEMP_DIR, f"{os.path.splitext(os.path.basename(ll_file))[0]}.o") for ll_file in ll_files] + [globals_o]
subprocess.run(["clang"] + o_files + ["-o", "output"], check=True)
print("Step 6: Linked all .o files into executable 'output'")

try:
    shutil.rmtree(TEMP_DIR)
    print("Step 7: Cleaned up temporary directory", TEMP_DIR)
except Exception as e:
    print(f"Step 7: Failed to clean up {TEMP_DIR}: {e}")
