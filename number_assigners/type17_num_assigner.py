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
    def __init__(self, n1="0", n2="0", n3="0", n4="0"):
        self.n1 = float(n1)
        self.n2 = float(n2)
        self.n3 = float(n3)
        self.n4 = float(n4)

    def solve_equation(self):
        x = Symbol("x")
        answer = solve([self.n2 + self.n1 * x - self.n4 - self.n3 * x], x)
        return answer

    def __str__(self):
        return "n1 = " + str(self.n1) + " ; n2 = " + str(self.n2) + " ; n3 = " + str(self.n3) + \
               " ; n4 = " + str(self.n4)


class Type17Question:
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
        eliminate_very_long_questions(self.generated_questions, 30)

        all_discovered_numbers, all_related_number_strings = discover_all_numbers(self.original_question)

        prioritized_numbers, backup_numbers = prioritize_discovered_numbers(all_discovered_numbers,
                                                                            all_related_number_strings)

        found_pairs = find_two_pairs_of_numbers(prioritized_numbers, self.generated_questions)
        if found_pairs == [["", ""], ["", ""]]:
            return None

        predicted_n2, predicted_n1 = assign_numbers_according_to_their_order_in_question(found_pairs[0],
                                                                                         self.original_question)
        predicted_n4, predicted_n3 = assign_numbers_according_to_their_order_in_question(found_pairs[1],
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
            if (i == "1" or i == "2" or 1950 < float(i) < 2020) and i not in backup_numbers:
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


def find_two_pairs_of_numbers(prioritized_numbers, generated_questions):
    found_pairs = []
    for i in generated_questions:
        temp_pair = []
        if not i.ignore_generated_q:
            generated_split = i.generated.replace('. ', ' ').replace('?', '').replace(',', '')\
                .replace('-', ' ').split()
            for j in range(len(generated_split)):
                generated_split[j] = generated_split[j].lower()
                if generated_split[j] in prioritized_numbers and generated_split[j] not in temp_pair:
                    temp_pair.append(generated_split[j])
        if not i.ignore_answer:
            answer_split = i.answer.replace('.', '').replace('?', '').replace("  ", ".").replace(' , ', '').split()
            for j in range(len(answer_split)):
                answer_split[j] = answer_split[j].lower()
                if answer_split[j] in prioritized_numbers and answer_split[j] not in temp_pair:
                    temp_pair.append(answer_split[j])
        if len(temp_pair) == 2 and temp_pair not in found_pairs and reversed(temp_pair) not in found_pairs:
            found_pairs.append(temp_pair)
            break

    if len(found_pairs) == 2:
        return found_pairs

    if len(found_pairs) == 1:
        copy_prioritized = prioritized_numbers.copy()
        for i in found_pairs:
            for j in i:
                j = j.lower()
                if j in copy_prioritized:
                    copy_prioritized.remove(j)
        if len(copy_prioritized) == 2:
            found_pairs.append([copy_prioritized[0], copy_prioritized[1]])
            return found_pairs
    return [["", ""], ["", ""]]


def assign_numbers_according_to_their_order_in_question(predicted_numbers, original_question):
    original_split = original_question.replace('. ', ' ').replace('?', '').replace(',', '').replace('-', ' ').split()
    ordered_numbers = []
    copy_predicted = predicted_numbers.copy()
    for i in range(len(original_split)):
        original_split[i] = original_split[i].lower()
        if original_split[i] == "2" and original_split[i - 2] == "sum":
            continue
        if original_split[i] in copy_predicted:
            ordered_numbers.append(original_split[i])
            copy_predicted.remove(original_split[i])
            break
    ordered_numbers.append(copy_predicted[0])
    return ordered_numbers[0], ordered_numbers[1]


def fix_solution_numbers_order(solution_line, _):
    num_from_equations = re.findall(r'\d*\.?\d+', solution_line)
    for i in solution_line:
        if i == "*":
            return num_from_equations[1] + "---" + num_from_equations[0] + "---" + \
                   num_from_equations[3] + "---" + num_from_equations[2]
    return solution_line


def read_type17_questions():
    return read_all_questions_from_file("../organized_questions/type_17.txt", Type17Question,
                                        fix_solution_function=fix_solution_numbers_order)


if __name__ == "__main__":
    all_type17_questions = read_type17_questions()
    acc_value = test_all_same_type_questions(all_type17_questions, "17")
    print("\n", "~" * 100, "\n====> Accuracy Value for Type 17 Questions =", acc_value * 100, "%")
