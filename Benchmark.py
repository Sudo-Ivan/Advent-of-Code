import json
import os
import re
import subprocess
from pathlib import Path
from timeit import default_timer as timer

RUST_DIR = "Rust"
PYTHON_DIR = "Python"
RUST_SOLUTIONS_DIR = f"{RUST_DIR}/solutions"
PYTHON_SOLUTIONS_DIR = f"{PYTHON_DIR}/solutions"
CARGO_TOML_PATH = f"{RUST_DIR}/Cargo.toml"
RESULTS_JSON_PATH = "benchmark_results.json"
NUM_RUNS = 5

def run_process(command, cwd):
    start = timer()
    process = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    end = timer()

    if process.returncode != 0:
        return None, f"Error: {process.stderr.decode('utf-8')}"

    return end - start, process.stdout.decode('utf-8')

def update_cargo_toml(rust_solutions):
    cargo_toml = Path(CARGO_TOML_PATH)
    existing_bins = set()

    if cargo_toml.exists():
        with cargo_toml.open('r') as file:
            data = file.read()
            existing_bins = set(re.findall(r'name = "(day\d+)"', data))

    new_bins = [s.replace('.rs', '') for s in rust_solutions if s.replace('.rs', '') not in existing_bins]

    if new_bins:
        with cargo_toml.open('a') as file:
            for bin_name in new_bins:
                file.write(f'\n[[bin]]\nname = "{bin_name}"\npath = "solutions/{bin_name}.rs"\n')

def find_solutions(directory, extension):
    return sorted(f for f in os.listdir(directory) if f.startswith("day") and f.endswith(extension))

def compile_rust_solutions():
    subprocess.run(["cargo", "build", "--release"], cwd=RUST_DIR)

def benchmark_rust(day):
    bin_path = (Path(RUST_DIR) / "target" / "release" / day).resolve()
    times = []
    for _ in range(NUM_RUNS):
        time, output = run_process([str(bin_path)], cwd=RUST_DIR)
        if output.startswith("No solution found"):
            raise ValueError(output)
        times.append(time)
    avg_time = sum(times) / NUM_RUNS
    return avg_time, output

def benchmark_python(day):
    times = []
    for _ in range(NUM_RUNS):
        time, output = run_process(["python", f"solutions/{day}.py"], cwd=PYTHON_DIR)
        times.append(time)
    avg_time = sum(times) / NUM_RUNS
    return avg_time, output

def write_results_to_json(results):
    with open(RESULTS_JSON_PATH, 'w') as json_file:
        json.dump(results, json_file, indent=4)

def main():
    rust_solutions = find_solutions(RUST_SOLUTIONS_DIR, ".rs")
    python_solutions = find_solutions(PYTHON_SOLUTIONS_DIR, ".py")

    update_cargo_toml(rust_solutions)
    compile_rust_solutions()

    benchmarks = {}
    any_benchmarks_ran = False

    for day in rust_solutions:
        try:
            day_name = day.split('.')[0]
            time, output = benchmark_rust(day_name)
            benchmarks[f"Rust {day}"] = {"time": time, "output": output}
            any_benchmarks_ran = True
        except Exception as e:
            benchmarks[f"Rust {day}"] = {"time": None, "output": str(e)}

    for day in python_solutions:
        try:
            day_name = day.split('.')[0]
            time, output = benchmark_python(day_name)
            benchmarks[f"Python {day}"] = {"time": time, "output": output}
            any_benchmarks_ran = True
        except Exception as e:
            benchmarks[f"Python {day}"] = {"time": None, "output": str(e)}

    for lang_day, result in benchmarks.items():
        print(f"{lang_day}:")
        if result["time"] is not None:
            print(f"  Time: {result['time']} seconds")
        else:
            print(f"  Time: Benchmark failed")

        if result["output"]:
            print(f"  Output: {result['output']}")
        print()

    if any_benchmarks_ran:
        write_results_to_json(benchmarks)

if __name__ == "__main__":
    main()