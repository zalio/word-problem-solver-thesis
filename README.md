# Question Based Problem Solver

## Installation

1. Download and install question generator program called QG-Iztech. The steps for this can be found here: 
https://github.com/OnurKeklik/Qg-Iztech

2. Install the following Python libraries: Sympy, pandas, pytorch, transformers.

## Datasets

- ALG514 (514 math problems)
- SingleEQ89 (89 math problems)
- SingleEQ396 (396 math problems)
- SVAMP762 (762 math problems)
- SVAMP1000 (1000 math problems)

## Steps for Replication of Our Paper's Results

1. Generate questions from the math problems:
- Select one of the datasets.
- There is a "tools.py" file in the QG-Iztech folder. Replace it with the "tools__for_qg_Iztech.py" provided by us.
- Scroll down to the last few lines of this file. Replace read_json function's input with the path of the selected dataset's json file.
- Replace the results file in the "f" variable with a path for a new txt file. For example; "<dataset_name>_all_generated_questions.txt".
- Run the tools.py code to retrieve the txt file containing all generated questions.
  
2. Run "question_answerer.py" for the "<dataset_name>_all_generated questions.txt" and retrieve a file called "<dataset_name>_Q_and_A.txt".

3. Run "organize_question.py" for the "<dataset_name>_Q_and_A.txt" file. It is possible to edit the name of the folder that stores the organized questions. For example; "<dataset_name>_organized_questions".

4. Open the "num_assigner_tools.py" file in the "number_assigners" folder. Replace the path on the 131st line with the path of your "<dataset_name>_organized_questions" folder.

5. Finally, run "test_all_question.py" to acquire the results.
