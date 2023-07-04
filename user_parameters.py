
class user():

  def __init__(self):
    self.new_model = True
    self.model_name = ""
    self.file_type = ""
    self.files = []
    self.type = ""

  def set_new_model(self, bool):
    self.new_model = bool

  def get_new_model(self):
    return self.new_model
  
  def add_file(self, fullpath):
    self.files.append(fullpath)

  def reset_files(self):
    self.files = [] 

  def get_files(self):
    return self.files

  def set_type(self, type):
    self.type = type

  def get_type(self):
    return self.type

  def set_model_name(self, model_name):
    self.model_name = model_name

  def get_model_name(self):
    return self.model_name

  def update_file_if_existis(self, fullpath):
    if fullpath in self.files:
      idx = self.files.index(fullpath)
      self.files[idx] = fullpath
      return True