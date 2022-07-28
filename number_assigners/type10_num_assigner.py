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
        answer = solve([self.n1 * x - self.n2 * y, x + y - self.n3], x, y)
        return answer

    def __str__(self):
        return "n1 = " + str(self.n1) + " ; n2 = " + str(self.n2) + " ; n3 = " + str(self.n3)


class Type10Question:
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
        predicted_n3 = assign_n3(prioritized_numbers, self.generated_questions)
        predicted_n1, predicted_n2 = assign_n1_n2_pair(prioritized_numbers, self.generated_questions, predicted_n3)

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
        if (i == "1" or i == "2") and i not in backup_numbers:
            backup_numbers.append(i)
        elif i not in prioritized_numbers:
            prioritized_numbers.append(i)
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


def assign_n3(prioritized_numbers, generated_questions):
    n3 = ""
    end_loop_flag = False
    for i in generated_questions:
        if not i.ignore_answer:
            generated_split = i.generated.replace('. ', ' ').replace('?', '').replace(',', '').split()
            if generated_split[0] == "How" and generated_split[1] == "many":
                answer_split = i.answer.replace('.', '').replace('?', '').replace("  ", ".").replace(' , ', '').split()
                if len(answer_split) == 1 and answer_split[0] in prioritized_numbers:
                    n3 = answer_split[0]
                    end_loop_flag = True
        if end_loop_flag:
            break
    return n3


def assign_n1_n2_pair(prioritized_numbers, generated_questions, predicted_n3):
    for i in range(len(prioritized_numbers)):
        prioritized_numbers[i] = prioritized_numbers[i].lower()

    n1_n2_pair = []
    for i in generated_questions:
        if not i.ignore_answer:
            answer_split = i.answer.replace('.', '').replace('?', '').replace("  ", ".").replace(' , ', '').split()
            for j in answer_split:
                if j in prioritized_numbers and j != predicted_n3 and j not in n1_n2_pair:
                    n1_n2_pair.append(j)
        if len(n1_n2_pair) == 2:
            break

    if not n1_n2_pair:
        n1_n2_pair = ["", ""]
    return n1_n2_pair[1], n1_n2_pair[0]


def read_type10_questions():
    return read_all_questions_from_file("type_10.txt", Type10Question,
                                        first_symbol_to_look_for="*")


if __name__ == "__main__":
    all_type10_questions = read_type10_questions()
    acc_value = test_all_same_type_questions(all_type10_questions, "10")
    print("\n", "~" * 100, "\n====> Accuracy Value for Type 10 Questions =", acc_value * 100, "%")
