import request from '@/utils/request.js'

export const queryUser = (users) => {
  return request.post('user/batchGetUserInfo', users);
}

export const queryContests = (users) => {
  return request.post('user/getUserRatings', users);
}
