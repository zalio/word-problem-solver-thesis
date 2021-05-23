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
    def __init__(self, n1="0", n2="0", n3="0", n4="0", n5="0", n6="0"):
        self.n1 = float(n1)
        self.n2 = float(n2)
        self.n3 = float(n3)
        self.n4 = float(n4)
        self.n5 = float(n5)
        self.n6 = float(n6)

    def solve_equation(self):
        x = Symbol("x")
        y = Symbol("y")
        answer = solve([self.n1 * x + self.n2 * y - self.n3, self.n4 * x + self.n5 * y - self.n6], x, y)
        return answer

    def __str__(self):
        return "n1 = " + str(self.n1) + " ; n2 = " + str(self.n2) + " ; n3 = " + str(self.n3) \
               + "; n4 = " + str(self.n4) + " ; n5 = " + str(self.n5) + " ; n6 = " + str(self.n6)


class Type8Question:
    def __init__(self, original_question, num_from_solution):
        self.original_question = original_question
        self.solution_equation = EquationSet(num_from_solution[0], num_from_solution[1], num_from_solution[2],
                                             num_from_solution[3], num_from_solution[4], num_from_solution[5])
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
                                                                            all_related_number_strings,
                                                                            self.original_question)

        found_pairs = find_three_pairs_of_numbers(prioritized_numbers, self.generated_questions)
        predicted_n1, predicted_n2, predicted_n3, predicted_n4, predicted_n5, predicted_n6 = "", "", "", "", "", ""
        if found_pairs != [["", ""], ["", ""], ["", ""]]:
            predicted_n1, predicted_n2, predicted_n3, predicted_n4, predicted_n5, predicted_n6 = assign_all_numbers(
                prioritized_numbers, self.original_question, found_pairs)

        if (predicted_n1 == "" or predicted_n2 == "" or predicted_n3 == "" or predicted_n4 == "" or
                predicted_n5 == "" or predicted_n6 == ""):
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
            try:
                self.predicted_equation.n5 = float(predicted_n5)
            except ValueError:
                self.predicted_equation.n5 = float(numbers_written_with_letters_dict[predicted_n5])
            try:
                self.predicted_equation.n6 = float(predicted_n6)
            except ValueError:
                self.predicted_equation.n6 = float(numbers_written_with_letters_dict[predicted_n6])

            return self.predicted_equation


def prioritize_discovered_numbers(all_discovered_numbers, all_related_number_strings, original_question):
    for i in range(len(all_related_number_strings)):
        all_related_number_strings[i] = all_related_number_strings[i].lower()
    prioritized_numbers = []
    backup_numbers = []
    repeated_numbers = []
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

    original_split = original_question.replace('. ', ' ').replace('?', '').replace(',', '').split()
    num_in_original = re.findall(r'\d*\.?\d+', original_question.replace('. ', ' ').replace('?', '').replace(',', ''))
    for i in original_split:
        if i in numbers_written_with_letters_dict:
            num_in_original.append(i)
    num_repetitions_in_original = {}
    for i in original_split:
        if i in num_in_original and i not in num_repetitions_in_original.keys():
            num_repetitions_in_original[i] = 0
        elif i in num_in_original:
            num_repetitions_in_original[i] += 1
    for k, v in num_repetitions_in_original.items():
        if v == 1:
            repeated_numbers.append(k)

    if len(prioritized_numbers) < 6 and "1" in backup_numbers:
        prioritized_numbers.append("1")
        backup_numbers.remove("1")
    if len(prioritized_numbers) < 6 and "2" in backup_numbers:
        prioritized_numbers.append("2")
        backup_numbers.remove("2")

    while len(prioritized_numbers) < 6 and len(repeated_numbers) > 0:
        prioritized_numbers.append(repeated_numbers[0])
        repeated_numbers.pop(0)

    while len(prioritized_numbers) < 6 and len(backup_numbers) > 0:
        prioritized_numbers.append(backup_numbers[0])
        backup_numbers.pop(0)
    return prioritized_numbers, backup_numbers


