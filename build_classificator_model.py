#import datetime
import warnings
#import pandas as pd
from disk import disk_access
from gensim import corpora, similarities, models
from database3 import Database
from models import Models
from datetime import datetime


warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
warnings.filterwarnings(action='ignore', category=FutureWarning, module='gensim')


class build_model():

  def __init__(self):
    self.dictionary = object 
    self.corpus = object
    self.model_TFIDF = object
    self.corpus_TFIDF = object
    self.index_TFIDF = object
    self.model_LSI = object
    self.corpus_LSI = object
    self.index_LSI = object  

  def build_all_models(self, parameter_value_list):
    self.dictionary = self.build_dict(parameter_value_list)
    self.corpus = self.build_corpus(parameter_value_list, self.dictionary)

    self.model_TFIDF = models.TfidfModel(self.corpus) #corpus_TFIDF?
    self.corpus_TFIDF = self.model_TFIDF[self.corpus]
    self.index_TFIDF = similarities.MatrixSimilarity(self.model_TFIDF[self.corpus]) #corpus_TFIDF?

    self.model_LSI = models.LsiModel(self.corpus_TFIDF, id2word=self.dictionary)
    self.corpus_LSI = self.model_LSI[self.corpus_TFIDF] #aplica o modelo para transformar o Corpus para LSI
    self.index_LSI = similarities.MatrixSimilarity(self.model_LSI[self.corpus_TFIDF])


  def save_pickle(self, object, modelname):
    self.write_to_disk(object, modelname, ".pkl")
    #write to database
    disk = disk_access()
    #class_model = Models()
    class_db = Database()
    model = Models(name = modelname, pathLocation = disk.get_model_absolute_path(modelname) , userName = "Marcelo", date = datetime.utcnow())
    class_db.saveData(model)

  
  def save_all(self, modelname):
    self.write_to_disk(self.dictionary, modelname, ".dict")
    
    self.write_to_disk(self.model_TFIDF, modelname, ".tfidf")
    self.write_to_disk(self.index_TFIDF, modelname, "_tfidf.index")

    self.write_to_disk(self.model_LSI, modelname, ".lsi")
    self.write_to_disk(self.index_LSI, modelname, "_lsi.index")

    #write to database
    disk = disk_access()
    #class_model = Models()
    class_db = Database()
    model = Models(name = modelname, pathLocation = disk.get_model_absolute_path(modelname) , userName = "Marcelo", date = datetime.utcnow())
    class_db.saveData(model)
    
  
  
  def build_dict(self, parameter_value_list):
    dictionary = corpora.Dictionary(parameter_value_list)
    return dictionary

  def build_corpus(self, parameter_value_list, dictionary):
    corpus = [dictionary.doc2bow(text) for text in parameter_value_list]
    return corpus
  
  def write_to_disk(self, object, modelname, type):
    filename = modelname + type
    disk = disk_access()
    if ".pkl" in type:
      disk.write_pickle(object, filename)
    else:
      disk.write_model(object, filename)
      
  def load(self, modelname):
    filename = modelname + ".pkl"
    disk = disk_access()       
    return disk.load_pickle(filename)
    