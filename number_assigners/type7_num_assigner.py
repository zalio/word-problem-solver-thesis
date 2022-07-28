from sympy import *
import re
from number_assigners.num_assigner_tools import GeneratedQuestion
from number_assigners.num_assigner_tools import eliminate_questions_without_any_numbers
from number_assigners.num_assigner_tools import discover_all_numbers
from number_assigners.num_assigner_tools import eliminate_useless_questions
from number_assigners.num_assigner_tools import eliminate_very_long_questions
from number_assigners.num_assigner_tools import test_all_same_type_questions
from number_assigners.num_assigner_tools import numbers_written_with_letters_dict
from number_assigners.num_assigner_tools import read_all_questions_from_file


class EquationSet:
    def __init__(self, n1="0", n2="0"):
        self.n1 = float(n1)
        self.n2 = float(n2)

    def solve_equation(self):
        x = Symbol("x")
        answer = solve([self.n1 / self.n2 - x], x)
        return answer

    def __str__(self):
        return "n1 = " + str(self.n1) + " ; n2 = " + str(self.n2)


class Type7Question:
    def __init__(self, original_question, num_from_solution):
        self.original_question = original_question
        self.solution_equation = EquationSet(num_from_solution[0], num_from_solution[1])
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

        predicted_n1, predicted_n2 = assign_n1_and_n2(prioritized_numbers, self.generated_questions)
        if predicted_n1 == "" or predicted_n2 == "":
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

            return self.predicted_equation


def prioritize_discovered_numbers(all_discovered_numbers, all_related_number_strings):
    prioritized_numbers = []
    backup_numbers = []
    for i in all_discovered_numbers:
        if (i == "1" or i == "2" or 1950 < float(i) < 2020) and i not in backup_numbers:
            backup_numbers.append(i)
        elif i not in prioritized_numbers:
            prioritized_numbers.append(i)
    for i in all_related_number_strings:
        if (i == "one" or i == "two") and i not in backup_numbers:
            backup_numbers.append(i)
        elif i not in prioritized_numbers:
            prioritized_numbers.append(i)

    while len(prioritized_numbers) < 2 and len(backup_numbers) > 0:
        prioritized_numbers.append(backup_numbers[0])
        backup_numbers.pop(0)
    return prioritized_numbers, backup_numbers


def assign_n1_and_n2(prioritized_numbers, generated_questions):
    if len(prioritized_numbers) > 2:
        count_for_prioritized = {}
        for i in prioritized_numbers:
            count_for_prioritized[i] = 0
        for i in generated_questions:
            if not i.ignore_generated_q:
                generated_split = i.generated.replace('. ', ' ').replace('?', '').replace(',', '').split()
                for j in generated_split:
                    if j in prioritized_numbers:
                        count_for_prioritized[j] += 1
            if not i.ignore_answer:
                answer_split = i.answer.replace('.', '').replace('?', '').replace("  ", ".").replace(' , ', '').split()
                for j in answer_split:
                    if j in prioritized_numbers:
                        count_for_prioritized[j] += 1

        key_of_max1 = max(count_for_prioritized, key=count_for_prioritized.get)
        count_for_prioritized.pop(key_of_max1)
        key_of_max2 = max(count_for_prioritized, key=count_for_prioritized.get)
        try:
            float_max1 = float(key_of_max1)
        except ValueError:
            float_max1 = float(numbers_written_with_letters_dict[key_of_max1])
        try:
            float_max2 = float(key_of_max2)
        except ValueError:
            float_max2 = float(numbers_written_with_letters_dict[key_of_max2])

        if float_max1 > float_max2:
            n1 = key_of_max1
            n2 = key_of_max2
        else:
            n1 = key_of_max2
            n2 = key_of_max1
        return n1, n2
    elif len(prioritized_numbers) == 2:
        temp_num1, temp_num2 = prioritized_numbers[0], prioritized_numbers[1]
        try:
            float_max1 = float(temp_num1)
        except ValueError:
            float_max1 = float(numbers_written_with_letters_dict[temp_num1])
        try:
            float_max2 = float(temp_num2)
        except ValueError:
            float_max2 = float(numbers_written_with_letters_dict[temp_num2])
        if float_max1 > float_max2:
            n1 = temp_num1
            n2 = temp_num2
        else:
            n1 = temp_num2
            n2 = temp_num1
        return n1, n2
    return "", ""


def fix_solution_numbers_order(solution_line, _):
    num_from_equations = re.findall(r'\d*\.?\d+', solution_line)
    for i in solution_line:
        if i == "*":
            return num_from_equations[1] + "---" + num_from_equations[0]
        elif i == "/" or i == "=":
            return num_from_equations[0] + "---" + num_from_equations[1]
    return solution_line


def read_type7_questions():
    return read_all_questions_from_file("type_7.txt", Type7Question,
                                        fix_solution_function=fix_solution_numbers_order)


if __name__ == "__main__":
    all_type7_questions = read_type7_questions()
    acc_value = test_all_same_type_questions(all_type7_questions, "7")
    print("\n", "~" * 100, "\n====> Accuracy Value for Type 7 Questions =", acc_value * 100, "%")
