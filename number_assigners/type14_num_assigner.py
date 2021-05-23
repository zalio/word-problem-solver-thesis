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
    def __init__(self, n1="0", n2="0", n3="0", n4="0"):
        self.n1 = float(n1)
        self.n2 = float(n2)
        self.n3 = float(n3)
        self.n4 = float(n4)

    def solve_equation(self):
        x = Symbol("x")
        y = Symbol("y")
        answer = solve([self.n1 * x - self.n2 * y - self.n3, x + y - self.n4], x, y)
        return answer

    def __str__(self):
        return "n1 = " + str(self.n1) + " ; n2 = " + str(self.n2) + " ; n3 = " + str(self.n3) + \
               " ; n4 = " + str(self.n4)


class Type14Question:
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

        n1_n2 = find_n1_n2_according_to_word_times(prioritized_numbers, self.original_question)
        n3_n4 = ["", ""]
        if n1_n2 == ["", ""]:
            n1_n2 = find_n1_n2_according_by_grouping_similar_words(prioritized_numbers, self.original_question)
        if n1_n2 != ["", ""]:
            n3_n4 = find_remaining_numbers_for_the_last_slots(prioritized_numbers, n1_n2)

        if n1_n2 == ["", ""] or n3_n4 == ["", ""]:
            return None
        predicted_n1, predicted_n2 = assign_numbers_according_to_their_order_in_question(n1_n2, self.original_question)
        predicted_n4, predicted_n3 = assign_numbers_according_to_their_order_in_question(n3_n4, self.original_question)

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


def find_n1_n2_according_to_word_times(prioritized_numbers, original_question):
    n1_n2 = []
    original_split = original_question.replace('. ', ' ').replace('?', '').replace(',', '').split()
    for i in range(len(original_split)):
        original_split[i] = original_split[i].lower()
        if original_split[i] == "twice" and original_split[i] in prioritized_numbers:
            n1_n2.append(original_split[i])
        elif original_split[i] == "times" and original_split[i - 1] in prioritized_numbers:
            n1_n2.append(original_split[i - 1])
    if len(n1_n2) == 2:
        return n1_n2
    return ["", ""]


def find_n1_n2_according_by_grouping_similar_words(prioritized_numbers, original_question):
    numbers_and_their_following_words = []
    original_split = original_question.replace('. ', ' ').replace('?', '').replace(',', '').split()
    for i in range(len(original_split) - 1):
        if (original_split[i] in prioritized_numbers and
           [original_split[i], original_split[i + 1]] not in numbers_and_their_following_words):
            numbers_and_their_following_words.append([original_split[i], original_split[i + 1]])

    temp_nums = []
    temp_following_words = []
    n1_n2 = []
    selected_num_and_word = []
    if len(numbers_and_their_following_words) == 4:
        for i in numbers_and_their_following_words:
            if i[1] in temp_following_words:
                selected_num_and_word = i
                break
            else:
                temp_nums.append(i[0])
                temp_following_words.append(i[1])
        if not selected_num_and_word:
            for i in numbers_and_their_following_words:
                if i[1][-1] == "s":
                    i[1] = i[1][:-1]
                if i[1] in temp_following_words:
                    selected_num_and_word = i
                    break
                else:
                    temp_nums.append(i[0])
                    temp_following_words.append(i[1])

        if selected_num_and_word:
            for i in numbers_and_their_following_words:
                if i[0] != selected_num_and_word[0] and i[1] == selected_num_and_word[1]:
                    n1_n2.append(i[0])
                    break
            n1_n2.append(selected_num_and_word[0])
            if len(n1_n2) == 2:
                return n1_n2
    return ["", ""]


def find_remaining_numbers_for_the_last_slots(prioritized_numbers, predicted_numbers):
    copy_prioritized = prioritized_numbers.copy()
    copy_prioritized.remove(predicted_numbers[0])
    copy_prioritized.remove(predicted_numbers[1])
    if len(copy_prioritized) == 2:
        return copy_prioritized
    return ["", ""]


def assign_numbers_according_to_their_order_in_question(predicted_numbers, original_question):
    original_split = original_question.replace('. ', ' ').replace('?', '').replace(',', '').split()
    ordered_numbers = []
    for i in range(len(original_split)):
        original_split[i] = original_split[i].lower()
        if original_split[i] == "2" and original_split[i - 2] == "sum":
            continue
        if original_split[i] in predicted_numbers:
            ordered_numbers.append(original_split[i])
            predicted_numbers.remove(original_split[i])
            break
    ordered_numbers.append(predicted_numbers[0])
    return ordered_numbers[0], ordered_numbers[1]


def read_type14_questions():
    return read_all_questions_from_file("../organized_questions/type_14.txt", Type14Question,
                                        first_symbol_to_look_for="*")


if __name__ == "__main__":
    all_type14_questions = read_type14_questions()
    acc_value = test_all_same_type_questions(all_type14_questions, "14")
    print("\n", "~" * 100, "\n====> Accuracy Value for Type 14 Questions =", acc_value * 100, "%")
