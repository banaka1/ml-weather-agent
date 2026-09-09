import request from './request'
import type { ChatReq, ChatResp } from '@/types/api'

export const sendChat = (data: ChatReq) =>
  request.post<unknown, ChatResp>('/api/chat', data)
