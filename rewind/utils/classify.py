"""Checking topicclassifier utility"""
from transformers import AutoTokenizer, AutoModelForSequenceClassification

def main():
    """main code"""
    tokenizer = AutoTokenizer.from_pretrained("models/TopicClassifier-NoURL")
    model = AutoModelForSequenceClassification.from_pretrained(
        "models/TopicClassifier-NoURL",
        trust_remote_code=True,
        use_memory_efficient_attention=False)

    tmp_web_page = """缚”,李贽自道“其心痴狂,其行率易”,袁宏道也自称“余生狂僻”"""

    inputs = tokenizer([tmp_web_page], return_tensors="pt")
    outputs = model(**inputs)

    print(outputs.logits)
    probs = outputs.logits.softmax(dim=-1)
    print(probs.argmax(dim=-1))
    # -> 5 ("Hardware" topic)

if __name__ == "__main__":
    main()
