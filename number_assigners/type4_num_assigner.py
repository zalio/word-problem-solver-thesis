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
    def __init__(self, n1="0", n2="0", n3="0"):
        self.n1 = float(n1)
        self.n2 = float(n2)
        self.n3 = float(n3)

    def solve_equation(self):
        x = Symbol("x")
        answer = solve([self.n1 * x - self.n2 - self.n3], x)
        return answer

    def __str__(self):
        return "n1 = " + str(self.n1) + " ; n2 = " + str(self.n2) + " ; n3 = " + str(self.n3)


class Type4Question:
    def __init__(self, original_question, num_from_solution):
        self.original_question = original_question
        self.solution_equation = EquationSet(num_from_solution[0], num_from_solution[1], num_from_solution[2])
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
        eliminate_very_long_questions(self.generated_questions, 30)

        all_discovered_numbers, all_related_number_strings = discover_all_numbers(self.original_question)

        prioritized_numbers, backup_numbers = prioritize_discovered_numbers(all_discovered_numbers,
                                                                            all_related_number_strings)
        n1_n2_pair, predicted_n3 = find_n1_n2_pair_and_assign_n3(prioritized_numbers, self.generated_questions)

        predicted_n1, predicted_n2 = "", ""
        if predicted_n3 != "":
            predicted_n1, predicted_n2 = assign_n1_n2_in_correct_order(predicted_n3,
                                                                       prioritized_numbers, self.original_question)

        if predicted_n1 == "" or predicted_n2 == "" or predicted_n3 == "":
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
            return self.predicted_equation


def prioritize_discovered_numbers(all_discovered_numbers, all_related_number_strings):
    prioritized_numbers = []
    backup_numbers = []
    for i in all_discovered_numbers:
        if (i == "1" or i == "2") and i not in backup_numbers:
            backup_numbers.append(i)
        elif i not in prioritized_numbers:
            prioritized_numbers.append(i)
    for i in all_related_number_strings:
        if (i == "one" or i == "two") and i not in backup_numbers:
            backup_numbers.append(i)
        elif i not in prioritized_numbers:
            prioritized_numbers.append(i)

    while len(prioritized_numbers) < 3 and len(backup_numbers) > 0:
        prioritized_numbers.append(backup_numbers[0])
        backup_numbers.pop(0)
    return prioritized_numbers, backup_numbers


