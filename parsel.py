import tkinter as tk
from tkinter import filedialog
import json
import re

def select_input_file():
    global input_file_path
    input_file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if input_file_path:
        input_file_label.config(text=f"Selected input file: {input_file_path}")
def find_correct_answer(data, start_index):
    i = start_index + 1
    while i < len(data):
        line = data[i]
        if "Answer" in line:
            correct_option_match = re.search(r'Answer\s*\(([A-D])\)', line)
            if correct_option_match:
                return correct_option_match.group(1)
        i += 1
    return None

def parse_input_file(input_file_path):
    questions = []
    current_question = {}
    question_started = False

    with open(input_file_path, 'r') as file:
        data = file.readlines()

    for i, line in enumerate(data):
        if "Question ID" in line:
            # If we have already started processing a question, add it to the list
            if question_started:
                questions.append(current_question)
                current_question = {}
                question_started = False

            # Extract question ID
            question_id = int(re.search(r'(\d+)', line).group(1))
            current_question["questionId"] = question_id

            # Extract question number
            question_number = len(questions) + 1
            current_question["questionNumber"] = question_number

            # Search for the question text in the following lines
            j = i + 1
            while j < len(data):
                if any(c.isalpha() for c in data[j]):  # Check if the line contains alphabetical characters
                    question_text = data[j].strip()
                    current_question["questionText"] = question_text
                    question_started = True
                    break
                j += 1

            # Find the correct answer
            correct_option = find_correct_answer(data, i)
            if correct_option:
                current_question["correctOption"] = correct_option

        elif question_started:
            # Process options and solution text
            if line.startswith("(A)") or line.startswith("(B)") or line.startswith("(C)") or line.startswith("(D)"):
                # Extract options
                if not current_question.get("options"):
                    current_question["options"] = []

                option_number = ord(line[1]) - 64
                option_text = line[4:].strip()

                # Check if the option is the correct answer
                is_correct = False
                if option_number == ord(current_question["correctOption"]) - 64:
                    is_correct = True

                current_question["options"].append({"optionNumber": option_number, "optionText": option_text, "isCorrect": is_correct})

            elif line.startswith("\\section*{Answer"):
                # Extract solution text
                solution_text = re.search(r'Sol\.(.*?)\\section\*{Question ID', line, re.DOTALL)
                if solution_text:
                    solution_text = solution_text.group(1).strip()
                current_question["solutionText"] = solution_text

    # Add the last question to the list
    if current_question:
        questions.append(current_question)

    return questions







def convert_to_json():
    global input_file_path
    if input_file_path:
        # Parse the input file and convert to JSON
        parsed_data = parse_input_file(input_file_path)
        # Save parsed data to JSON file
        output_file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if output_file_path:
            with open(output_file_path, 'w') as file:
                json.dump(parsed_data, file, indent=2)
            output_file_label.config(text="Conversion successful.")
        else:
            output_file_label.config(text="Please select an output file.")
    else:
        input_file_label.config(text="Please select an input file.")

# Create the Tkinter GUI
root = tk.Tk()
root.title("TXT to JSON Converter")

# Button to select input file
input_file_button = tk.Button(root, text="Select Input TXT File", command=select_input_file)
input_file_button.pack(pady=10)

# Label to display selected input file
input_file_label = tk.Label(root, text="")
input_file_label.pack(pady=5)

# Button to convert TXT to JSON
convert_button = tk.Button(root, text="Convert to JSON", command=convert_to_json)
convert_button.pack(pady=20)

# Label to display conversion status
output_file_label = tk.Label(root, text="")
output_file_label.pack(pady=5)

root.mainloop()
