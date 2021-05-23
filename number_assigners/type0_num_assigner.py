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
        answer = solve([x + y - self.n1, x - self.n2 * y + self.n3], x, y)
        return answer

    def __str__(self):
        return "n1 = " + str(self.n1) + " ; n2 = " + str(self.n2) + " ; n3 = " + str(self.n3)


class Type0Question:
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

        best_fit_for_n1 = find_most_fitting_num_for_slot_n1(self.generated_questions, prioritized_numbers)
        potential_n2_or_n3_values = find_n2_and_n3_according_to_word_than(self.generated_questions, prioritized_numbers)
        if potential_n2_or_n3_values[0] == "" or potential_n2_or_n3_values[1] == "":
            potential_n2_or_n3_values = get_n2_and_n3_from_specific_questions(self.generated_questions,
                                                                              prioritized_numbers)
        if best_fit_for_n1 == "":
            best_fit_for_n1 = put_last_num_to_last_slot(prioritized_numbers, potential_n2_or_n3_values)
        ordered_n3_and_n2 = get_passing_orders_of_numbers_in_question(self.original_question, potential_n2_or_n3_values)
        predicted_n1 = best_fit_for_n1
        predicted_n2 = ordered_n3_and_n2[1]
        predicted_n3 = ordered_n3_and_n2[0]
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


def find_closest_num_to_a_word(split_words, index_of_word, prioritized_numbers):
    close_num1 = ""
    close_num_index1 = 0
    close_num2 = ""
    close_num_index2 = 0
    for i in range(index_of_word, len(split_words)):
        if split_words[i] in prioritized_numbers:
            close_num1 = split_words[i]
            close_num_index1 = i
            break
    for i in range(index_of_word, 0, -1):
        if split_words[i] in prioritized_numbers:
            close_num2 = split_words[i]
            close_num_index2 = i
            break
    if close_num1 != "" and close_num_index1 - index_of_word <= index_of_word - close_num_index2:
        return close_num1
    elif close_num2 != "" and close_num_index1 - index_of_word > index_of_word - close_num_index2:
        return close_num2
    else:
        return ""


def find_most_fitting_num_for_slot_n1(generated_questions, prioritized_numbers):
    does_num_fit_n1_score = {}
    for i in prioritized_numbers:
        does_num_fit_n1_score[i] = 0

    for i in generated_questions:
        closest_num = ""
        if not i.ignore_generated_q:
            generated_split = i.generated.replace('. ', ' ').replace('?', '').split()
            for j in range(len(generated_split)):
                if generated_split[j][:3] == "sum":
                    closest_num = find_closest_num_to_a_word(generated_split, j, prioritized_numbers)
                elif generated_split[j][:5] == "total":
                    closest_num = find_closest_num_to_a_word(generated_split, j, prioritized_numbers)
            if closest_num != "":
                does_num_fit_n1_score[closest_num] += 1

        if not i.ignore_answer:
            closest_num = ""
            answer_split = i.answer.replace('.', '').replace('?', '').replace("  ", ".").split()
            for j in range(len(answer_split)):
                if answer_split[j][:3] == "sum":
                    closest_num = find_closest_num_to_a_word(answer_split, j, prioritized_numbers)
                elif answer_split[j][:5] == "total":
                    closest_num = find_closest_num_to_a_word(answer_split, j, prioritized_numbers)
            if closest_num != "":
                does_num_fit_n1_score[closest_num] += 1

    best_fit_for_n1 = max(does_num_fit_n1_score, key=does_num_fit_n1_score.get)
    if does_num_fit_n1_score[best_fit_for_n1] > 0:
        return best_fit_for_n1
    else:
        return ""


def get_closest_neighbor_numbers_of_a_word(split_words, index_of_word, prioritized_numbers):
    close_num_left = ""
    close_num_right = ""
    for i in range(index_of_word, len(split_words)):
        if split_words[i] in prioritized_numbers:
            close_num_right = split_words[i]
            break
    for i in range(index_of_word, 0, -1):
        if split_words[i] in prioritized_numbers:
            close_num_left = split_words[i]
            break
    return close_num_left, close_num_right


def find_n2_and_n3_according_to_word_than(generated_questions, prioritized_numbers):
    for i in generated_questions:
        if not i.ignore_generated_q:
            left_closest, right_closest = "", ""
            generated_split = i.generated.replace('. ', ' ').replace('?', '').split()
            if "than" in generated_split:
                index_of_than = generated_split.index("than")
                left_closest, right_closest = get_closest_neighbor_numbers_of_a_word(generated_split, index_of_than,
                                                                                     prioritized_numbers)
            if left_closest != "" and right_closest != "":
                return left_closest, right_closest

        if not i.ignore_answer:
            left_closest, right_closest = "", ""
            answer_split = i.answer.replace('.', '').replace('?', '').replace("  ", ".").split()
            if "than" in answer_split:
                index_of_than = answer_split.index("than")
                left_closest, right_closest = get_closest_neighbor_numbers_of_a_word(answer_split, index_of_than,
                                                                                     prioritized_numbers)
            if left_closest != "" and right_closest != "":
                return [left_closest, right_closest]
    return ["", ""]


def get_n2_and_n3_from_specific_questions(generated_questions, prioritized_numbers):
    for i in generated_questions:
        temp_n2_or_n3_values = []
        answer_split = i.answer.replace('.', '').replace('?', '').replace("  ", ".").split()
        if "How would you describe" == i.generated[:22]:
            for j in answer_split:
                if j in prioritized_numbers:
                    temp_n2_or_n3_values.append(j)
            if len(temp_n2_or_n3_values) == 2:
                return temp_n2_or_n3_values

        temp_n2_or_n3_values = []
        if "Indicate" == i.generated[:8]:
            for j in answer_split:
                if j in prioritized_numbers:
                    temp_n2_or_n3_values.append(j)
            if len(temp_n2_or_n3_values) == 2:
                return temp_n2_or_n3_values
    return ["", ""]


def put_last_num_to_last_slot(prioritized_numbers, potential_n2_or_n3_values):
    temp_priority_list = prioritized_numbers.copy()
    temp_priority_list.remove(potential_n2_or_n3_values[0])
    temp_priority_list.remove(potential_n2_or_n3_values[1])
    return temp_priority_list[0]


def get_passing_orders_of_numbers_in_question(original_question, numbers_to_look_for):
    ordered_numbers = []
    original_split = original_question.replace('. ', ' ').replace('?', '').split()
    for i in original_split:
        if i == numbers_to_look_for[0] or i == numbers_to_look_for[1]:
            ordered_numbers.append(i)
            if i == numbers_to_look_for[0]:
                ordered_numbers.append(numbers_to_look_for[1])
            else:
                ordered_numbers.append(numbers_to_look_for[0])
            break
    return ordered_numbers


def read_type0_questions():
    return read_all_questions_from_file("../organized_questions/type_0.txt", Type0Question,
                                        first_symbol_to_look_for="+")


if __name__ == "__main__":
    all_type0_questions = read_type0_questions()
    acc_value = test_all_same_type_questions(all_type0_questions, "0")
    print("\n", "~" * 100, "\n====> Accuracy Value for Type 0 Questions =", acc_value * 100, "%")
