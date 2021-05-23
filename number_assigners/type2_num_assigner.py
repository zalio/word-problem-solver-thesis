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
        answer = solve([self.n1 * x - self.n2 - self.n3 * x], x)
        return answer

    def __str__(self):
        return "n1 = " + str(self.n1) + " ; n2 = " + str(self.n2) + " ; n3 = " + \
               str(self.n3)


class Type2Question:
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
        n1_and_n3, predicted_n2 = assign_n2(self.original_question, self.generated_questions, prioritized_numbers)
        predicted_n1 = ""
        predicted_n3 = ""
        if n1_and_n3[0] != "" and n1_and_n3[1] != "":
            try:
                temp_n1 = float(n1_and_n3[0])
            except ValueError:
                temp_n1 = float(numbers_written_with_letters_dict[n1_and_n3[0]])
            try:
                temp_n3 = float(n1_and_n3[1])
            except ValueError:
                temp_n3 = float(numbers_written_with_letters_dict[n1_and_n3[1]])
            if temp_n1 > temp_n3:
                predicted_n1 = n1_and_n3[0]
                predicted_n3 = n1_and_n3[1]
            else:
                predicted_n1 = n1_and_n3[1]
                predicted_n3 = n1_and_n3[0]
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
        if i == "1" or i == "2":
            backup_numbers.append(i)
        else:
            prioritized_numbers.append(i)
    for i in all_related_number_strings:
        if i == "one" or i == "two":
            backup_numbers.append(i)
        else:
            prioritized_numbers.append(i)

    while len(prioritized_numbers) < 3 and len(backup_numbers) > 0:
        prioritized_numbers.append(backup_numbers[0])
        backup_numbers.pop(0)
    return prioritized_numbers, backup_numbers


def list_all_nearby_words_of_a_num(split_words, index_of_num):
    closest_words = []
    index_movement_count = 0
    for i in range(index_of_num, len(split_words)):
        index_movement_count += 1
        if index_movement_count == 4:
            break
        if split_words[i] not in closest_words:
            closest_words.append(split_words[i])
    index_movement_count = 0
    for i in range(index_of_num, 0, -1):
        index_movement_count += 1
        if index_movement_count == 3:
            break
        if split_words[i] not in closest_words:
            closest_words.append(split_words[i])
    return closest_words


def group_most_similar_lists(words_around_prioritized_nums, prioritized_numbers):
    closest_words_of_the_first_prioritized = words_around_prioritized_nums[prioritized_numbers[0]]
    closest_words_of_the_second_prioritized = words_around_prioritized_nums[prioritized_numbers[1]]
    closest_words_of_the_third_prioritized = words_around_prioritized_nums[prioritized_numbers[2]]

    size_intersection_of_1_2 = len(
        set(closest_words_of_the_first_prioritized) & set(closest_words_of_the_second_prioritized))
    size_intersection_of_2_3 = len(
        set(closest_words_of_the_second_prioritized) & set(closest_words_of_the_third_prioritized))
    size_intersection_of_1_3 = len(
        set(closest_words_of_the_first_prioritized) & set(closest_words_of_the_third_prioritized))

    if max([size_intersection_of_1_2, size_intersection_of_2_3, size_intersection_of_1_3]) == size_intersection_of_1_2:
        return [prioritized_numbers[0], prioritized_numbers[1]], prioritized_numbers[2]
    elif max([size_intersection_of_1_2, size_intersection_of_2_3,
              size_intersection_of_1_3]) == size_intersection_of_2_3:
        return [prioritized_numbers[1], prioritized_numbers[2]], prioritized_numbers[0]
    else:
        return [prioritized_numbers[0], prioritized_numbers[2]], prioritized_numbers[1]


def assign_n2(original_question, generated_questions, prioritized_numbers):
    if len(prioritized_numbers) != 3:
        return ["", ""], ""

    words_around_prioritized_nums = {}
    for i in prioritized_numbers:
        words_around_prioritized_nums[i] = []
    for j in generated_questions:
        if not j.ignore_generated_q:
            generated_split = j.generated.replace('. ', ' ').replace('?', '').replace(',', '').split()
            for k in range(len(generated_split)):
                if generated_split[k] in prioritized_numbers:
                    words_around_prioritized_nums[generated_split[k]] += list_all_nearby_words_of_a_num(generated_split,
                                                                                                        k)
        if not j.ignore_answer:
            answer_split = j.answer.replace('.', '').replace('?', '').replace("  ", ".").replace(' , ', '').split()
            for k in range(len(answer_split)):
                if answer_split[k] in prioritized_numbers:
                    words_around_prioritized_nums[answer_split[k]] += list_all_nearby_words_of_a_num(answer_split, k)
    original_split = original_question.replace('. ', ' ').replace('?', '').replace(',', '').split()
    for k in range(len(original_split)):
        if original_split[k] in prioritized_numbers:
            words_around_prioritized_nums[original_split[k]] += list_all_nearby_words_of_a_num(original_split, k)

    keys_of_two_lists_with_most_similar_words, other_key = group_most_similar_lists(words_around_prioritized_nums,
                                                                                    prioritized_numbers)
    return keys_of_two_lists_with_most_similar_words, other_key


def fix_solution_numbers_order(solution_line, _):
    num_order_dict = {"*-=*": [0, 1, 2], "+*=*": [2, 0, 1], "*=*+": [0, 2, 1], "*=+*": [0, 1, 2], "*-*=": [0, 2, 1],
                      "*=*-": [0, 2, 1]}
    symbols_to_look_for = ["*", "-", "=", "+"]
    symbols_of_current_line = ""
    for i in solution_line:
        if i in symbols_to_look_for:
            symbols_of_current_line += i
    current_num_order = num_order_dict[symbols_of_current_line]
    num_from_equations_without_order = re.findall(r'\d*\.?\d+', solution_line)

    num_from_equations_with_order = []
    if current_num_order == [2, 0, 1]:
        num_from_equations_with_order.append(num_from_equations_without_order[2])
        num_from_equations_with_order.append(num_from_equations_without_order[0])
        num_from_equations_with_order.append(num_from_equations_without_order[1])
    elif current_num_order == [0, 2, 1]:
        num_from_equations_with_order.append(num_from_equations_without_order[0])
        num_from_equations_with_order.append(num_from_equations_without_order[2])
        num_from_equations_with_order.append(num_from_equations_without_order[1])
    else:
        num_from_equations_with_order.append(num_from_equations_without_order[0])
        num_from_equations_with_order.append(num_from_equations_without_order[1])
        num_from_equations_with_order.append(num_from_equations_without_order[2])

    if float(num_from_equations_with_order[0]) < float(num_from_equations_with_order[2]):
        temp_num = num_from_equations_with_order[0]
        num_from_equations_with_order[0] = num_from_equations_with_order[2]
        num_from_equations_with_order[2] = temp_num

    fixed_solution_line = (num_from_equations_with_order[0] + "---" + num_from_equations_with_order[1] + "---" +
                           num_from_equations_with_order[2])
    return fixed_solution_line


def read_type2_questions():
    return read_all_questions_from_file("../organized_questions/type_2.txt", Type2Question,
                                        fix_solution_function=fix_solution_numbers_order)


if __name__ == "__main__":
    all_type2_questions = read_type2_questions()
    acc_value = test_all_same_type_questions(all_type2_questions, "2")
    print("\n", "~" * 100, "\n====> Accuracy Value for Type 2 Questions =", round(acc_value * 100), "%")