def find_n1_n2_pair_and_assign_n3(prioritized_numbers, generated_questions):
    if "twice" in prioritized_numbers:
        prioritized_numbers[prioritized_numbers.index("twice")] = "2"
    pair_scores = {prioritized_numbers[0] + " " + prioritized_numbers[1]: 0,
                   prioritized_numbers[0] + " " + prioritized_numbers[2]: 0,
                   prioritized_numbers[1] + " " + prioritized_numbers[2]: 0}
    for i in generated_questions:
        if not i.ignore_generated_q:
            num_from_generated = re.findall(r'\d*\.?\d+', i.generated.replace('twice', '2').replace('. ', ' ')
                                            .replace('?', '').replace(',', ''))
            if len(num_from_generated) == 2:
                if ((num_from_generated[0] == prioritized_numbers[0] and
                    num_from_generated[1] == prioritized_numbers[1]) or
                        (num_from_generated[1] == prioritized_numbers[0] and
                         num_from_generated[0] == prioritized_numbers[1])):
                    pair_scores[prioritized_numbers[0] + " " + prioritized_numbers[1]] += 1
                elif ((num_from_generated[0] == prioritized_numbers[0] and
                       num_from_generated[1] == prioritized_numbers[2]) or
                        (num_from_generated[1] == prioritized_numbers[0] and
                         num_from_generated[0] == prioritized_numbers[2])):
                    pair_scores[prioritized_numbers[0] + " " + prioritized_numbers[2]] += 1
                elif ((num_from_generated[0] == prioritized_numbers[1] and
                       num_from_generated[1] == prioritized_numbers[2]) or
                        (num_from_generated[1] == prioritized_numbers[1] and
                         num_from_generated[0] == prioritized_numbers[2])):
                    pair_scores[prioritized_numbers[1] + " " + prioritized_numbers[2]] += 1
        if not i.ignore_answer:
            num_from_answer = re.findall(r'\d*\.?\d+', i.answer.replace('twice', '2').replace('.', '').replace('?', '').
                                         replace("  ", ".").replace(' , ', ''))
            if len(num_from_answer) == 2:
                if ((num_from_answer[0] == prioritized_numbers[0] and
                     num_from_answer[1] == prioritized_numbers[1]) or
                        (num_from_answer[1] == prioritized_numbers[0] and
                         num_from_answer[0] == prioritized_numbers[1])):
                    pair_scores[prioritized_numbers[0] + " " + prioritized_numbers[1]] += 1
                elif ((num_from_answer[0] == prioritized_numbers[0] and
                       num_from_answer[1] == prioritized_numbers[2]) or
                      (num_from_answer[1] == prioritized_numbers[0] and
                       num_from_answer[0] == prioritized_numbers[2])):
                    pair_scores[prioritized_numbers[0] + " " + prioritized_numbers[2]] += 1
                elif ((num_from_answer[0] == prioritized_numbers[1] and
                       num_from_answer[1] == prioritized_numbers[2]) or
                      (num_from_answer[1] == prioritized_numbers[1] and
                       num_from_answer[0] == prioritized_numbers[2])):
                    pair_scores[prioritized_numbers[1] + " " + prioritized_numbers[2]] += 1

    max_score = 0
    max_score_key = "1 9999999"
    for k, v in pair_scores.items():
        if v > max_score:
            max_score = v
            max_score_key = k
        elif v == max_score:
            current_key_difference = abs(float(k.split()[0]) - float(k.split()[1]))
            max_key_difference = abs(float(max_score_key.split()[0]) - float(max_score_key.split()[1]))
            if current_key_difference < max_key_difference:
                max_score = v
                max_score_key = k

    n1_n2_pair = max_score_key.split(" ")
    for i in prioritized_numbers:
        if i not in n1_n2_pair:
            return n1_n2_pair, i
    return ["", ""], ""


def assign_n1_n2_in_correct_order(predicted_n3, prioritized_numbers, original_question):
    copy_prioritized = prioritized_numbers.copy()
    copy_prioritized.remove(predicted_n3)
    original_split = original_question.replace('twice', '2').replace('. ', ' ').replace('?', '')\
        .replace(',', '').split()
    temp_n1 = ""
    temp_n2 = ""
    if "number" in original_split:
        index_of_first_number_word = original_split.index("number")
        for i in range(index_of_first_number_word, -1, -1):
            if original_split[i] in copy_prioritized:
                temp_n1 = original_split[i]
                copy_prioritized.remove(temp_n1)
                temp_n2 = copy_prioritized[0]
                break
    elif "twice" in original_split:
        temp_n1 = "2"
        copy_prioritized.remove("twice")
        temp_n2 = copy_prioritized[0]
    else:
        if copy_prioritized[0] < copy_prioritized[1]:
            temp_n1 = copy_prioritized[0]
            temp_n2 = copy_prioritized[1]
        else:
            temp_n1 = copy_prioritized[1]
            temp_n2 = copy_prioritized[0]
    return temp_n1, temp_n2


def fix_solution_numbers_order(solution_line, _):
    num_from_equations = re.findall(r'\d*\.?\d+', solution_line)
    for i in solution_line:
        if i == "*":
            return num_from_equations[0] + "---" + num_from_equations[1] + "---" + num_from_equations[2]
        elif i == "=":
            return num_from_equations[1] + "---" + num_from_equations[2] + "---" + num_from_equations[0]
    return solution_line


def read_type4_questions():
    return read_all_questions_from_file("../organized_questions/type_4.txt", Type4Question,
                                        fix_solution_function=fix_solution_numbers_order)


if __name__ == "__main__":
    all_type4_questions = read_type4_questions()
    acc_value = test_all_same_type_questions(all_type4_questions, "4")
    print("\n", "~" * 100, "\n====> Accuracy Value for Type 4 Questions =", acc_value * 100, "%")
