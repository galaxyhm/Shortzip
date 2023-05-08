# 전체 모델 트레이닝 코드

import json
import nltk
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds
import torch
from datasets import Dataset
from transformers import BartForConditionalGeneration
from transformers import DataCollatorForSeq2Seq, Seq2SeqTrainingArguments, Seq2SeqTrainer
from transformers import PreTrainedTokenizerFast
import evaluate


tokenizer = PreTrainedTokenizerFast.from_pretrained('gogamza/kobart-base-v2')
model = BartForConditionalGeneration.from_pretrained('gogamza/kobart-base-v2')


def compute_metrics(eval_pred):
    '''
    모델 트레이닝 지표 함수
    rouge score 계산 함수
    '''

    metric = evaluate.load("rouge")

    predictions, labels = eval_pred
    decoded_preds = tokenizer.batch_decode(predictions, skip_special_tokens=True)
    # Replace -100 in the labels as we can't decode them.
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

    # Rouge expects a newline after each sentence
    decoded_preds = ["\n".join(nltk.sent_tokenize(pred.strip())) for pred in decoded_preds]
    decoded_labels = ["\n".join(nltk.sent_tokenize(label.strip())) for label in decoded_labels]

    result = metric.compute(predictions=decoded_preds, references=decoded_labels, use_stemmer=True)
    # Extract a few results
    result = {key: value.mid.fmeasure * 100 for key, value in result.items()}

    # Add mean generated length
    prediction_lens = [np.count_nonzero(pred != tokenizer.pad_token_id) for pred in predictions]
    result["gen_len"] = np.mean(prediction_lens)

    return {k: round(v, 4) for k, v in result.items()}


def preprocess_function(examples):
    prefix = ''
    max_input_length = 2000
    max_target_length = 750
    inputs = [prefix + doc for doc in examples["body"]]
    model_inputs = tokenizer(inputs, max_length=max_input_length, truncation=True)
    # 데이터가 손실될 경우에 앞의 단어가 아니라 뒤의 단어가 삭제되도록 하고싶다면 truncating이라는 인자를 사용합니다. truncating='post'를 사용할 경우 뒤의 단어가 삭제됩니다.
    # Setup the tokenizer for targets
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(examples["abstractive"], max_length=max_target_length, truncation=True)

    model_inputs["labels"] = labels["input_ids"]
    return model_inputs


def extract_body(article) -> str:
    art_sentence = []

    for contents in article:
        if len(contents) >= 2:
            for sub_con in contents:
                art_sentence.append(sub_con['sentence'])
                continue
        elif len(contents) == 0:
            pass
        else:
            art_sentence.append(contents[0]['sentence'])

    return art_sentence


def sentence_validation(art_sentence):
    del_sentence = []
    for sentence in art_sentence:
        if '@' in sentence or '/사진' in sentence:
            del_sentence.append(sentence)
        elif sentence[-1] != '.':
            del_sentence.append(sentence)
    for del_sen in del_sentence:
        art_sentence.remove(del_sen)
    return ' '.join(art_sentence)


def main():
    torch.cuda.is_available()
    with open('../data/train_original.json', encoding='utf-8') as train_f:
        train_data = json.loads(train_f.read())
        train_df = pd.DataFrame(train_data['documents'])

    with open('../data/valid_original.json', encoding='utf-8') as valid_f:
        valid_data = json.loads(valid_f.read())
        valid_df = pd.DataFrame(valid_data['documents'])

    train_df['body'] = train_df.text.apply(lambda x: sentence_validation(extract_body(x)))
    valid_df['body'] = valid_df.text.apply(lambda x: sentence_validation(extract_body(x)))

    train_df.abstractive = train_df.abstractive.apply(lambda x: x[0])
    valid_df.abstractive = valid_df.abstractive.apply(lambda x: x[0])

    train_df.drop(train_df.body.str.len().sort_values(ascending=False).head(1).index[0], inplace=True)

    df = train_df.copy()
    dataset = ds.dataset(pa.Table.from_pandas(df).to_batches())

    ### convert to Huggingface dataset
    hg_dataset = Dataset(pa.Table.from_pandas(df))
    hg_dataset_test = Dataset(pa.Table.from_pandas(valid_df[:1000]))

    del df

    tokenized_data = hg_dataset.map(preprocess_function, batched=True)
    tokenized_data_test = hg_dataset_test.map(preprocess_function, batched=True)
    metric = evaluate.load("rouge")

    batch_size = 2
    model_name = 'kobart_v2'
    args = Seq2SeqTrainingArguments(
        f"{model_name}-full-finetuned",
        evaluation_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        weight_decay=0.01,
        save_total_limit=3,
        num_train_epochs=5,
        predict_with_generate=True,
        fp16=True,  # CUDA 설정을 완료한 후 사용가능.
        push_to_hub=False,
    )

    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

    print('start training')
    trainer = Seq2SeqTrainer(
        model,
        args,
        train_dataset=tokenized_data,
        eval_dataset=tokenized_data_test,
        data_collator=data_collator,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics
    )

    trainer.train()

    trainer.save_model()


if __name__ == '__main__':
    main()
