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
    def __init__(self, n1="0", n2="0", n3="0"):
        self.n1 = float(n1)
        self.n2 = float(n2)
        self.n3 = float(n3)

    def solve_equation(self):
        x = Symbol("x")
        y = Symbol("y")
        answer = solve([x + y - self.n1, x - self.n2 * y - self.n3], x, y)
        return answer

    def __str__(self):
        return "n1 = " + str(self.n1) + " ; n2 = " + str(self.n2) + " ; n3 = " + str(self.n3)


class Type13Question:
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
        predicted_n1 = assign_n1_according_to_words_sum_or_total(prioritized_numbers, self.generated_questions)
        predicted_n2 = assign_n2(prioritized_numbers, self.original_question)
        predicted_n3 = ""
        if predicted_n1 != "" and predicted_n2 != "":
            predicted_n3 = assign_remaining_num_to_the_last_slot(prioritized_numbers, predicted_n1, predicted_n2)
        elif predicted_n1 != "" and predicted_n2 == "":
            predicted_n2, predicted_n3 = assign_n2_n3_if_n1_is_selected(prioritized_numbers, predicted_n1)
        elif predicted_n1 == "" and predicted_n2 != "":
            predicted_n1, predicted_n3 = assign_n1_n3_if_n2_is_selected(prioritized_numbers, self.original_question,
                                                                        predicted_n2)

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
        if (i == "1" or i == "2" or 1900 < float(i) < 2020) and i not in backup_numbers:
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


def assign_n1_according_to_words_sum_or_total(prioritized_numbers, generated_questions):
    n1 = ""
    for i in generated_questions:
        generated_split = i.generated.replace('. ', ' ').replace('?', '').replace(',', '').split()
        answer_split = i.answer.replace('.', '').replace('?', '').replace("  ", ".").replace(' , ', '').split()
        words_sum_or_total_exists = False
        for j in generated_split:
            if j[:3] == "sum" or j[:5] == "total":
                words_sum_or_total_exists = True
        for j in answer_split:
            if j[:3] == "sum" or j[:5] == "total":
                words_sum_or_total_exists = True
        prioritized_numbers_near_words_sum_or_total = []
        if words_sum_or_total_exists:
            for j in generated_split:
                if j in prioritized_numbers and j not in prioritized_numbers_near_words_sum_or_total:
                    prioritized_numbers_near_words_sum_or_total.append(j)
            for j in answer_split:
                if j in prioritized_numbers and j not in prioritized_numbers_near_words_sum_or_total:
                    prioritized_numbers_near_words_sum_or_total.append(j)
        if len(prioritized_numbers_near_words_sum_or_total) == 1:
            n1 = prioritized_numbers_near_words_sum_or_total[0]
            break
    return n1


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


def assign_remaining_num_to_the_last_slot(prioritized_numbers, predicted_num1, predicted_num2):
    copy_prioritized = prioritized_numbers.copy()
    copy_prioritized.remove(predicted_num1)
    copy_prioritized.remove(predicted_num2)
    if len(copy_prioritized) == 1:
        return copy_prioritized[0]
    return ""


def assign_n2_n3_if_n1_is_selected(prioritized_numbers, predicted_n1):
    copy_prioritized = prioritized_numbers.copy()
    copy_prioritized.remove(predicted_n1)
    n2, n3 = "", ""
    if len(copy_prioritized) == 2:
        try:
            float_1 = float(copy_prioritized[0])
        except ValueError:
            float_1 = float(numbers_written_with_letters_dict[copy_prioritized[0]])
        try:
            float_2 = float(copy_prioritized[1])
        except ValueError:
            float_2 = float(numbers_written_with_letters_dict[copy_prioritized[1]])
        if float_1 < float_2:
            n2 = float_1
            n3 = float_2
        else:
            n2 = float_2
            n3 = float_1
    return n2, n3


def assign_n1_n3_if_n2_is_selected(prioritized_numbers, original_question, predicted_n2):
    copy_prioritized = prioritized_numbers.copy()
    copy_prioritized.remove(predicted_n2)
    n1, n3 = "", ""
    if len(copy_prioritized) == 2:
        original_split = original_question.replace('. ', ' ').replace('?', '').replace(',', '').split()
        index_of_predicted_n2 = original_split.index(predicted_n2)
        last_index = index_of_predicted_n2 + 7
        if last_index > len(original_split):
            last_index = len(original_split)
        i = 0
        number_found_on_the_right_side = ""
        for i in range(index_of_predicted_n2 + 1, last_index):
            if original_split[i] in prioritized_numbers:
                number_found_on_the_right_side = original_split[i]
                break

        first_index = index_of_predicted_n2 - 6
        if first_index < 0:
            first_index = 0
        j = 0
        number_found_on_the_left_side = ""
        for j in range(first_index, index_of_predicted_n2):
            if original_split[j] in prioritized_numbers:
                number_found_on_the_left_side = original_split[j]
                break

        if number_found_on_the_right_side != "" and number_found_on_the_left_side == "":
            n3 = number_found_on_the_right_side
        elif number_found_on_the_right_side == "" and number_found_on_the_left_side != "":
            n3 = number_found_on_the_left_side
        elif number_found_on_the_right_side == "" and number_found_on_the_left_side == "":
            if i < j:
                n3 = number_found_on_the_right_side
            else:
                n3 = number_found_on_the_left_side
        if n3 != "":
            copy_prioritized.remove(n3)
            if len(copy_prioritized) == 1:
                n1 = copy_prioritized[0]
    return n1, n3


def read_type13_questions():
    return read_all_questions_from_file("../organized_questions/type_13.txt", Type13Question,
                                        first_symbol_to_look_for="+")


if __name__ == "__main__":
    all_type13_questions = read_type13_questions()
    acc_value = test_all_same_type_questions(all_type13_questions, "13")
    print("\n", "~" * 100, "\n====> Accuracy Value for Type 13 Questions =", acc_value * 100, "%")
