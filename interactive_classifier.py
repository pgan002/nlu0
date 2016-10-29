# Interactive classifier of utterances. Examples are defined in the files in
# directory DATA_DIR. Each data file represents a separate class and each line
# is an example user utterance.


import os

from sklearn.pipeline import make_pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import cross_val_score


DATA_DIR = 'data/raw'
CV_FOLDS = 5  # Number of cross-validation folds for evaluating a classifier


def _read_data_file(file_name):
  file_path = os.path.join(DATA_DIR, file_name)
  with open(file_path) as f:
    return f.readlines()


class InteractiveClassifier(object):
  """
  This implementation assumes that the raw text data and vectorized data fit
  together into memory.
   """
  def __init__(self, classifier_class):
    self.lines = None
    self.labels = None
    self.data = None
    self.classifier_class = classifier_class
    self.vectorizer = None
    self.classifier = None
    self.accuracies = None
  
  def read_data(self):
    """
    Read text lines from raw data files in the data directory.
    Return a list of lines in all files and a list of corresponding class labels.
    """
    file_names = os.listdir(DATA_DIR)
    self.lines = []
    self.labels = []
    for cls, file_name in enumerate(file_names):
      print cls, file_name
      lines = _read_data_file(file_name)
      self.lines += lines
      self.labels += [cls] * len(lines)
 
    assert len(self.lines) == len(self.labels)
    print len(self.lines), 'examples'
    return self.lines, self.labels

  def train_and_evaluate(self):
    """
    Evaluate this classifier using cross validation and return a classifier
    trained on all the available data.
    """
    self.vectorizer = CountVectorizer()
    self.classifier = self.classifier_class()
    pipeline = make_pipeline(self.vectorizer, self.classifier)

    # Evaluate
    self.accuracies = cross_val_score(
      pipeline,
      self.lines,
      self.labels,
      cv=CV_FOLDS
    )
    print('Accuracy on {}-fold cross-validation: mean={:0.3f}, STD={:0.3f}'.format(
      CV_FOLDS,
      self.accuracies.mean(),
      self.accuracies.std()
    ))

    # Train the final classifier
    self.data = self.vectorizer.fit_transform(self.lines)
    self.classifier.fit(self.data, self.labels)

  def classify_interactive(self):
    """Keep prompting for an utterance and classify it"""
    while True:
      try:
        line = raw_input('User utterance: ')
        query = self.vectorizer.transform([line])
        print(self.classifier.predict(query))
      except KeyboardInterrupt:
        break


def run():
  classifier = InteractiveClassifier(MultinomialNB)
  classifier.read_data()
  classifier.train_and_evaluate()
  classifier.classify_interactive()


if __name__ == '__main__':
  run()