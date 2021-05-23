from number_assigners.type0_num_assigner import read_type0_questions
from number_assigners.type1_num_assigner import read_type1_questions
from number_assigners.type2_num_assigner import read_type2_questions
from number_assigners.type3_num_assigner import read_type3_questions
from number_assigners.type4_num_assigner import read_type4_questions
from number_assigners.type5_num_assigner import read_type5_questions
from number_assigners.type6_num_assigner import read_type6_questions
from number_assigners.type7_num_assigner import read_type7_questions
from number_assigners.type8_num_assigner import read_type8_questions
from number_assigners.type9_num_assigner import read_type9_questions
from number_assigners.type10_num_assigner import read_type10_questions
from number_assigners.type11_num_assigner import read_type11_questions
from number_assigners.type12_num_assigner import read_type12_questions
from number_assigners.type13_num_assigner import read_type13_questions
from number_assigners.type14_num_assigner import read_type14_questions
from number_assigners.type15_num_assigner import read_type15_questions
from number_assigners.type16_num_assigner import read_type16_questions
from number_assigners.type17_num_assigner import read_type17_questions
from number_assigners.type18_num_assigner import read_type18_questions
from number_assigners.type19_num_assigner import read_type19_questions
from number_assigners.type20_num_assigner import read_type20_questions
from number_assigners.type21_num_assigner import read_type21_questions
from sympy import *


def calculate_detailed_accuracy(predicted_answers, actual_answers):
    correct_predictions_count = 0
    incorrect_predictions_count = 0
    unsolvable_predictions_count = 0
    for i in range(len(predicted_answers)):
        solved_flag = False
        if predicted_answers[i] is None:
            unsolvable_predictions_count += 1
            continue
        if predicted_answers[i] == actual_answers[i]:
            correct_predictions_count += 1
            solved_flag = True
        elif len(actual_answers[i]) == 2 and predicted_answers[i] is not None and actual_answers[i] is not None:
            x = Symbol("x")
            y = Symbol("y")
            if predicted_answers[i][x] == actual_answers[i][y] and predicted_answers[i][y] == actual_answers[i][x]:
                correct_predictions_count += 1
                solved_flag = True

        if not solved_flag:
            incorrect_predictions_count += 1
    return (correct_predictions_count / len(predicted_answers), correct_predictions_count, incorrect_predictions_count,
            unsolvable_predictions_count)


def test_same_type_questions(same_type_questions, type_no, detailed_output=False):
    predicted_answers = []
    actual_answers = []
    index = 0
    for q in same_type_questions:
        if detailed_output:
            print("\n********** Results of Question", index, "from Type", type_no, "Questions **********\n")
        predicted_eq = q.predict_equation_from_generated_q()
        if predicted_eq is None:
            if detailed_output:
                print("Question", index, "has been failed to be solved.\n")
            predicted_answers.append(None)
        else:
            pred_answer = predicted_eq.solve_equation()
            if detailed_output:
                print("Predicted number slot values: ", predicted_eq)
                print("Predicted answer --> ", pred_answer, "\n")
            predicted_answers.append(pred_answer)
        actual_eq = q.solution_equation
        actual_answer = actual_eq.solve_equation()
        if detailed_output:
            print("Actual number slot values: ", actual_eq)
            print("Actual answer --> ", actual_answer)
        actual_answers.append(actual_answer)
        index += 1

    if detailed_output:
        print("\n" + "-" * 80, "\n----- The total number of type", type_no, "questions:", str(len(actual_answers)),
              "-----\n")
    accuracy_value, correct_predictions_count, incorrect_predictions_count, unsolvable_predictions_count = \
        calculate_detailed_accuracy(predicted_answers, actual_answers)
    return accuracy_value, correct_predictions_count, incorrect_predictions_count, unsolvable_predictions_count


def test_all_questions():
    all_questions = {0: read_type0_questions(), 1: read_type1_questions(), 2: read_type2_questions(),
                     3: read_type3_questions(), 4: read_type4_questions(), 5: read_type5_questions(),
                     6: read_type6_questions(), 7: read_type7_questions(), 8: read_type8_questions(),
                     9: read_type9_questions(), 10: read_type10_questions(), 11: read_type11_questions(),
                     12: read_type12_questions(), 13: read_type13_questions(), 14: read_type14_questions(),
                     15: read_type15_questions(), 16: read_type16_questions(), 17: read_type17_questions(),
                     18: read_type18_questions(), 19: read_type19_questions(), 20: read_type20_questions(),
                     21: read_type21_questions()}

    total_correct_predictions_count, total_incorrect_predictions_count, total_unsolvable_predictions_count = 0, 0, 0
    for k, v in all_questions.items():
        accuracy_value, correct_predictions_count, incorrect_predictions_count, unsolvable_predictions_count = \
            test_same_type_questions(v, str(k), detailed_output=False)
        print("----->Accuracy for the type", str(k), "questions =", str(accuracy_value * 100), "%\n\n" + "~" * 120,
              "\n")
        total_correct_predictions_count += correct_predictions_count
        total_incorrect_predictions_count += incorrect_predictions_count
        total_unsolvable_predictions_count += unsolvable_predictions_count

    print("*" * 120, "\n" + "*" * 120, "\n")
    print("The total number of all questions: 514\n")
    print("The total number of correct predictions out of all questions:", str(total_correct_predictions_count), "\n")
    print("The total number of incorrect predictions out of all questions:", str(total_incorrect_predictions_count),
          "\n")
    print("The total number of unsolvable questions out of all questions:", str(total_unsolvable_predictions_count),
          "\n")
    print("=====> Final accuracy of all 514 questions =", str((total_correct_predictions_count / 514) * 100), "%\n")


if __name__ == "__main__":
    test_all_questions()
