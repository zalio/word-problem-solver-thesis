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
        answer = solve([self.n1 * x - self.n2 * y + self.n3, x + y - self.n4], x, y)
        return answer

    def __str__(self):
        return "n1 = " + str(self.n1) + " ; n2 = " + str(self.n2) + " ; n3 = " + str(self.n3) +\
               " ; n4 = " + str(self.n4)


class Type1Question:
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

        predicted_n4 = assign_n4(self.generated_questions, prioritized_numbers)

        predicted_n1, predicted_n2, predicted_n3 = assign_n1_n2_and_n3(self.original_question, prioritized_numbers,
                                                                       predicted_n4)
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
        if i == "1" or i == "2":
            backup_numbers.append(i)
        else:
            prioritized_numbers.append(i)
    for i in all_related_number_strings:
        if i == "one" or i == "two":
            backup_numbers.append(i)
        else:
            prioritized_numbers.append(i)

    while len(prioritized_numbers) < 4 and len(backup_numbers) > 0:
        if "2" in backup_numbers:
            prioritized_numbers.append("2")
            backup_numbers.remove("2")
        else:
            prioritized_numbers.append(backup_numbers[0])
            backup_numbers.pop(0)
    return prioritized_numbers, backup_numbers


def find_closest_num_to_a_word(split_words, index_of_word, prioritized_numbers):
    close_num1 = ""
    close_num_index1 = 0
    close_num2 = ""
    close_num_index2 = 0
    for i in range(index_of_word, len(split_words)):
        if split_words[i] == "2":
            continue
        if split_words[i] in prioritized_numbers:
            close_num1 = split_words[i]
            close_num_index1 = i
            break
    for i in range(index_of_word, 0, -1):
        if split_words[i] == "2":
            continue
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


def assign_n4(generated_questions, prioritized_numbers):
    does_num_fit_n4_score = {}
    for i in prioritized_numbers:
        does_num_fit_n4_score[i] = 0

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
                does_num_fit_n4_score[closest_num] += 1

        if not i.ignore_answer:
            closest_num = ""
            answer_split = i.answer.replace('.', '').replace('?', '').replace("  ", ".").split()
            for j in range(len(answer_split)):
                if answer_split[j][:3] == "sum":
                    closest_num = find_closest_num_to_a_word(answer_split, j, prioritized_numbers)
                elif answer_split[j][:5] == "total":
                    closest_num = find_closest_num_to_a_word(answer_split, j, prioritized_numbers)
            if closest_num != "":
                does_num_fit_n4_score[closest_num] += 1

    best_fit_for_n4 = max(does_num_fit_n4_score, key=does_num_fit_n4_score.get)
    if does_num_fit_n4_score[best_fit_for_n4] > 0:
        return best_fit_for_n4
    else:
        return ""


def assign_n1_n2_and_n3(original_question, prioritized_numbers, num_selected_for_n4):
    copy_prioritized = prioritized_numbers.copy()
    copy_prioritized.remove(num_selected_for_n4)
    if len(copy_prioritized) < 3:
        return "", "", ""

    ordered_numbers = []
    original_split = original_question.replace('. ', ' ').replace('?', '').split()
    for i in range(len(original_split)):
        if original_split[i] == "2" and original_split[i - 2] == "sum":
            continue
        if original_split[i] in copy_prioritized:
            ordered_numbers.append(original_split[i])
    return ordered_numbers[0], ordered_numbers[2], ordered_numbers[1]


def read_type1_questions():
    return read_all_questions_from_file("../organized_questions/type_1.txt", Type1Question,
                                        first_symbol_to_look_for="*")


if __name__ == "__main__":
    all_type1_questions = read_type1_questions()
    acc_value = test_all_same_type_questions(all_type1_questions, "1")
    print("\n", "~" * 100, "\n====> Accuracy Value for Type 1 Questions =", acc_value * 100, "%")
