from sympy import *
import numpy as np
from number_assigners.num_assigner_tools import GeneratedQuestion
from number_assigners.num_assigner_tools import eliminate_questions_without_any_numbers
from number_assigners.num_assigner_tools import discover_all_numbers
from number_assigners.num_assigner_tools import eliminate_useless_questions
from number_assigners.num_assigner_tools import eliminate_very_long_questions
from number_assigners.num_assigner_tools import test_all_same_type_questions
from number_assigners.num_assigner_tools import numbers_written_with_letters_dict
from number_assigners.num_assigner_tools import read_all_questions_from_file


class EquationSet:
    def __init__(self, n1="0", n2="0", n3="0", n4="0"):
        self.n1 = float(n1)
        self.n2 = float(n2)
        self.n3 = float(n3)
        self.n4 = float(n4)

    def solve_equation(self):
        x = Symbol("x")
        y = Symbol("y")
        answer = solve([(x + y) * self.n1 - self.n2, (x - y) * self.n3 - self.n4], x, y)
        return answer

    def __str__(self):
        return "n1 = " + str(self.n1) + " ; n2 = " + str(self.n2) + " ; n3 = " + str(self.n3) + \
               " ; n4 = " + str(self.n4)


class Type16Question:
    def __init__(self, original_question, num_from_solution):
        self.original_question = original_question
        self.solution_equation = EquationSet(num_from_solution[0], num_from_solution[1], num_from_solution[2],
                                             num_from_solution[3])
        self.generated_questions = []
        self.predicted_equation = EquationSet()

    def organize_generated_q_and_a(self, generated_q_lines):
        for line in generated_q_lines:
            split_q_and_a = line.split(" --> ")
            temp_generated = GeneratedQuestion(split_q_and_a[0], split_q_and_a[1])
            self.generated_questions.append(temp_generated)

    def predict_equation_from_generated_q(self):
        eliminate_questions_without_any_numbers(self.generated_questions)
        eliminate_useless_questions(self.generated_questions)
        eliminate_very_long_questions(self.generated_questions, 40)

        all_discovered_numbers, all_related_number_strings = discover_all_numbers(self.original_question)

        prioritized_numbers, backup_numbers = prioritize_discovered_numbers(all_discovered_numbers,
                                                                            all_related_number_strings)
        predicted_n2, predicted_n4 = assign_n2_n4(prioritized_numbers)
        if predicted_n2 == "" or predicted_n4 == "":
            return None

        predicted_n1, predicted_n3 = assign_n1_n3_according_to_generated_questions(prioritized_numbers, predicted_n2,
                                                                                   self.generated_questions)

        if predicted_n1 == "" or predicted_n2 == "" or predicted_n3 == "" or predicted_n4 == "":
            return None
        else:
            try:
                self.predicted_equation.n1 = float(predicted_n1)
            except ValueError:
                self.predicted_equation.n1 = float(numbers_written_with_letters_dict[predicted_n1])
            try:
                self.predicted_equation.n2 = float(predicted_n2)
            except ValueError:
                self.predicted_equation.n2 = float(numbers_written_with_letters_dict[predicted_n2])
            try:
                self.predicted_equation.n3 = float(predicted_n3)
            except ValueError:
                self.predicted_equation.n3 = float(numbers_written_with_letters_dict[predicted_n3])
            try:
                self.predicted_equation.n4 = float(predicted_n4)
            except ValueError:
                self.predicted_equation.n4 = float(numbers_written_with_letters_dict[predicted_n4])

            return self.predicted_equation


def prioritize_discovered_numbers(all_discovered_numbers, all_related_number_strings):
    prioritized_numbers = []
    backup_numbers = []
    for i in all_discovered_numbers:
        if len(prioritized_numbers) < 3:
            if (i == "1" or i == "2") and i not in backup_numbers:
                backup_numbers.append(i)
            elif i not in prioritized_numbers:
                prioritized_numbers.append(i)
    if len(prioritized_numbers) < 3:
        for i in all_related_number_strings:
            i = i.lower()
            if (i == "one" or i == "two") and i not in backup_numbers:
                backup_numbers.append(i)
            elif i not in prioritized_numbers:
                prioritized_numbers.append(i)

    while len(prioritized_numbers) < 3 and len(backup_numbers) > 0:
        prioritized_numbers.append(backup_numbers[0])
        backup_numbers.pop(0)
    return prioritized_numbers, backup_numbers


