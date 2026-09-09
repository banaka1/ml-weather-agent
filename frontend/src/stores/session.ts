import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { SessionItem } from '@/types/models'
import {
  createSession,
  listSessions,
  renameSession,
  deleteSession,
} from '@/api/session'

export const useSessionStore = defineStore('session', () => {
  const sessions = ref<SessionItem[]>([])
  const currentId = ref<string>('')

  async function fetchSessions() {
    sessions.value = await listSessions()
  }

  async function newSession(): Promise<string> {
    const resp = await createSession()
    sessions.value.unshift({ id: resp.session_id, title: resp.title, updated_at: '' })
    currentId.value = resp.session_id
    return resp.session_id
  }

  function selectSession(id: string) {
    currentId.value = id
  }

  async function rename(id: string, title: string) {
    await renameSession(id, { title })
    const item = sessions.value.find((s) => s.id === id)
    if (item) item.title = title
  }

  async function remove(id: string) {
    await deleteSession(id)
    sessions.value = sessions.value.filter((s) => s.id !== id)
    if (currentId.value === id) currentId.value = ''
  }

  return { sessions, currentId, fetchSessions, newSession, selectSession, rename, remove }
})
