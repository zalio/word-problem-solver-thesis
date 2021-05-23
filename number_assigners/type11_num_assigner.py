from sympy import *
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
        y = Symbol("y")
        answer = solve([x + y - self.n1, x - self.n2 * y], x, y)
        return answer

    def __str__(self):
        return "n1 = " + str(self.n1) + " ; n2 = " + str(self.n2)


class Type11Question:
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
        eliminate_very_long_questions(self.generated_questions, 30)

        all_discovered_numbers, all_related_number_strings = discover_all_numbers(self.original_question)

        prioritized_numbers, backup_numbers = prioritize_discovered_numbers(all_discovered_numbers,
                                                                            all_related_number_strings)
        predicted_n2 = assign_n2(prioritized_numbers, self.original_question)
        if predicted_n2 != "":
            predicted_n1 = assign_remaining_num_to_the_last_slot(prioritized_numbers, predicted_n2)
        else:
            predicted_n1 = assign_n1_if_still_empty(prioritized_numbers, self.generated_questions)
            predicted_n2 = assign_remaining_num_to_the_last_slot(prioritized_numbers, predicted_n1)

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
        i = i.lower()
        if (i == "one" or i == "two") and i not in backup_numbers:
            backup_numbers.append(i)
        elif i not in prioritized_numbers:
            prioritized_numbers.append(i)

    while len(prioritized_numbers) < 2 and len(backup_numbers) > 0:
        prioritized_numbers.append(backup_numbers[0])
        backup_numbers.pop(0)
    return prioritized_numbers, backup_numbers


def assign_n2(prioritized_numbers, original_question):
    n2 = ""
    original_split = original_question.replace('. ', ' ').replace('?', '').replace(',', '').split()
    for i in range(len(original_split)):
        if (original_split[i] == "twice" or original_split[i] == "thrice") and original_split[i] in prioritized_numbers:
            n2 = original_split[i]
        elif (original_split[i] == "times" or
              original_split[i] == "of") and original_split[i - 1] in prioritized_numbers:
            n2 = original_split[i - 1]
    return n2


def assign_remaining_num_to_the_last_slot(prioritized_numbers, predicted_num):
    copy_prioritized = prioritized_numbers.copy()
    copy_prioritized.remove(predicted_num)
    if len(copy_prioritized) == 1:
        return copy_prioritized[0]
    return ""


def assign_n1_if_still_empty(prioritized_numbers, generated_questions):
    count_for_prioritized = {}
    for i in prioritized_numbers:
        count_for_prioritized[i] = 0
    for i in generated_questions:
        if not i.ignore_answer:
            answer_split = i.answer.replace('.', '').replace('?', '').replace("  ", ".").replace(' , ', '').split()
            if len(answer_split) == 1 and answer_split[0] in prioritized_numbers:
                count_for_prioritized[answer_split[0]] += 1
    max_count = 0
    key_with_max_count = ""
    for k, v in count_for_prioritized.items():
        if v > max_count:
            max_count = v
            key_with_max_count = k
        elif v > 0 and v == max_count:
            try:
                float_k = float(k)
            except ValueError:
                float_k = float(numbers_written_with_letters_dict[k])
            try:
                float_key_with_max_count = float(key_with_max_count)
            except ValueError:
                float_key_with_max_count = float(numbers_written_with_letters_dict[key_with_max_count])
            if float_k > float_key_with_max_count:
                max_count = v
                key_with_max_count = k
    return key_with_max_count


def read_type11_questions():
    return read_all_questions_from_file("../organized_questions/type_11.txt", Type11Question,
                                        first_symbol_to_look_for="+")


if __name__ == "__main__":
    all_type11_questions = read_type11_questions()
    acc_value = test_all_same_type_questions(all_type11_questions, "11")
    print("\n", "~" * 100, "\n====> Accuracy Value for Type 11 Questions =", acc_value * 100, "%")
