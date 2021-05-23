import pandas as pd
from pntl import tree_kernel
from pntl.tools import generate

# This .py file needs to be in the same folder as qg_iztech's pntl folder. 
# This will only work if it is able call generate function of qg_iztech.

df = pd.read_json('alg514.json')

all_questions = df['sQuestion'].tolist()

f = open("all_generated_questions.txt", "w")

for i in range(len(all_questions)):
    print("*** Question", i, "-", all_questions[i], "\n===> Generated questions:\n")
    generated_questions = generate(all_questions[i])
    print("\n*********************************************************************\n")

    f.write("*** " + all_questions[i] + "\n")
    f.write(generated_questions + "~~~\n")

f.close()
