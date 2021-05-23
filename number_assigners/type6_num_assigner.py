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
        answer = solve([self.n1 * x + self.n2 * y - self.n3, x - self.n4 - y], x, y)
        return answer

    def __str__(self):
        return "n1 = " + str(self.n1) + " ; n2 = " + str(self.n2) + " ; n3 = " + str(self.n3) \
               + " ; n4 = " + str(self.n4)


class Type6Question:
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

        grouped_numbers, group_type = group_prioritized_numbers(prioritized_numbers, self.generated_questions,
                                                                self.original_question)

        predicted_n1 = ""
        predicted_n2 = ""
        predicted_n3 = ""
        predicted_n4 = ""
        if group_type == "2+2":
            predicted_n1, predicted_n2, predicted_n3, predicted_n4 = assign_for_2_2_case(grouped_numbers[0],
                                                                                         prioritized_numbers,
                                                                                         self.original_question)
        elif group_type == "2+1+1":
            predicted_n1, predicted_n2, predicted_n3, predicted_n4 = assign_for_2_1_1_case(grouped_numbers,
                                                                                           prioritized_numbers,
                                                                                           self.original_question)
        elif group_type == "2+1":
            predicted_n1, predicted_n2, predicted_n3, predicted_n4 = assign_for_2_1_case(grouped_numbers[0],
                                                                                         prioritized_numbers)

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
        if (i == "1" or i == "2" or 1950 < float(i) < 2020) and i not in backup_numbers:
            backup_numbers.append(i)
        elif i not in prioritized_numbers:
            prioritized_numbers.append(i)
    for i in all_related_number_strings:
        if (i == "one" or i == "two") and i not in backup_numbers:
            backup_numbers.append(i)
        elif i not in prioritized_numbers:
            prioritized_numbers.append(i)

    while len(prioritized_numbers) < 4 and len(backup_numbers) > 0:
        prioritized_numbers.append(backup_numbers[0])
        backup_numbers.pop(0)
    if "two" in prioritized_numbers:
        prioritized_numbers.remove("two")
    elif "Two" in prioritized_numbers:
        prioritized_numbers.remove("Two")
    return prioritized_numbers, backup_numbers


def check_if_similar_words(word_1, word_2):
    if word_1[-1] == "s":
        word_1 = word_1[:-1]
    if word_2[-1] == "s":
        word_2 = word_2[:-1]

    if word_1 == word_2:
        return True
    words = [word_1, word_2]
    if ("cent" in words and "dollar" in words) or ("kilometer" in words and "km" in words):
        return True
    return False


def check_numbers_around_word_and_in_original_q(prioritized_numbers, original_split):
    possible_new_num_group = []
    if len(prioritized_numbers) == 4 and "and" in original_split:
        index_of_word_and = original_split.index("and")
        last_index = index_of_word_and + 6
        if last_index > len(original_split):
            last_index = len(original_split)
        for i in range(index_of_word_and + 1, last_index):
            if original_split[i] in prioritized_numbers:
                possible_new_num_group.append(original_split[i])
                break
        first_index = index_of_word_and - 5
        if first_index < 0:
            first_index = 0
        for i in range(first_index, index_of_word_and):
            if original_split[i] in prioritized_numbers:
                possible_new_num_group.append(original_split[i])
                break
        if len(possible_new_num_group) == 2:
            copy_prioritized = prioritized_numbers.copy()
            for j in possible_new_num_group:
                copy_prioritized.remove(j)
            return copy_prioritized, "2+1+1"
    return [], "?"


def group_prioritized_numbers(prioritized_numbers, generated_questions, original_question):
    all_numbers_and_their_following_words = []
    for i in generated_questions:
        if not i.ignore_generated_q:
            generated_split = i.generated.replace('. ', ' ').replace('?', '').replace(',', '').split()
            for j in range(len(generated_split) - 1):
                if generated_split[j] in prioritized_numbers:
                    all_numbers_and_their_following_words.append([generated_split[j], generated_split[j + 1]])
        if not i.ignore_answer:
            answer_split = i.answer.replace('.', '').replace('?', '').replace("  ", ".").replace(' , ', '').split()
            for j in range(len(answer_split) - 1):
                if answer_split[j] in prioritized_numbers:
                    all_numbers_and_their_following_words.append([answer_split[j], answer_split[j + 1]])

    original_split = original_question.replace('. ', ' ').replace('?', '').replace(',', '').split()
    for i in range(len(original_split) - 1):
        if original_split[i] in prioritized_numbers:
            all_numbers_and_their_following_words.append([original_split[i], original_split[i + 1]])

    unique_numbers_and_their_following_words = []
    for i in all_numbers_and_their_following_words:
        if i not in unique_numbers_and_their_following_words:
            unique_numbers_and_their_following_words.append(i)

    grouped_numbers = []
    for i in unique_numbers_and_their_following_words:
        for j in unique_numbers_and_their_following_words:
            if i[0] != j[0] and (i[1] == j[1] or check_if_similar_words(i[1], j[1])) \
                    and [i[0], j[0]] not in grouped_numbers and [j[0], i[0]] not in grouped_numbers:
                grouped_numbers.append([i[0], j[0]])

    if len(prioritized_numbers) == 4 and len(grouped_numbers) == 2:
        return grouped_numbers, "2+2"
    elif len(prioritized_numbers) == 4 and len(grouped_numbers) == 1:
        return grouped_numbers, "2+1+1"
    elif len(prioritized_numbers) == 3 and len(grouped_numbers) == 1:
        return grouped_numbers, "2+1"
    elif len(prioritized_numbers) == 3 and "double" in original_split:
        copy_prioritized = prioritized_numbers.copy()
        copy_prioritized.remove("double")
        return [copy_prioritized], "2+1"
    else:
        return check_numbers_around_word_and_in_original_q(prioritized_numbers, original_split)


