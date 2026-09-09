import request from './request'
import type { RegisterReq, LoginReq, LoginResp } from '@/types/api'
import type { UserInfo } from '@/types/models'

export const register = (data: RegisterReq) =>
  request.post<unknown, UserInfo>('/api/auth/register', data)

export const login = (data: LoginReq) =>
  request.post<unknown, LoginResp>('/api/auth/login', data)

export const getMe = () => request.get<unknown, UserInfo>('/api/auth/me')
