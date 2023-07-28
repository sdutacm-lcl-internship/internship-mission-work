import json


class UserInfo:
  def __init__(self, handle, rating, rank, updated_at):
    self.__handle = handle
    self.__rating = rating
    self.__rank = rank
    self.__updated_at = updated_at

    # get methods
  def get_handle(self):
    return self.__handle

  def get_rating(self):
    return self.__rating

  def get_rank(self):
    return self.__rank

  def get_updated_at(self):
    return self.__updated_at

    # Setter methods

  def set_handle(self, handle):
    self.__handle = handle

  def set_rating(self, rating):
    self.__rating = rating

  def set_rank(self, rank):
    self.__rank = rank

  def set_updated_at(self, updated_at):
    self.__updated_at = updated_at


class UserRating:

  def __init__(self):
    pass

  # Getter methods
  def get_user_rating_id(self):
    return self.__user_rating_id

  def get_handle(self):
    return self.__handle

  def get_contest_id(self):
    return self.__contest_id

  def get_contest_name(self):
    return self.__contest_name

  def get_rank(self):
    return self.__rank

  def get_old_rating(self):
    return self.__old_rating

  def get_new_rating(self):
    return self.__new_rating

  def get_updated_at(self):
    return self.__updated_at

  # Setter methods
  def set_user_rating_id(self, user_rating_id):
    self.__user_rating_id = user_rating_id

  def set_handle(self, handle):
    self.__handle = handle

  def set_contest_id(self, contest_id):
    self.__contest_id = contest_id

  def set_contest_name(self, contest_name):
    self.__contest_name = contest_name

  def set_rank(self, rank):
    self.__rank = rank

  def set_old_rating(self, old_rating):
    self.__old_rating = old_rating

  def set_new_rating(self, new_rating):
    self.__new_rating = new_rating

  def set_updated_at(self, updated_at):
    self.__updated_at = updated_at

  def __repr__(self):
    return self.__str__()
