from sympy import *
import re
import itertools
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
        answer = solve([self.n1 * x + self.n2 * x - self.n3], x)
        return answer

    def __str__(self):
        return "n1 = " + str(self.n1) + " ; n2 = " + str(self.n2) + " ; n3 = " + str(self.n3)


class Type19Question:
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
        eliminate_very_long_questions(self.generated_questions, 50)

        all_discovered_numbers, all_related_number_strings = discover_all_numbers(self.original_question)

        prioritized_numbers, backup_numbers = prioritize_discovered_numbers(all_discovered_numbers,
                                                                            all_related_number_strings)

        n1_n2, predicted_n3 = find_a_pair_among_generated_questions(prioritized_numbers, self.generated_questions,
                                                                    self.original_question)
        predicted_n1, predicted_n2 = n1_n2[0], n1_n2[1]

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


def find_most_common_element_in_list(lst):
    fixed_lst = []
    for i in lst:
        if reversed(i) in fixed_lst:
            fixed_lst.append(reversed(i))
        else:
            fixed_lst.append(i)

    element_counts = {}
    for i in fixed_lst:
        element_counts[str(i[0]) + " " + str(i[1])] = 0
    for i in fixed_lst:
        element_counts[str(i[0]) + " " + str(i[1])] += 1

    max_v = 0
    max_k = ""
    for k, v in element_counts.items():
        if v > max_v:
            max_v = v
            max_k = k
        elif v == max_v and v > 0:
            return ["", ""]
    max_k_pair_values = max_k.split()
    return max_k_pair_values


def find_a_pair_among_generated_questions(prioritized_numbers, generated_questions, original_question):
    found_pairs = []
    for i in generated_questions:
        if not i.ignore_generated_q:
            temp_pair = []
            generated_split = i.generated.replace('. ', ' ').replace('?', '').replace(',', '').split()
            for j in generated_split:
                if j in prioritized_numbers and j not in temp_pair:
                    temp_pair.append(j)
            if len(temp_pair) == 2:
                found_pairs.append(temp_pair)
            elif len(temp_pair) > 2:
                possible_pairs = itertools.combinations(temp_pair, 2)
                found_pairs += possible_pairs
        if not i.ignore_answer:
            temp_pair = []
            answer_split = i.answer.replace('.', '').replace('?', '').replace("  ", ".").replace(' , ', '').split()
            for j in answer_split:
                if j in prioritized_numbers and j not in temp_pair:
                    temp_pair.append(j)
            if len(temp_pair) == 2:
                found_pairs.append(temp_pair)
            elif len(temp_pair) > 2:
                possible_pairs = itertools.combinations(temp_pair, 2)
                found_pairs += possible_pairs

    most_common_pair = find_most_common_element_in_list(found_pairs)
    if found_pairs == [] or most_common_pair == ["", ""]:
        n1_n2, n3 = assign_numbers_according_to_their_order_in_question(prioritized_numbers, original_question)
    else:
        n1_n2 = most_common_pair
        prioritized_numbers.remove(n1_n2[0])
        prioritized_numbers.remove(n1_n2[1])
        n3 = prioritized_numbers[0]
    return n1_n2, n3


def assign_numbers_according_to_their_order_in_question(predicted_numbers, original_question):
    original_split = original_question.replace('. ', ' ').replace('?', '').replace(',', '').replace('-', ' ').split()
    ordered_numbers = []
    copy_predicted = predicted_numbers.copy()
    for i in range(len(original_split)):
        original_split[i] = original_split[i].lower()
        if original_split[i] in copy_predicted:
            ordered_numbers.append(original_split[i])
            copy_predicted.remove(original_split[i])
        if len(ordered_numbers) == 3:
            break

    return [ordered_numbers[0], ordered_numbers[1]], ordered_numbers[2]


def fix_solution_numbers_order(solution_line, _):
    num_from_equations = re.findall(r'\d*\.?\d+', solution_line)
    for i in solution_line:
        if i == "*":
            return num_from_equations[0] + "---" + num_from_equations[1] + "---" + num_from_equations[2]
    return solution_line


def read_type19_questions():
    return read_all_questions_from_file("type_19.txt", Type19Question,
                                        fix_solution_function=fix_solution_numbers_order)


if __name__ == "__main__":
    all_type19_questions = read_type19_questions()
    acc_value = test_all_same_type_questions(all_type19_questions, "19")
    print("\n", "~" * 100, "\n====> Accuracy Value for Type 19 Questions =", acc_value * 100, "%")
