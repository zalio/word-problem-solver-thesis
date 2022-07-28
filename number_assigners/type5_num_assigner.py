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
        answer = solve([self.n1 + self.n2 * x - self.n3], x)
        return answer

    def __str__(self):
        return "n1 = " + str(self.n1) + " ; n2 = " + str(self.n2) + " ; n3 = " + str(self.n3)


class Type5Question:
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
        eliminate_very_long_questions(self.generated_questions, 40)

        all_discovered_numbers, all_related_number_strings = discover_all_numbers(self.original_question)

        prioritized_numbers, backup_numbers = prioritize_discovered_numbers(all_discovered_numbers,
                                                                            all_related_number_strings)

        if len(prioritized_numbers) < 3:
            return None

        predicted_n2 = find_n2_by_number_related_words(prioritized_numbers, self.original_question)

        eliminate_generated_q_or_a_with_three_numbers(prioritized_numbers, self.generated_questions)
        predicted_n3 = find_n3_by_scoring_repeated_numbers(prioritized_numbers, self.generated_questions, predicted_n2)

        for i in range(len(prioritized_numbers)):
            if prioritized_numbers[i] in numbers_written_with_letters_dict:
                prioritized_numbers[i] = str(numbers_written_with_letters_dict[prioritized_numbers[i]])
        if predicted_n2 in numbers_written_with_letters_dict:
            predicted_n2 = str(numbers_written_with_letters_dict[predicted_n2])
        if predicted_n3 in numbers_written_with_letters_dict:
            predicted_n3 = str(numbers_written_with_letters_dict[predicted_n3])

        predicted_n1 = ""
        if predicted_n2 != "" and predicted_n3 != "":
            copy_prioritized = prioritized_numbers.copy()
            copy_prioritized.remove(predicted_n2)
            copy_prioritized.remove(predicted_n3)
            predicted_n1 = copy_prioritized[0]
        elif predicted_n3 != "":
            copy_prioritized = prioritized_numbers.copy()
            copy_prioritized.remove(predicted_n3)
            if float(copy_prioritized[0]) > float(copy_prioritized[1]):
                predicted_n1 = copy_prioritized[0]
                predicted_n2 = copy_prioritized[1]
            else:
                predicted_n1 = copy_prioritized[1]
                predicted_n2 = copy_prioritized[0]

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

            if "%" in self.original_question or "cents" in self.original_question:
                self.predicted_equation.n2 *= 0.01
            return self.predicted_equation


def prioritize_discovered_numbers(all_discovered_numbers, all_related_number_strings):
    prioritized_numbers = []
    backup_numbers = []
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

    while len(prioritized_numbers) < 3 and len(backup_numbers) > 0:
        prioritized_numbers.append(backup_numbers[0])
        backup_numbers.pop(0)
    return prioritized_numbers, backup_numbers


def find_n2_by_number_related_words(prioritized_numbers, original_question):
    original_split = original_question.replace('. ', ' ').replace('?', '').replace(',', '').split()
    for i in range(len(original_split)):
        if (original_split[i] == "%" or original_split[i] == "cents") and original_split[i - 1] in prioritized_numbers:
            return original_split[i - 1]
        elif original_split[i] == "twice":
            return "2"
    return ""


def eliminate_generated_q_or_a_with_three_numbers(prioritized_numbers, generated_questions):
    for i in generated_questions:
        generated_split = i.generated.replace('. ', ' ').replace('?', '').replace(',', '').split()
        prioritized_found_count = 0
        for j in generated_split:
            if j in prioritized_numbers:
                prioritized_found_count += 1
        if prioritized_found_count > 2:
            i.ignore_generated_q = True

        answer_split = i.answer.replace('.', '').replace('?', '').replace("  ", ".").replace(' , ', '').split()
        prioritized_found_count = 0
        for j in answer_split:
            if j in prioritized_numbers:
                prioritized_found_count += 1
        if prioritized_found_count > 2:
            i.ignore_answer = True


def find_n3_by_scoring_repeated_numbers(prioritized_numbers, generated_questions, potential_n2_value):
    prioritized_num_scores = {}
    for i in prioritized_numbers:
        prioritized_num_scores[i] = 0

    for i in generated_questions:
        if not i.ignore_generated_q:
            generated_split = i.generated.replace('. ', ' ').replace('?', '').replace(',', '').split()
            prioritized_found_count = 0
            temp_prioritized_numbers = []
            for j in generated_split:
                if j in prioritized_numbers:
                    prioritized_found_count += 1
                    temp_prioritized_numbers.append(j)
            if prioritized_found_count == 2:
                prioritized_num_scores[temp_prioritized_numbers[0]] += 0.5
                prioritized_num_scores[temp_prioritized_numbers[1]] += 0.5
            elif prioritized_found_count == 1 and len(generated_split) < 4:
                prioritized_num_scores[temp_prioritized_numbers[0]] += 2
            elif prioritized_found_count == 1:
                prioritized_num_scores[temp_prioritized_numbers[0]] += 1
        if not i.ignore_answer:
            answer_split = i.answer.replace('.', '').replace('?', '').replace("  ", ".").replace(' , ', '').split()
            prioritized_found_count = 0
            temp_prioritized_numbers = []
            for j in answer_split:
                if j in prioritized_numbers:
                    prioritized_found_count += 1
                    temp_prioritized_numbers.append(j)
            if prioritized_found_count == 2:
                prioritized_num_scores[temp_prioritized_numbers[0]] += 0.5
                prioritized_num_scores[temp_prioritized_numbers[1]] += 0.5
            elif prioritized_found_count == 1 and len(answer_split) < 4:
                prioritized_num_scores[temp_prioritized_numbers[0]] += 2
            elif prioritized_found_count == 1:
                prioritized_num_scores[temp_prioritized_numbers[0]] += 1

    max_score = 0
    key_with_max_score = ""
    for k, v in prioritized_num_scores.items():
        if k == potential_n2_value:
            continue
        elif v > max_score:
            max_score = v
            key_with_max_score = k
        elif v > 0 and v == max_score:
            try:
                float_k = float(k)
            except ValueError:
                float_k = float(numbers_written_with_letters_dict[k])
            try:
                float_key_with_max_score = float(key_with_max_score)
            except ValueError:
                float_key_with_max_score = float(numbers_written_with_letters_dict[key_with_max_score])
            if float_k > float_key_with_max_score:
                max_score = v
                key_with_max_score = k
    return key_with_max_score


def fix_solution_numbers_order(solution_line, _):
    num_from_equations = re.findall(r'\d*\.?\d+', solution_line)
    for i in solution_line:
        if i == "+":
            return num_from_equations[0] + "---" + num_from_equations[1] + "---" + num_from_equations[2]
        elif i == "*":
            return num_from_equations[1] + "---" + num_from_equations[0] + "---" + num_from_equations[2]
        elif i == "-":
            return num_from_equations[2] + "---" + num_from_equations[1] + "---" + num_from_equations[0]
    return solution_line


def read_type5_questions():
    return read_all_questions_from_file("type_5.txt", Type5Question,
                                        fix_solution_function=fix_solution_numbers_order)


if __name__ == "__main__":
    all_type5_questions = read_type5_questions()
    acc_value = test_all_same_type_questions(all_type5_questions, "5")
    print("\n", "~" * 100, "\n====> Accuracy Value for Type 5 Questions =", acc_value * 100, "%")
