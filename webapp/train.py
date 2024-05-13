import random
import json
import pickle
import numpy as np
import tensorflow as tf
import nltk



from nltk.stem import WordNetLemmatizer

nltk.download('punkt')

"""
The 'punkt' tokenizer is used for tokenizing text into individual words or sentences.
"""
nltk.download('wordnet')
""" 
The 'wordnet' corpus is a lexical database that provides synonyms, antonyms, and other word relationships.
"""


lemmatizer = WordNetLemmatizer()

# Load intents from a JSON file

intents = json.loads(open('webapp/intents2.json').read())



words = []  # List to store individual words
classes = []  # List to store classes (intent tags)
documents = []  # List to store word patterns with their corresponding intent tags
ignoreLetters = ['?', '!', '.', ',']  # List of characters to ignore

# Extract words, classes, and word patterns from intents
for intent in intents['intents']:
    for pattern in intent['patterns']:

        wordList = nltk.word_tokenize(pattern)  # Tokenize the pattern into words

        words.extend(wordList)  # Add words to the words list

        documents.append((wordList, intent['tag']))  # Add word pattern and intent tag to documents list
        
        if intent['tag'] not in classes:
            classes.append(intent['tag'])  # Add unique intent tags to classes list



# Lemmatize words (reduce them to their base form) and remove ignored characters
words = [lemmatizer.lemmatize(word) for word in words if word not in ignoreLetters]

# Sort and remove duplicates from words and classes lists
words = sorted(set(words))



classes = sorted(set(classes))


# Save words and classes lists using pickle
pickle.dump(words, open('words.pkl', 'wb'))
pickle.dump(classes, open('classes.pkl', 'wb'))

"""
This line saves the words variable to a file named 'words.pkl'. 
The pickle.dump() function serializes the object (words in this case) and writes it to the file. 
The 'wb' argument specifies that the file should be opened in binary mode for writing.
"""

training = []  # List to store training data
outputEmpty = [0] * len(classes)  # List representing empty output with 0s

# Create training data by converting word patterns to bag of words format and generating output rows
#  preparing the data for training a model.

for document in documents:
    bag = []
    wordPatterns = document[0]
    
    wordPatterns = [lemmatizer.lemmatize(word.lower()) for word in wordPatterns]

    for word in words:
        bag.append(1) if word in wordPatterns else bag.append(0)

    outputRow = list(outputEmpty)
    
    outputRow[classes.index(document[1])] = 1
    
    training.append(bag + outputRow)



# Shuffle the training data randomly
random.shuffle(training)
"""
By shuffling the training data, you are changing the order of the elements randomly.
This can be useful to ensure that the data is not biased by any specific order during training.
Shuffling the data helps to introduce randomness and prevent the model from learning any patterns that may exist due to the order of the data.
"""

# Convert training data to a numpy array
training = np.array(training)

trainX = training[:, :len(words)] # Input features (bag of words)


trainY = training[:, len(words):]


model = tf.keras.Sequential()

# Add layers to the model
model.add(tf.keras.layers.Dense(128, input_shape=(len(trainX[0]),), activation='relu'))  # Input layer
"""
This line adds the input layer to the model. The Dense layer represents a fully connected layer, 
where each neuron is connected to every neuron in the previous layer. The 128 parameter specifies the number of neurons in this layer.
The input_shape parameter defines the shape of the input data, which in this case is (len(trainX[0]),). 
The activation='relu' parameter specifies the activation function to be used, which is the Rectified Linear Unit (ReLU) in this case.
"""
model.add(tf.keras.layers.Dropout(0.5))  # Dropout layer for regularization
"""
This line adds a dropout layer to the model.
Dropout is a regularization technique that randomly sets a fraction of input units to 0 during training, 
which helps prevent overfitting.
The 0.5 parameter specifies the dropout rate, which is the fraction of input units to drop.
"""
model.add(tf.keras.layers.Dense(64, activation='relu'))  # Hidden layer
"""
This line adds a hidden layer to the model. It is similar to the input layer, but with 64 neurons instead of 128.
"""
model.add(tf.keras.layers.Dropout(0.5))  # Dropout layer for regularization
"""
This line adds another dropout layer for regularization, similar to the previous one.
"""
model.add(tf.keras.layers.Dense(len(trainY[0]), activation='softmax'))  # Output layer


"""
This line adds the output layer to the model. The number of neurons in this layer is determined by the number of classes in your target variable,
which is len(trainY[0]) in this case. The activation='softmax' parameter specifies the activation function to be used, which is the softmax function.
Softmax is commonly used for multi-class classification problems as it produces a probability distribution over the classes.
"""



parameters = model.trainable_variables  # Get the trainable variables (parameters) of the model

sgd = tf.keras.optimizers.SGD(learning_rate=0.01, momentum=0.9, nesterov=True)

"""
This line creates an instance of the Stochastic Gradient Descent (SGD) optimizer.
The SGD optimizer is a popular optimization algorithm used in neural networks.
The learning_rate parameter determines the step size at each iteration of the optimization process. 
The momentum parameter controls the amount of momentum to apply during optimization,
which helps the optimizer to converge faster.
The nesterov parameter specifies whether to use Nesterov momentum, which is an improvement over standard momentum.
"""
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

"""
This line compiles the model. The loss parameter specifies the loss function to be used during training. 
In this case, 'categorical_crossentropy' is used, which is commonly used for multi-class classification problems.
The optimizer parameter specifies the optimizer to be used for training, which is the sgd optimizer that we created earlier.
The metrics parameter specifies the evaluation metric(s) to be used during training and testing.
In this case, we are using 'accuracy' as the metric to monitor the performance of the model.
"""

# Train the model using the training data
hist = model.fit(np.array(trainX), np.array(trainY), epochs=200, batch_size=5, verbose=1)

"""

epochs=200: This parameter specifies the number of times the entire training dataset will be passed through the model during training. 
In this case, the model will be trained for 200 epochs.

batch_size=5: This parameter determines the number of samples that will be propagated through the model at once. 
The training dataset will be divided into batches, 
and each batch will be used to update the model's weights. A smaller batch size can help with memory constraints and can also lead to faster convergence,
but it may introduce more noise in the training process.

verbose=1: This parameter controls the verbosity of the training process. Setting it to 1 will display progress bars during training, 
while setting it to 0 will suppress the output
The model.fit function will train the model by iteratively updating the model's weights based on the provided input and target data. 
It uses the specified optimizer, loss function, and evaluation metric to guide the training process.
After training is complete, the fit function will return a History object, which contains information about the training process,
such as the loss and accuracy values at each epoch.
If you have any further questions or need more clarification, feel free to ask!
"""



# Save the trained model
model.save('chatbot_model.h5', hist)

print('Done')
