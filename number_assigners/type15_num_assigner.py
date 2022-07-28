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
        answer = solve([self.n1 * x + self.n2 * y - self.n3, x + y - self.n4], x, y)
        return answer

    def __str__(self):
        return "n1 = " + str(self.n1) + " ; n2 = " + str(self.n2) + " ; n3 = " + str(self.n3) + \
               " ; n4 = " + str(self.n4)


class Type15Question:
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
        found_pairs = find_two_pairs_of_numbers(prioritized_numbers, self.generated_questions, self.original_question)

        if found_pairs == [["", ""], ["", ""]]:
            return None
        n1_n2, n3_n4 = distinguish_n1_n2_and_n3_n4_pairs(found_pairs, self.original_question)
        predicted_n1, predicted_n2 = assign_numbers_according_to_their_order_in_question(n1_n2, self.original_question)

        predicted_n3, predicted_n4 = assign_n3_n4_according_to_common_following_words(predicted_n1, predicted_n2,
                                                                                      n3_n4, self.original_question)
        if predicted_n3 == "" or predicted_n3 == "":
            predicted_n3, predicted_n4 = assign_n3_n4_according_to_their_values(n3_n4, self.original_question)

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

            original_split = self.original_question.replace('. ', ' ').replace('?', '').\
                replace(',', '').replace('-', ' ').split()
            if "%" in original_split or "cents" in original_split or "percent" in original_split:
                self.predicted_equation.n1 = self.predicted_equation.n1 * 0.01
                self.predicted_equation.n2 = self.predicted_equation.n2 * 0.01

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


def find_two_pairs_of_numbers(prioritized_numbers, generated_questions, original_question):
    found_pairs = []
    for i in generated_questions:
        if not i.ignore_generated_q:
            generated_split = i.generated.replace('. ', ' ').replace('?', '').replace(',', '').replace('-', ' ').split()
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
        if len(found_pairs) == 1:
            break

    if len(found_pairs) == 0:
        original_split = original_question.replace('. ', ' ').replace('?', '').replace(',', '')\
            .replace('-', ' ').split()
        for i in range(len(original_split)):
            if original_split[i] == "and":
                temp_pair = find_two_num_around_word_and(prioritized_numbers, original_split, i)
                if temp_pair != ["", ""] and temp_pair not in found_pairs and reversed(temp_pair) not in found_pairs:
                    found_pairs.append(temp_pair)

    if len(found_pairs) == 0:
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


def distinguish_n1_n2_and_n3_n4_pairs(found_pairs, original_question):
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

    sum_of_first_pair = first_pair_1 + first_pair_2
    sum_of_second_pair = second_pair_1 + second_pair_2

    n1_n2, n3_n4 = ["", ""], ["", ""]
    original_split = original_question.replace('. ', ' ').replace('?', '').replace(',', '').replace('-', ' ').split()
    if "%" in original_split or "percent" in original_split or "cents" in original_split:
        for i in range(len(original_split)):
            original_split[i] = original_split[i].lower()
            if original_split[i] == "%" or original_split[i] == "percent" or original_split[i] == "cents":
                if original_split[i - 1] in found_pairs[0]:
                    n1_n2 = found_pairs[0]
                    n3_n4 = found_pairs[1]
                elif original_split[i - 1] in found_pairs[1]:
                    n1_n2 = found_pairs[1]
                    n3_n4 = found_pairs[0]
    else:
        if sum_of_first_pair > sum_of_second_pair:
            n1_n2 = found_pairs[1]
            n3_n4 = found_pairs[0]
        else:
            n1_n2 = found_pairs[0]
            n3_n4 = found_pairs[1]

    return n1_n2, n3_n4


def assign_numbers_according_to_their_order_in_question(predicted_numbers, original_question):
    original_split = original_question.replace('. ', ' ').replace('?', '').replace(',', '').replace('-', ' ').split()
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


def assign_n3_n4_according_to_common_following_words(predicted_n1, predicted_n2, n3_n4_pair, original_question):
    original_split = original_question.replace('. ', ' ').replace('?', '').replace(',', '').replace('-', ' ').split()
    following_words = []
    for i in range(len(original_split) - 1):
        original_split[i] = original_split[i].lower()
        if original_split[i] == predicted_n1 or original_split[i] == predicted_n2:
            following_words.append(original_split[i + 1])

    n3, n4 = "", ""
    for i in range(len(original_split)):
        original_split[i] = original_split[i].lower()
        if original_split[i] in n3_n4_pair and (original_split[i + 1] in following_words or
                                                (original_split[i + 1] == "dollars" and "cents" in following_words)):
            n3 = original_split[i]
            n3_n4_pair.remove(n3)
            n4 = n3_n4_pair[0]
            break
    return n3, n4


def assign_n3_n4_according_to_their_values(n3_n4_pair, original_question):
    original_split = original_question.replace('. ', ' ').replace('?', '').replace(',', '').replace('-', ' ').split()
    try:
        float_1 = float(n3_n4_pair[0])
    except ValueError:
        float_1 = float(numbers_written_with_letters_dict[n3_n4_pair[0]])
    try:
        float_2 = float(n3_n4_pair[1])
    except ValueError:
        float_2 = float(numbers_written_with_letters_dict[n3_n4_pair[1]])
    if "%" in original_split or "percent" in original_split or "dimes" in original_split or "nickels" in original_split:
        if float_1 < float_2:
            n3 = n3_n4_pair[0]
            n4 = n3_n4_pair[1]
        else:
            n3 = n3_n4_pair[1]
            n4 = n3_n4_pair[0]
    else:
        if float_1 < float_2:
            n3 = n3_n4_pair[1]
            n4 = n3_n4_pair[0]
        else:
            n3 = n3_n4_pair[0]
            n4 = n3_n4_pair[1]
    return n3, n4


def read_type15_questions():
    return read_all_questions_from_file("type_15.txt", Type15Question,
                                        first_symbol_to_look_for="*")


if __name__ == "__main__":
    all_type15_questions = read_type15_questions()
    acc_value = test_all_same_type_questions(all_type15_questions, "15")
    print("\n", "~" * 100, "\n====> Accuracy Value for Type 15 Questions =", acc_value * 100, "%")