def find_two_num_around_word_and(prioritized_numbers, split_words, index_of_and):
    found_pair = []
    last_index_of_slice = index_of_and + 7
    if last_index_of_slice > len(split_words):
        last_index_of_slice = len(split_words)
    for i in range(index_of_and + 1, last_index_of_slice):
        split_words[i] = split_words[i].lower()
        if split_words[i] in prioritized_numbers:
            found_pair.append(split_words[i])
            break

    first_index_of_slice = index_of_and - 7
    if first_index_of_slice < -1:
        first_index_of_slice = -1
    for i in range(index_of_and - 1, first_index_of_slice, -1):
        split_words[i] = split_words[i].lower()
        if split_words[i] in prioritized_numbers:
            found_pair.append(split_words[i])
            break

    if len(found_pair) == 2:
        return found_pair
    else:
        return ["", ""]


def find_three_pairs_of_numbers(prioritized_numbers, generated_questions):
    found_pairs = []
    for i in generated_questions:
        if not i.ignore_generated_q:
            generated_split = i.generated.replace('. ', ' ').replace('?', '').replace(',', '').split()
            for j in range(len(generated_split)):
                if generated_split[j] == "and":
                    temp_pair = find_two_num_around_word_and(prioritized_numbers, generated_split, j)
                    if temp_pair != ["", ""] and temp_pair not in found_pairs and \
                            reversed(temp_pair) not in found_pairs:
                        found_pairs.append(temp_pair)
        if not i.ignore_answer:
            answer_split = i.answer.replace('.', '').replace('?', '').replace("  ", ".").replace(' , ', '').split()
            for j in range(len(answer_split)):
                if answer_split[j] == "and":
                    temp_pair = find_two_num_around_word_and(prioritized_numbers, answer_split, j)
                    if temp_pair != ["", ""] and temp_pair not in found_pairs and \
                            reversed(temp_pair) not in found_pairs:
                        found_pairs.append(temp_pair)
        if len(found_pairs) == 2:
            break

    copy_prioritized = prioritized_numbers.copy()
    for i in found_pairs:
        for j in i:
            if j in copy_prioritized:
                copy_prioritized.remove(j)

    if len(copy_prioritized) == 2:
        found_pairs.append([copy_prioritized[0], copy_prioritized[1]])
        return found_pairs
    elif len(copy_prioritized) == 4:
        found_pairs.append([copy_prioritized[0], copy_prioritized[1]])
        found_pairs.append([copy_prioritized[2], copy_prioritized[3]])
        return found_pairs
    return [["", ""], ["", ""], ["", ""]]