def assign_n2_n4(prioritized_numbers):
    if len(prioritized_numbers) != 3:
        return "", ""
    float_prioritized_numbers = []
    for i in prioritized_numbers:
        try:
            float_prioritized_numbers.append(float(i))
        except ValueError:
            float_prioritized_numbers.append(float(numbers_written_with_letters_dict[i]))
    max_num_index = np.argmax(float_prioritized_numbers)
    max_num = prioritized_numbers.pop(max_num_index)
    return max_num, max_num


def assign_n1_n3_according_to_generated_questions(prioritized_numbers, predicted_n2, generated_questions):
    scores_for_pairs = {}
    for i in prioritized_numbers:
        scores_for_pairs[i] = 0

    for i in generated_questions:
        if not i.ignore_generated_q or not i.ignore_answer:
            generated_split = i.generated.replace('. ', ' ').replace('?', '').replace(',', '').replace('-', ' ').split()
            answer_split = i.answer.replace('.', '').replace('?', '').replace("  ", ".").replace(' , ', '').split()
            if predicted_n2 in generated_split and prioritized_numbers[0] in generated_split:
                scores_for_pairs[prioritized_numbers[0]] += 1
            if predicted_n2 in generated_split and prioritized_numbers[1] in generated_split:
                scores_for_pairs[prioritized_numbers[1]] += 1
            if predicted_n2 in answer_split and prioritized_numbers[0] in answer_split:
                scores_for_pairs[prioritized_numbers[0]] += 1
            if predicted_n2 in answer_split and prioritized_numbers[1] in answer_split:
                scores_for_pairs[prioritized_numbers[1]] += 1
            if predicted_n2 in answer_split and prioritized_numbers[0] in generated_split:
                scores_for_pairs[prioritized_numbers[0]] += 1
            if predicted_n2 in answer_split and prioritized_numbers[1] in generated_split:
                scores_for_pairs[prioritized_numbers[1]] += 1
            if predicted_n2 in generated_split and prioritized_numbers[0] in answer_split:
                scores_for_pairs[prioritized_numbers[0]] += 1
            if predicted_n2 in generated_split and prioritized_numbers[1] in answer_split:
                scores_for_pairs[prioritized_numbers[1]] += 1

    n1, n3 = "", ""
    if scores_for_pairs[prioritized_numbers[0]] > scores_for_pairs[prioritized_numbers[1]]:
        n1 = prioritized_numbers[0]
        n3 = prioritized_numbers[1]
    elif scores_for_pairs[prioritized_numbers[0]] < scores_for_pairs[prioritized_numbers[1]]:
        n1 = prioritized_numbers[1]
        n3 = prioritized_numbers[0]
    elif scores_for_pairs[prioritized_numbers[0]] == scores_for_pairs[prioritized_numbers[1]]:
        try:
            float_1 = float(prioritized_numbers[0])
        except ValueError:
            float_1 = float(numbers_written_with_letters_dict[prioritized_numbers[0]])
        try:
            float_2 = float(prioritized_numbers[1])
        except ValueError:
            float_2 = float(numbers_written_with_letters_dict[prioritized_numbers[1]])
        if float_1 < float_2:
            n1 = prioritized_numbers[0]
            n3 = prioritized_numbers[1]
        else:
            n1 = prioritized_numbers[1]
            n3 = prioritized_numbers[0]
    return n1, n3


def read_type16_questions():
    return read_all_questions_from_file("type_16.txt", Type16Question,
                                        first_symbol_to_look_for="+")


if __name__ == "__main__":
    all_type16_questions = read_type16_questions()
    acc_value = test_all_same_type_questions(all_type16_questions, "16")
    print("\n", "~" * 100, "\n====> Accuracy Value for Type 16 Questions =", acc_value * 100, "%")
