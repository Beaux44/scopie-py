from .compile import Parser, lex
import json
import os


file_path = os.path.dirname(os.path.realpath(__file__))
with open(f"{file_path}/scenarios.json") as f:
    test_cases = json.load(f)["benchmarks"]

for bench in test_cases:
    rules = Parser(bench["actor"]).parse()
    scopes = bench["rules"]
    print(f"Test ID: {bench['id']}")
    print(f"Actor: {bench['actor']}")
    print(f"Parser Output: {rules}\n")

