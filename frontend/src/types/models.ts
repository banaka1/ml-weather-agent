// 用户/会话/消息实体类型

export interface UserInfo {
  user_id: number
  username: string
}

export interface SessionItem {
  id: string
  title: string
  updated_at: string
}

export interface MessageItem {
  role: 'human' | 'ai' | 'tool' | 'system'
  content: string
  ts: string
}

export interface ToolCallInfo {
  name: string
  args: Record<string, unknown>
  result: string
  ms: number
}
