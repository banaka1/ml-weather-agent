import type { UserInfo, SessionItem, MessageItem, ToolCallInfo } from './models'

// 鉴权
export interface RegisterReq {
  username: string
  password: string
}
export interface LoginReq {
  username: string
  password: string
}
export interface LoginResp {
  token: string
  user: UserInfo
}

// 会话
export interface CreateSessionResp {
  session_id: string
  title: string
}
export interface RenameSessionReq {
  title: string
}
export interface OkResp {
  ok: boolean
}

// 聊天
export interface ChatReq {
  session_id: string
  message: string
}
export interface ChatResp {
  reply: string
  intent: string
  tools: ToolCallInfo[]
}

// 通用列表
export type SessionListResp = SessionItem[]
export type MessageListResp = MessageItem[]
