import pandas as pd

df = pd.read_json('alg514.json')

df = df[['sQuestion', 'lEquations', 'templateType']]

f1 = open("all_generated_Q_and_A.txt", "r")
lines_f1 = f1.readlines()
f1.close()

for i in range(22): 
    f2 = open("organized_questions/type_" + str(i) + ".txt", "w")
    for index, row in df.iterrows():
        if row['templateType'] == i:
            temp_q = row['sQuestion']
            flag = False
            for line in lines_f1:
                # print(line[:-1])
                # print(temp_q)
                if line == ("*** " + temp_q + "\n"):
                    flag = True
                if flag and line == "~~~\n":
                    flag = False
                    f2.write("==> Solution Equation: " + row['lEquations'][0])
                    if len(row['lEquations']) == 2:
                        f2.write(" and " + row['lEquations'][1])
                    f2.write("\n" + line + "\n")
                    break
                if flag:
                    f2.write(line)
    f2.close()
