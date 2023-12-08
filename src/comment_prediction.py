from tensorflow import keras
import pickle

# Loading the vectorizer
def load_vectorizer(filename = 'models/text-vectorizer.pkl'):
    from_disk = pickle.load(open(filename, "rb"))
    new_vectorizer = keras.layers.TextVectorization(max_tokens=from_disk['config']['max_tokens'],
                                    output_mode=from_disk['config']['output_mode'],
                                    output_sequence_length=from_disk['config']['output_sequence_length'])
    new_vectorizer.set_weights(from_disk['weights'])
    return new_vectorizer


# Loading the model 
def get_model() -> keras.models.Sequential:

    model_path='models/toxic-comment-model.h5'
    model = keras.models.load_model(model_path)
    return model

# Defining the model to predict the toxicity of comment
def predict_toxicity(comment) -> dict:
    vectorizer = load_vectorizer()
    # converting the text into numpy array of length 1800
    input_comment = vectorizer([comment])
    # predicting the result
    model = get_model()
    result = model.predict(input_comment)
    return {
        "toxic": result[0][0],
        "severe_toxic": result[0][1],
        "obscene": result[0][2],
        "threat": result[0][3],
        "insult": result[0][4],
        "identity_hate": result[0][5]
    }

if __name__ == '__main__':
    # Make predictions with a sample text
    """
    The source of comment is from this
    https://web.stanford.edu/class/archive/cs/cs224n/cs224n.1194/posters/15722323.pdf
    I have nothing to do with this text
    """
    text = ". F* ck ing trollreasons\" \"if ytou think shes greek your a morooon"
    prediction = predict_toxicity(text)

    # Printing the prediction
    for key, value in prediction.items():
        if value >= 0.5:
            print(f'{key} : {value * 100 : 0.2f}%')