def assign_all_numbers(prioritized_numbers, original_question, found_pairs):
    try:
        first_pair_1 = float(found_pairs[0][0])
    except ValueError:
        first_pair_1 = float(numbers_written_with_letters_dict[found_pairs[0][0]])
    try:
        first_pair_2 = float(found_pairs[0][1])
    except ValueError:
        first_pair_2 = float(numbers_written_with_letters_dict[found_pairs[0][1]])
    try:
        second_pair_1 = float(found_pairs[1][0])
    except ValueError:
        second_pair_1 = float(numbers_written_with_letters_dict[found_pairs[1][0]])
    try:
        second_pair_2 = float(found_pairs[1][1])
    except ValueError:
        second_pair_2 = float(numbers_written_with_letters_dict[found_pairs[1][1]])
    try:
        third_pair_1 = float(found_pairs[2][0])
    except ValueError:
        third_pair_1 = float(numbers_written_with_letters_dict[found_pairs[2][0]])
    try:
        third_pair_2 = float(found_pairs[2][1])
    except ValueError:
        third_pair_2 = float(numbers_written_with_letters_dict[found_pairs[2][1]])

    sum_of_first_pair = first_pair_1 + first_pair_2
    sum_of_second_pair = second_pair_1 + second_pair_2
    sum_of_third_pair = third_pair_1 + third_pair_2
    if sum_of_first_pair > sum_of_second_pair and sum_of_first_pair > sum_of_third_pair:
        n3_n6_pair = found_pairs[0]
    elif sum_of_second_pair > sum_of_first_pair and sum_of_second_pair > sum_of_third_pair:
        n3_n6_pair = found_pairs[1]
    else:
        n3_n6_pair = found_pairs[2]

    assignment_style_flag = ""
    original_q_sentences = original_question.replace('?', '').replace(',', '').split(". ")
    for i in original_q_sentences:
        if "while" in i:
            original_q_sentences = i.split("while")
            break
        if " or " in i:
            original_q_sentences = i.split(" or ")
            break

    first_2_num_sentence_exists = False
    for i in original_q_sentences:
        original_q_sentence_split = i.split()
        prioritized_count = 0
        for j in original_q_sentence_split:
            j = j.lower()
            if j in prioritized_numbers:
                prioritized_count += 1
        if prioritized_count == 3:
            assignment_style_flag = "1_2 4_5"
            break
        elif prioritized_count == 2:
            first_2_num_sentence_exists = True
        elif first_2_num_sentence_exists and prioritized_count == 1:
            assignment_style_flag = "1_2 4_5"
            break
        else:
            first_2_num_sentence_exists = False
    if assignment_style_flag == "":
        assignment_style_flag = "1_4 2_5"

    if assignment_style_flag == "1_4 2_5":
        n1_n4_pair, n2_n5_pair = ["", ""], ["", ""]
        found_pairs.remove(n3_n6_pair)
        original_split = original_question.replace('. ', ' ').replace('?', '').replace(',', '').split()
        for i in original_split:
            if i in found_pairs[0]:
                n1_n4_pair = found_pairs[0]
                n2_n5_pair = found_pairs[1]
                break
            elif i in found_pairs[1]:
                n1_n4_pair = found_pairs[1]
                n2_n5_pair = found_pairs[0]
                break
        if n1_n4_pair == ["", ""] or n2_n5_pair == ["", ""]:
            n1_n4_pair = found_pairs[0]
            n2_n5_pair = found_pairs[1]

        n1, n2, n3, n4, n5, n6 = "", "", "", "", "", ""
        for i in original_split:
            i = i.lower()
            if i in n1_n4_pair and n1 == "" and n4 == "":
                n1 = i
                n1_n4_pair.remove(i)
            elif i in n1_n4_pair and n4 == "":
                n4 = n1_n4_pair[0]
            elif i in n2_n5_pair and n2 == "" and n5 == "":
                n2 = i
                n2_n5_pair.remove(i)
            elif i in n2_n5_pair and n5 == "":
                n5 = n2_n5_pair[0]
            elif i in n3_n6_pair and n3 == "" and n6 == "":
                n3 = i
                n3_n6_pair.remove(i)
            elif i in n3_n6_pair and n6 == "":
                n6 = n3_n6_pair[0]
        return n1, n2, n3, n4, n5, n6
    else:
        n1_n2_pair, n4_n5_pair = ["", ""], ["", ""]
        found_pairs.remove(n3_n6_pair)
        original_split = original_question.replace('. ', ' ').replace('?', '').replace(',', '').split()
        for i in original_split:
            if i in found_pairs[0]:
                n1_n2_pair = found_pairs[0]
                n4_n5_pair = found_pairs[1]
                break
            elif i in found_pairs[1]:
                n1_n2_pair = found_pairs[1]
                n4_n5_pair = found_pairs[0]
                break
        if n1_n2_pair == ["", ""] or n4_n5_pair == ["", ""]:
            n1_n2_pair = found_pairs[0]
            n4_n5_pair = found_pairs[1]

        n1, n2, n3, n4, n5, n6 = "", "", "", "", "", ""
        for i in original_split:
            i = i.lower()
            if i in n1_n2_pair and n1 == "" and n2 == "":
                n1 = i
                n1_n2_pair.remove(i)
            elif i in n1_n2_pair and n2 == "":
                n2 = n1_n2_pair[0]
            elif i in n4_n5_pair and n4 == "" and n5 == "":
                n4 = i
                n4_n5_pair.remove(i)
            elif i in n4_n5_pair and n5 == "":
                n5 = n4_n5_pair[0]
            elif i in n3_n6_pair and n3 == "" and n6 == "":
                n3 = i
                n3_n6_pair.remove(i)
            elif i in n3_n6_pair and n6 == "":
                n6 = n3_n6_pair[0]
        return n1, n2, n3, n4, n5, n6


def read_type8_questions():
    return read_all_questions_from_file("../organized_questions/type_8.txt", Type8Question)


if __name__ == "__main__":
    all_type8_questions = read_type8_questions()
    acc_value = test_all_same_type_questions(all_type8_questions, "8")
    print("\n", "~" * 100, "\n====> Accuracy Value for Type 8 Questions =", acc_value * 100, "%")
