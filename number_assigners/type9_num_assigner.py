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
        y = Symbol("y")
        answer = solve([self.n1 * x - self.n2 - y, x + y - self.n3], x, y)
        return answer

    def __str__(self):
        return "n1 = " + str(self.n1) + " ; n2 = " + str(self.n2) + " ; n3 = " + str(self.n3)


class Type9Question:
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
        eliminate_very_long_questions(self.generated_questions, 40)

        all_discovered_numbers, all_related_number_strings = discover_all_numbers(self.original_question)

        prioritized_numbers, backup_numbers = prioritize_discovered_numbers(all_discovered_numbers,
                                                                            all_related_number_strings)

        predicted_n3 = assign_n3_according_to_sum_word(prioritized_numbers, self.original_question)
        if predicted_n3 == "":
            predicted_n3 = assign_n3_by_looking_for_a_lone_number(prioritized_numbers, self.generated_questions)

        predicted_n1, predicted_n2 = assign_n1_and_n2(prioritized_numbers, self.original_question, predicted_n3)

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


def assign_n3_according_to_sum_word(prioritized_numbers, original_question):
    original_split = original_question.replace('. ', ' ').replace('?', '').replace(',', '').split()
    if "sum" not in original_split:
        return ""
    has_passed_beyond_word_sum = False
    n3 = ""
    for i in original_split:
        if i == "sum":
            has_passed_beyond_word_sum = True
        if i in prioritized_numbers and has_passed_beyond_word_sum:
            n3 = i
            break
    return n3


def assign_n3_by_looking_for_a_lone_number(prioritized_numbers, generated_questions):
    prioritized_num_scores = {}
    for i in prioritized_numbers:
        prioritized_num_scores[i] = 0

    for i in generated_questions:
        if not i.ignore_generated_q:
            num_from_generated = re.findall(r'\d*\.?\d+', i.generated.replace('. ', ' ').replace('?', '')
                                            .replace(',', ''))
            generated_split = i.generated.replace('. ', ' ').replace('?', '').replace(',', '').split()
            for j in generated_split:
                if j in prioritized_numbers:
                    if len(num_from_generated) == 1:
                        prioritized_num_scores[j] += 1
                    else:
                        prioritized_num_scores[j] -= 1
        if not i.ignore_answer:
            num_from_answer = re.findall(r'\d*\.?\d+', i.answer.replace('.', '').replace('?', '')
                                         .replace("  ", ".").replace(' , ', ''))
            answer_split = i.answer.replace('.', '').replace('?', '').replace("  ", ".").replace(' , ', '').split()
            for j in answer_split:
                if j in prioritized_numbers:
                    if len(num_from_answer) == 1:
                        prioritized_num_scores[j] += 1
                    else:
                        prioritized_num_scores[j] -= 1
    max_score = 0
    key_with_max_score = ""
    for k, v in prioritized_num_scores.items():
        if v > max_score:
            max_score = v
            key_with_max_score = k
        elif v > 0 and v == max_score:
            try:
                float_k = float(k)
            except ValueError:
                float_k = float(numbers_written_with_letters_dict[k])
            try:
                float_key_with_max_score = float(key_with_max_score)
            except ValueError:
                float_key_with_max_score = float(numbers_written_with_letters_dict[key_with_max_score])
            if float_k > float_key_with_max_score:
                max_score = v
                key_with_max_score = k
    return key_with_max_score


def assign_n1_and_n2(prioritized_numbers, original_question, selected_n3):
    copy_prioritized = prioritized_numbers.copy()
    copy_prioritized.remove(selected_n3)
    if len(copy_prioritized) != 2:
        return "", ""
    original_split = original_question.replace('. ', ' ').replace('?', '').replace(',', '').split()
    if "times" in original_split or "twice" in original_split:
        n1 = ""
        for i in range(1, len(original_split)):
            if original_split[i] == "times" and original_split[i - 1] in prioritized_numbers:
                n1 = original_split[i - 1]
            elif original_split[i] == "twice":
                n1 = "twice"
        copy_prioritized.remove(n1)
        n2 = copy_prioritized[0]
        return n1, n2
    try:
        float_1 = float(copy_prioritized[0])
    except ValueError:
        float_1 = float(numbers_written_with_letters_dict[copy_prioritized[0]])
    try:
        float_2 = float(copy_prioritized[1])
    except ValueError:
        float_2 = float(numbers_written_with_letters_dict[copy_prioritized[1]])
    if float_1 > float_2:
        n2 = float_1
        n1 = float_2
    else:
        n2 = float_2
        n1 = float_1
    return n1, n2


def fix_solution_numbers_order(solution_line, first_symbol_to_look_for):
    split_solution_line = solution_line.split(" and ")
    all_possible_symbols = ["+", "-", "*", "/", "="]
    all_possible_symbols.remove(first_symbol_to_look_for)
    if len(split_solution_line) > 1:
        for i in split_solution_line[0]:
            if i == first_symbol_to_look_for:
                return split_solution_line[1] + " and " + split_solution_line[0]
            elif i in all_possible_symbols:
                return solution_line
    return solution_line


def read_type9_questions():
    return read_all_questions_from_file("../organized_questions/type_9.txt", Type9Question,
                                        fix_solution_function=fix_solution_numbers_order,
                                        first_symbol_to_look_for="+")


if __name__ == "__main__":
    all_type9_questions = read_type9_questions()
    acc_value = test_all_same_type_questions(all_type9_questions, "9")
    print("\n", "~" * 100, "\n====> Accuracy Value for Type 9 Questions =", acc_value * 100, "%")
