# Question Based Problem Solver

## Installation

1. Download and install question generator program called QG-Iztech. The steps for this can be found here: 
https://github.com/OnurKeklik/Qg-Iztech

2. Install the following Python libraries: 
- sympy-1.10.1 (Necessary for solving mathematical solution equations. Capable of solving single or double variable equation systems.)
- pandas-1.4.3
- pytorch-1.12.0
- transformers-4.20.1


## Datasets

- ALG514 (http://groups.csail.mit.edu/rbg/code/wordprobs/)
- SingleEQ (https://gitlab.cs.washington.edu/ALGES/TACL2015/-/blob/master/questions.json)
- SVAMP (https://github.com/arkilpatel/SVAMP/blob/main/SVAMP.json)

The preprocessed versions of these datasets can be found in the the root folder of the project. The ALG514 dataset has a single preprocessed version with 514 problems. The SingleEq dataset has two different versions with 89 problems and 396 problems. The SVAMP dataset has two different versions with 762 problems and 1000 problems.


## Steps for Replication of Our Paper's Results

1. Generate questions from the math problems:
- Select one of the datasets.
- There is a "tools.py" file in the QG-Iztech folder. Replace it with the "tools__for_qg_Iztech.py" provided by us.
- Scroll down to the last few lines of this file. Replace read_json function's input with the path of the selected dataset's json file.
- Replace the results file in the "f" variable with a path for a new txt file. For example; "<dataset_name>_all_generated_questions.txt".
- Run the tools.py code to retrieve the txt file containing all generated questions.
  
  
2. Run "question_answerer.py" for the "<dataset_name>_all_generated questions.txt" and retrieve a file called "<dataset_name>_Q_and_A.txt".
- The "question_answerer.py" code uses a pre-trained question answering model to answer generated questions from the QG-Iztech code. These generated questions and their answers will serve as extra information during the solution steps of our code. We used BERT-large (https://mccormickml.com/2020/03/10/question-answering-with-a-fine-tuned-BERT/) that has been trained on the SQuAD v1.1 dataset and have not performed any fine-tuning on this machine for our datasets. Thus, we answered all the generated questions from the previous step.


3. Run "organize_questions.py" for the "<dataset_name>_Q_and_A.txt" file. It is possible to edit the name of the folder that stores the organized questions. For example; "<dataset_name>_organized_questions" can be the name of the folder.
- The "organize_questions.py" code seperates all math problems according to their solution equation types and groups them into their own txt file. These txt files are stored in a folder with a name like the one stated above.

4. Open the "num_assigner_tools.py" file in the "number_assigners" folder. Replace the path on the 131st line with the path of your "<dataset_name>_organized_questions" folder.
- The "num_assigner_tools.py" code mainly contains the necessary operations that are used commonly during the number assignment step for the solution equations. The most important detail of this code is that it requires the path of the organized_questions folder, so that the last step can work properly.

5. Finally, run "test_all_question.py" to acquire the results.
