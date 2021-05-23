from sympy import *
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
    def __init__(self, n1="0", n2="0", n3="0", n4="0"):
        self.n1 = float(n1)
        self.n2 = float(n2)
        self.n3 = float(n3)
        self.n4 = float(n4)

    def solve_equation(self):
        x = Symbol("x")
        y = Symbol("y")
        answer = solve([self.n1 * x + self.n2 * y - self.n3, x - self.n4 * y], x, y)
        return answer

    def __str__(self):
        return "n1 = " + str(self.n1) + " ; n2 = " + str(self.n2) + " ; n3 = " + str(self.n3) + \
               " ; n4 = " + str(self.n4)


class Type21Question:
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

        predicted_n4 = assign_n4(prioritized_numbers, self.original_question)

        if predicted_n4 == "":
            return None
        predicted_n1, predicted_n2, predicted_n3 = assign_all_remaining_numbers(prioritized_numbers,
                                                                                self.generated_questions,
                                                                                self.original_question)

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
        if len(prioritized_numbers) < 4:
            if (i == "1" or i == "2") and i not in backup_numbers:
                backup_numbers.append(i)
            elif i not in prioritized_numbers:
                prioritized_numbers.append(i)
    if len(prioritized_numbers) < 4:
        for i in all_related_number_strings:
            i = i.lower()
            if (i == "one" or i == "two") and i not in backup_numbers:
                backup_numbers.append(i)
            elif i not in prioritized_numbers:
                prioritized_numbers.append(i)

    while len(prioritized_numbers) < 4 and len(backup_numbers) > 0:
        prioritized_numbers.append(backup_numbers[0])
        backup_numbers.pop(0)
    return prioritized_numbers, backup_numbers


def assign_n4(prioritized_numbers, original_question):
    original_split = original_question.replace('. ', ' ').replace('?', '').replace(',', '').replace('-', ' ').split()
    n4 = ""
    for i in range(len(original_split)):
        original_split[i] = original_split[i].lower()
        if original_split[i] == "times" and original_split[i - 1] in prioritized_numbers:
            n4 = original_split[i - 1]
        elif original_split[i] == "twice":
            n4 = "twice"

    prioritized_numbers.remove(n4)
    return n4


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


def assign_all_remaining_numbers(prioritized_numbers, generated_questions, original_question):
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
                continue
            elif len(temp_pair) > 2:
                possible_pairs = itertools.combinations(temp_pair, 2)
                found_pairs += possible_pairs
                continue
        if not i.ignore_answer:
            temp_pair = []
            answer_split = i.answer.replace('.', '').replace('?', '').replace("  ", ".").replace(' , ', '').split()
            for j in answer_split:
                if j in prioritized_numbers and j not in temp_pair:
                    temp_pair.append(j)
            if len(temp_pair) == 2:
                found_pairs.append(temp_pair)
                continue
            elif len(temp_pair) > 2:
                possible_pairs = itertools.combinations(temp_pair, 2)
                found_pairs += possible_pairs
                continue

    copy_prioritized = prioritized_numbers.copy()
    most_common_pair = find_most_common_element_in_list(found_pairs)
    if found_pairs == [] or most_common_pair == ["", ""]:
        n1, n2 = assign_numbers_according_to_their_order_in_question(prioritized_numbers, original_question)
        copy_prioritized.remove(n1)
        copy_prioritized.remove(n2)
        n3 = copy_prioritized[0]
    else:
        n1, n2 = most_common_pair[0], most_common_pair[1]
        copy_prioritized.remove(n1)
        copy_prioritized.remove(n2)
        n3 = copy_prioritized[0]
    return n1, n2, n3


def assign_numbers_according_to_their_order_in_question(predicted_numbers, original_question):
    original_split = original_question.replace('. ', ' ').replace('?', '').replace(',', '').replace('-', ' ').split()
    ordered_numbers = []
    copy_predicted = predicted_numbers.copy()
    for i in range(len(original_split)):
        original_split[i] = original_split[i].lower()
        if original_split[i] in copy_predicted:
            ordered_numbers.append(original_split[i])
            copy_predicted.remove(original_split[i])
        if len(ordered_numbers) == 2:
            break

    return ordered_numbers[0], ordered_numbers[1]


def read_type21_questions():
    return read_all_questions_from_file("../organized_questions/type_21.txt", Type21Question,
                                        first_symbol_to_look_for="*")


if __name__ == "__main__":
    all_type21_questions = read_type21_questions()
    acc_value = test_all_same_type_questions(all_type21_questions, "21")
    print("\n", "~" * 100, "\n====> Accuracy Value for Type 21 Questions =", acc_value * 100, "%")
