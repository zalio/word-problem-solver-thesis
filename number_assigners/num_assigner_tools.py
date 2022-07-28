from sympy import *
import re


numbers_written_with_letters_dict = {"double": 2, "twice": 2, "thrice": 3, "triple": 3, "one": 1, "two": 2, "three": 3,
                                     "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "Double": 2,
                                     "Twice": 2, "Thrice": 3, "Triple": 3, "One": 1, "Two": 2, "Three": 3, "Four": 4,
                                     "Five": 5, "Six": 6, "Seven": 7, "Eight": 8, "Nine": 9, "half": 0.5, "Half": 0.5,
                                     "nickels": 0.05, "dimes": 0.1, "Nickels": 0.05, "Dimes": 0.1,
                                     "thousand": 1000, "Thousand": 1000}


class GeneratedQuestion:
    def __init__(self, generated, answer):
        self.generated = generated
        self.answer = answer
        self.ignore_generated_q = False
        self.ignore_answer = False


def eliminate_questions_without_any_numbers(generated_questions):
    for i in generated_questions:
        numbers_in_generated = re.findall(r'\d*\.?\d+', i.generated)
        numbers_in_answer = re.findall(r'\d*\.?\d+', i.answer)
        if len(numbers_in_generated) == 0:
            number_exists_flag = False
            generated_split = i.generated.replace('. ', ' ').replace('?', '').replace(',', '').split()
            for j in generated_split:
                if j in numbers_written_with_letters_dict:
                    number_exists_flag = True
            if not number_exists_flag:
                i.ignore_generated_q = True

        if len(numbers_in_answer) == 0:
            number_exists_flag = False
            answer_split = i.answer.replace('.', '').replace('?', '').replace("  ", ".").replace(' , ', '').split()
            for j in answer_split:
                if j in numbers_written_with_letters_dict:
                    number_exists_flag = True
            if not number_exists_flag:
                i.ignore_answer = True


def discover_all_numbers(original_question):
    all_discovered_numbers = []
    all_related_number_strings = []
    modified_original_q = original_question.replace('. ', ' ').replace('?', '').replace(',', '').replace('-', ' ')
    original_q_split = modified_original_q.split()
    for i in original_q_split:
        if i in numbers_written_with_letters_dict:
            if i not in all_related_number_strings:
                all_related_number_strings.append(i)

    numbers_in_original = re.findall(r'\d*\.?\d+', modified_original_q)
    for i in numbers_in_original:
        if i not in all_discovered_numbers:
            all_discovered_numbers.append(i)
    return all_discovered_numbers, all_related_number_strings


def eliminate_useless_questions(generated_questions):
    for i in generated_questions:
        generated_split = i.generated.replace('. ', ' ').replace('?', '').replace(',', '').split()
        if generated_split[0] == "Where" or generated_split[0] == "When":
            i.ignore_generated_q = True
            i.ignore_answer = True


def eliminate_very_long_questions(generated_questions, max_number_of_words_in_a_question):
    for i in generated_questions:
        generated_split = i.generated.replace('. ', ' ').replace('?', '').replace(',', '').split()
        if len(generated_split) > max_number_of_words_in_a_question:
            i.ignore_generated_q = True
            i.ignore_answer = True


def fix_solution_line_if_necessary(solution_line, first_symbol_to_look_for):
    split_solution_line = solution_line.split(" and ")
    all_possible_symbols = ["+", "-", "*", "/", "="]
    all_possible_symbols.remove(first_symbol_to_look_for)
    if len(split_solution_line) > 1:
        for i in split_solution_line[0]:
            if i == first_symbol_to_look_for:
                return solution_line
            elif i in all_possible_symbols:
                return split_solution_line[1] + " and " + split_solution_line[0]
    return solution_line


def calc_accuracy(predicted_answers, actual_answers):
    correct_predictions_count = 0
    for i in range(len(predicted_answers)):
        if predicted_answers[i] == actual_answers[i]:
            correct_predictions_count += 1
        elif len(actual_answers[i]) == 2 and predicted_answers[i] is not None and actual_answers[i] is not None:
            x = Symbol("x")
            y = Symbol("y")
            if predicted_answers[i][x] == actual_answers[i][y] and predicted_answers[i][y] == actual_answers[i][x]:
                correct_predictions_count += 1
    return correct_predictions_count / len(predicted_answers)


def test_all_same_type_questions(all_same_type_questions, type_no):
    predicted_answers = []
    actual_answers = []
    index = 0
    for q in all_same_type_questions:
        print("\n********** Results of Question", index, "from Type", type_no, "Questions **********\n")
        predicted_eq = q.predict_equation_from_generated_q()
        if predicted_eq is None:
            print("Question", index, "has been failed to be solved.\n")
            predicted_answers.append(None)
        else:
            pred_answer = predicted_eq.solve_equation()
            print("Predicted number slot values: ", predicted_eq)
            print("Predicted answer --> ", pred_answer, "\n")
            predicted_answers.append(pred_answer)
        actual_eq = q.solution_equation
        actual_answer = actual_eq.solve_equation()
        print("Actual number slot values: ", actual_eq)
        print("Actual answer --> ", actual_answer)
        actual_answers.append(actual_answer)
        index += 1

    accuracy_value = calc_accuracy(predicted_answers, actual_answers)
    return accuracy_value


def read_all_questions_from_file(path, question_type_class, first_symbol_to_look_for="*",
                                 fix_solution_function=fix_solution_line_if_necessary):
    path = "./svamp1000_organized_questions/" + path
    f = open(path, "r")
    all_lines = f.readlines()
    generated_q_lines = []
    original_q = ""
    num_from_equations = []
    all_questions = []
    for line in all_lines:
        if line[:4] == "*** ":
            original_q = line[4:-1]
        elif line[:4] == "==> ":
            fixed_solution_line = fix_solution_function(line[23:-1], first_symbol_to_look_for)
            num_from_equations = re.findall(r'\d*\.?\d+', fixed_solution_line)
        elif line != "\n" and line != "~~~\n":
            generated_q_lines.append(line[:-1])
        elif line == "~~~\n":
            temp_type1 = question_type_class(original_q, num_from_equations)
            temp_type1.organize_generated_q_and_a(generated_q_lines)
            generated_q_lines = []
            all_questions.append(temp_type1)
    return all_questions
