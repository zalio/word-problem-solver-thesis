
import pandas as pd
import re

df = pd.read_json('./data/alg514.json')

df = df[['sQuestion', 'lEquations', 'templateType']]


def extract_num_from_df_questions(dataframe):
    num_from_each_question = []
    for i in dataframe['sQuestion']:
        matches = re.findall(r"[-+]?\d*\.\d+|\d+", i)
        num_from_each_question.append(matches)
        # print("i = ", i, "--->", matches)
    return num_from_each_question


def extract_num_from_df_equations(dataframe):
    num_from_each_equation = []
    for i in dataframe['lEquations']:
        matches = []
        for j in range(len(i)):
            temp_matches = re.findall(r"[-+]?\d*\.\d+|\d+", i[j])
            for k in temp_matches:
                matches.append(k)
        num_from_each_equation.append(matches)
    return num_from_each_equation


def convert_all_number_strings_to_floats(number_strings_list):
    converted_list = []
    for i in number_strings_list:
        temp_list_for_each_group = []
        for j in range(len(i)):
            temp_list_for_each_group.append(float(i[j]))
        converted_list.append(temp_list_for_each_group)
    return converted_list


def print_each_extraction(dataframe, extracted_numbers, extraction_type="sQuestion"):
    for i in range(len(dataframe[extraction_type])):
        print("Extracted numbers:", extracted_numbers[i], "-->", extraction_type, "=", dataframe[extraction_type][i])


num_from_questions = extract_num_from_df_questions(df)
converted_num_from_questions = convert_all_number_strings_to_floats(num_from_questions)
# print("Num_from_questions ==>", converted_num_from_questions)
print_each_extraction(df, converted_num_from_questions)
print("\nLength of important number groups from questions =", len(converted_num_from_questions), "\n")

print("~" * 50)
print()

num_from_equations = extract_num_from_df_equations(df)
converted_num_from_equations = convert_all_number_strings_to_floats(num_from_equations)
# print("Num_from_equations ==>", converted_num_from_equations)
print_each_extraction(df, converted_num_from_equations, extraction_type="lEquations")
print("\nLength of important number groups from equations =", len(converted_num_from_equations))
