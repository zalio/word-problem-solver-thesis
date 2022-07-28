from sympy import *
import numpy as np
import re
from number_assigners.num_assigner_tools import GeneratedQuestion
from number_assigners.num_assigner_tools import eliminate_questions_without_any_numbers
from number_assigners.num_assigner_tools import discover_all_numbers
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
        answer = solve([self.n1 + x - self.n2], x)
        return answer

    def __str__(self):
        return "n1 = " + str(self.n1) + " ; n2 = " + str(self.n2)


class Type3Question:
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
        eliminate_very_long_questions(self.generated_questions, 30)

        all_discovered_numbers, all_related_number_strings = discover_all_numbers(self.original_question)

        prioritized_numbers, backup_numbers = prioritize_discovered_numbers(all_discovered_numbers,
                                                                            all_related_number_strings,
                                                                            self.generated_questions)

        if len(prioritized_numbers) < 2:
            return None
        if prioritized_numbers[0] == ' ' or prioritized_numbers[1] == ' ':
            return None

        temp_num1, temp_num2 = prioritized_numbers[0], prioritized_numbers[1]
        try:
            float_1 = float(temp_num1)
        except ValueError:
            float_1 = float(numbers_written_with_letters_dict[temp_num1])
        try:
            float_2 = float(temp_num2)
        except ValueError:
            float_2 = float(numbers_written_with_letters_dict[temp_num2])
        if float_1 < float_2:
            predicted_n1 = prioritized_numbers[0]
            predicted_n2 = prioritized_numbers[1]
        else:
            predicted_n1 = prioritized_numbers[1]
            predicted_n2 = prioritized_numbers[0]
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


def get_three_following_words_of_a_num(split_words, index_of_num):
    next_three_words = []
    index_movement_count = 0
    for i in range(index_of_num + 1, len(split_words)):
        index_movement_count += 1
        if index_movement_count == 5:
            break
        if split_words[i] not in next_three_words:
            next_three_words.append(split_words[i])
    return next_three_words


def find_closest_numbers_with_most_in_common_words(prioritized_numbers, words_after_each_number):
    grouped_words_for_numbers = {}
    for i in prioritized_numbers:
        temp_words = words_after_each_number[i]
        for j in prioritized_numbers:
            if i != j and (str(i) + " " + str(j)) not in grouped_words_for_numbers and \
                    (str(j) + " " + str(i)) not in grouped_words_for_numbers:
                grouped_words_for_numbers[str(i) + " " + str(j)] = set(temp_words) & set(words_after_each_number[j])

    best_i_j_pairs = []
    for key, value in grouped_words_for_numbers.items():
        if len(value) > 0:
            best_i_j_pairs.append(key)
    if len(best_i_j_pairs) == 1:
        return best_i_j_pairs[0]
    elif len(best_i_j_pairs) == 0:
        return []
    else:
        differences_between_i_and_j = []
        for s in best_i_j_pairs:
            split_s = s.split(" ")
            temp_num1, temp_num2 = split_s[0], split_s[1]
            try:
                float_1 = float(temp_num1)
            except ValueError:
                float_1 = float(numbers_written_with_letters_dict[temp_num1])
            try:
                float_2 = float(temp_num2)
            except ValueError:
                float_2 = float(numbers_written_with_letters_dict[temp_num2])
            differences_between_i_and_j.append(abs(float_1 - float_2))
        index_of_closest_pair = np.argmin(differences_between_i_and_j)
        return best_i_j_pairs[int(index_of_closest_pair)].split(" ")


def select_two_related_numbers(prioritized_numbers, generated_questions):
    words_after_each_number = {}
    for i in prioritized_numbers:
        words_after_each_number[i] = []
    for i in generated_questions:
        if not i.ignore_generated_q:
            generated_split = i.generated.replace('. ', ' ').replace('?', '').replace(',', '').split()
            for j in range(len(generated_split)):
                if generated_split[j] in prioritized_numbers:
                    temp_next_three_words = get_three_following_words_of_a_num(generated_split, j)
                    for k in temp_next_three_words:
                        if k not in words_after_each_number[generated_split[j]]:
                            words_after_each_number[generated_split[j]].append(k)
        if not i.ignore_answer:
            answer_split = i.answer.replace('.', '').replace('?', '').replace("  ", ".").replace(' , ', '').split()
            for j in range(len(answer_split)):
                if answer_split[j] in prioritized_numbers:
                    temp_next_three_words = get_three_following_words_of_a_num(answer_split, j)
                    for k in temp_next_three_words:
                        if k not in words_after_each_number[answer_split[j]]:
                            words_after_each_number[answer_split[j]].append(k)
    closest_pair = find_closest_numbers_with_most_in_common_words(prioritized_numbers, words_after_each_number)
    return closest_pair


def prioritize_discovered_numbers(all_discovered_numbers, all_related_number_strings, generated_questions):
    prioritized_numbers = []
    backup_numbers = []

    if (len(all_discovered_numbers) + len(all_related_number_strings)) == 2:
        prioritized_numbers = all_discovered_numbers + all_related_number_strings
        return prioritized_numbers, backup_numbers

    for i in all_discovered_numbers:
        if i == "1" or i == "2":
            backup_numbers.append(i)
        else:
            prioritized_numbers.append(i)
    for i in all_related_number_strings:
        if i == "one" or i == "two" or i == "dimes":
            backup_numbers.append(i)
        else:
            prioritized_numbers.append(i)

    if len(prioritized_numbers) > 2:
        prioritized_numbers = select_two_related_numbers(prioritized_numbers, generated_questions)

    while len(prioritized_numbers) < 2 and len(backup_numbers) > 0:
        prioritized_numbers.append(backup_numbers[0])
        backup_numbers.pop(0)
    return prioritized_numbers, backup_numbers


def fix_solution_numbers_order(solution_line, _):
    num_from_equations_without_order = re.findall(r'\d*\.?\d+', solution_line)
    if float(num_from_equations_without_order[0]) > float(num_from_equations_without_order[1]):
        return num_from_equations_without_order[1] + "---" + num_from_equations_without_order[0]
    else:
        return num_from_equations_without_order[0] + "---" + num_from_equations_without_order[1]


def read_type3_questions():
    return read_all_questions_from_file("type_3.txt", Type3Question,
                                        fix_solution_function=fix_solution_numbers_order)


if __name__ == "__main__":
    all_type3_questions = read_type3_questions()
    acc_value = test_all_same_type_questions(all_type3_questions, "3")
    print("\n", "~" * 100, "\n====> Accuracy Value for Type 3 Questions =", round(acc_value * 100), "%")