def assign_for_2_1_1_case(grouped_numbers, prioritized_numbers, original_question):
    n1, n2, n3, n4 = "", "", "", ""
    if len(grouped_numbers) == 1:
        grouped_numbers = grouped_numbers[0]
    try:
        float_grouped_num1 = float(grouped_numbers[0])
    except ValueError:
        float_grouped_num1 = float(numbers_written_with_letters_dict[grouped_numbers[0]])
    try:
        float_grouped_num2 = float(grouped_numbers[1])
    except ValueError:
        float_grouped_num2 = float(numbers_written_with_letters_dict[grouped_numbers[1]])
    if float_grouped_num1 > float_grouped_num2:
        n3 = grouped_numbers[0]
        n4 = grouped_numbers[1]
    else:
        n3 = grouped_numbers[1]
        n4 = grouped_numbers[0]

    copy_prioritized = prioritized_numbers.copy()

    for i in grouped_numbers:
        copy_prioritized.remove(i)
    if "one" in copy_prioritized:
        copy_prioritized.remove("one")
    elif "One" in copy_prioritized:
        copy_prioritized.remove("One")

    original_split = original_question.replace('. ', ' ').replace('?', '').replace(',', '').split()
    for i in original_split:
        if i in copy_prioritized and n1 == "" and n2 == "":
            n1 = i
        elif i in copy_prioritized and n2 == "":
            n2 = i

    if len(copy_prioritized) == 1:
        n1 = copy_prioritized[0]
        n2 = copy_prioritized[0]
    elif "each" in original_split:
        if n1 == "2":
            n1 = n2
        elif n2 == "2":
            n2 = n1
    return n1, n2, n3, n4


def assign_for_2_2_case(grouped_numbers, prioritized_numbers, original_question):
    copy_prioritized = prioritized_numbers.copy()
    for i in grouped_numbers:
        copy_prioritized.remove(i)
    try:
        float_grouped_num1 = float(grouped_numbers[0])
    except ValueError:
        float_grouped_num1 = float(numbers_written_with_letters_dict[grouped_numbers[0]])
    try:
        float_grouped_num2 = float(grouped_numbers[1])
    except ValueError:
        float_grouped_num2 = float(numbers_written_with_letters_dict[grouped_numbers[1]])
    try:
        float_prioritized_num1 = float(copy_prioritized[0])
    except ValueError:
        float_prioritized_num1 = float(numbers_written_with_letters_dict[copy_prioritized[0]])
    try:
        float_prioritized_num2 = float(copy_prioritized[1])
    except ValueError:
        float_prioritized_num2 = float(numbers_written_with_letters_dict[copy_prioritized[1]])

    n1, n2, n3, n4 = "", "", "", ""
    if (float_grouped_num1 + float_grouped_num2) > (float_prioritized_num1 + float_prioritized_num2):
        n1_n2 = [copy_prioritized[0], copy_prioritized[1]]
        n3_n4 = [float_grouped_num1, float_grouped_num2]
        if n3_n4[0] > n3_n4[1]:
            n3 = grouped_numbers[0]
            n4 = grouped_numbers[1]
        else:
            n3 = grouped_numbers[1]
            n4 = grouped_numbers[0]
    else:
        n1_n2 = [grouped_numbers[0], grouped_numbers[1]]
        n3_n4 = [float_prioritized_num1, float_prioritized_num2]
        if n3_n4[0] > n3_n4[1]:
            n3 = copy_prioritized[0]
            n4 = copy_prioritized[1]
        else:
            n3 = copy_prioritized[1]
            n4 = copy_prioritized[0]

    original_split = original_question.replace('. ', ' ').replace('?', '').replace(',', '').split()
    for i in original_split:
        if i in n1_n2 and n1 == "" and n2 == "":
            n1 = i
        elif i in n1_n2 and n2 == "":
            n2 = i
    return n1, n2, n3, n4


def assign_for_2_1_case(grouped_numbers, prioritized_numbers):
    copy_prioritized = prioritized_numbers.copy()
    for i in grouped_numbers:
        copy_prioritized.remove(i)
    n1, n2 = copy_prioritized[0], copy_prioritized[0]

    try:
        float_grouped_num1 = float(grouped_numbers[0])
    except ValueError:
        float_grouped_num1 = float(numbers_written_with_letters_dict[grouped_numbers[0]])
    try:
        float_grouped_num2 = float(grouped_numbers[1])
    except ValueError:
        float_grouped_num2 = float(numbers_written_with_letters_dict[grouped_numbers[1]])
    if float_grouped_num1 > float_grouped_num2:
        n3 = grouped_numbers[0]
        n4 = grouped_numbers[1]
    else:
        n3 = grouped_numbers[1]
        n4 = grouped_numbers[0]
    return n1, n2, n3, n4


def read_type6_questions():
    return read_all_questions_from_file("../organized_questions/type_6.txt", Type6Question,
                                        first_symbol_to_look_for="*")


if __name__ == "__main__":
    all_type6_questions = read_type6_questions()
    acc_value = test_all_same_type_questions(all_type6_questions, "6")
    print("\n", "~" * 100, "\n====> Accuracy Value for Type 6 Questions =", acc_value * 100, "%")
