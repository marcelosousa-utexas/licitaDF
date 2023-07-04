import os
import json


class file_io():

  def __init__(self, file_full_path):
    self.file_full_path = file_full_path
    self.file_type = "plain_text"
    self.single_multiple_class = "single_classif"

    self.switch_file_type = {
      "plain_text": self.process_plain_text,
      "json": self.process_json_file,
      "pdf_OCR": self.process_searchable_pdf,
      "pdf": self.process_non_searchable_pdf
    }

    self.switch_single_multiple_class = {
      "single_classif": self.process_single_classif,
      "multiple_classif": self.process_multiple_classif
    }

  def set_file_type(self, file_type):
    self.file_type = file_type

  def get_file_type(self):
    return self.file_type

  def set_single_multiple_class(self, single_multiple_class):
    self.single_multiple_class = single_multiple_class

  def get_single_multiple_class(self):
    return self.single_multiple_class

  # def dispatch_filetype(self):
  #     """Dispatch method"""
  #     ext = os.path.splitext(self.file_full_path)[1][1:]
  #     method_name = 'read_' + ext
  #     # Get the method from 'self'. Default to a lambda.
  #     method = getattr(self, method_name, lambda: "Wrong document type")
  #     # Call the method as we return it
  #     return method()

  # def read_txt(self):
  #   with open(self.file_full_path, encoding="utf8") as txt_file:
  #     data = txt_file.read().lower()
  #   return data

  # def read_pdf(self):
  #     return None

  def process_plain_text(self):
    print("Processing plain text file...")
    with open(self.file_full_path, encoding="utf8") as txt_file:
      data = txt_file.read()
    return data

  def process_json_file(self):
    print("Processing json file...")
    with open(self.file_full_path, 'r', encoding='utf-8') as json_file:
      data = json.load(json_file)
    return data

  def process_searchable_pdf(self):
    print("Processing searchable PDF file...")

  def process_non_searchable_pdf(self):
    print("Processing non-searchable PDF file...")

  def process_unknown_file_type(self):
    print("Unknown file type")

  def process_single_classif(self):
    print("One classification per file")

  def process_multiple_classif(self):
    print("Multiple classifications per file")

  def process_unknown_classif(self):
    print("Unknown classification type")
