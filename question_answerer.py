from transformers import BertForQuestionAnswering
from transformers import BertTokenizer
import torch

model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')


def answer_a_question_about_a_question(question_highlighter, question_text_as_context):
    # ======== Tokenize ========
    # Apply the tokenizer to the input text, treating them as a text-pair.
    input_ids = tokenizer.encode(question_highlighter, question_text_as_context)

    # Report how long the input sequence is.
    # print('Query has {:,} tokens.\n'.format(len(input_ids)))

    # ======== Set Segment IDs ========
    # Search the input_ids for the first instance of the `[SEP]` token.
    sep_index = input_ids.index(tokenizer.sep_token_id)

    # The number of segment A tokens includes the [SEP] token itself.
    num_seg_a = sep_index + 1

    # The remainder are segment B.
    num_seg_b = len(input_ids) - num_seg_a

    # Construct the list of 0s and 1s.
    segment_ids = [0] * num_seg_a + [1] * num_seg_b

    # There should be a segment_id for every input token.
    assert len(segment_ids) == len(input_ids)

    # ======== Evaluate ========
    # Run our example question through the model.
    # start_scores, end_scores = model(torch.tensor([input_ids]), # The tokens representing our input text.
    # token_type_ids=torch.tensor([segment_ids])) # The segment IDs to differentiate question from answer_text

    outputs = model(torch.tensor([input_ids]),  # The tokens representing our input text.
                    token_type_ids=torch.tensor(
                        [segment_ids]))  # The segment IDs to differentiate question from answer_text

    # ======== Reconstruct Answer ========
    # Find the tokens with the highest `start` and `end` scores.
    start_scores = outputs.start_logits
    end_scores = outputs.end_logits

    answer_start = torch.argmax(start_scores)
    answer_end = torch.argmax(end_scores)
    # answer_start = torch.argmax(start_scores)
    # answer_end = torch.argmax(end_scores)

    # Get the string versions of the input tokens.
    tokens = tokenizer.convert_ids_to_tokens(input_ids)

    # Start with the first token.
    answer = tokens[answer_start]

    # Select the remaining answer tokens and join them with whitespace.
    for i in range(answer_start + 1, answer_end + 1):

        # If it's a subword token, then recombine it with the previous token.
        if tokens[i][0:2] == '##':
            answer += tokens[i][2:]

        # Otherwise, add a space then the token.
        else:
            answer += ' ' + tokens[i]

    print('Answer: "' + answer + '"')
    return answer


f = open("svamp1000_all_generated_questions.txt", "r")
f2 = open("svamp1000_Q_and_A.txt", "w")

context_question = ""
temp_answers = []
answers_to_generated_questions = []
while True:
    line = f.readline()
    if not line:
        break
    if line[0] == "*":
        context_question = line
        temp_answers = []

        f2.write(line)
        continue
    if line[0] == "~":
        answers_to_generated_questions.append(temp_answers)

        f2.write(line)
        continue
    temp_answer = answer_a_question_about_a_question(line[4:-1], context_question)
    temp_answers.append(temp_answer)

    f2.write(line[:-1] + " --> " + temp_answer + "\n")

f.close()
f2.close()
# print(answers_to_generated_questions)
