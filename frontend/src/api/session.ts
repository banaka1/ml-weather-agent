import request from './request'
import type { CreateSessionResp, RenameSessionReq, OkResp } from '@/types/api'
import type { SessionItem, MessageItem } from '@/types/models'

export const createSession = () =>
  request.post<unknown, CreateSessionResp>('/api/sessions')

export const listSessions = () =>
  request.get<unknown, SessionItem[]>('/api/sessions')

export const getSessionMessages = (sessionId: string, page = 1, size = 100) =>
  request.get<unknown, MessageItem[]>(`/api/sessions/${sessionId}/messages`, {
    params: { page, size },
  })

export const renameSession = (sessionId: string, data: RenameSessionReq) =>
  request.patch<unknown, OkResp>(`/api/sessions/${sessionId}`, data)

export const deleteSession = (sessionId: string) =>
  request.delete<unknown, OkResp>(`/api/sessions/${sessionId}`)
