import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { UserInfo } from '@/types/models'
import { login as apiLogin, register as apiRegister } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('token') || '')
  const user = ref<UserInfo | null>(
    (() => {
      const raw = localStorage.getItem('user')
      return raw ? (JSON.parse(raw) as UserInfo) : null
    })(),
  )

  const isLoggedIn = () => !!token.value

  async function login(username: string, password: string) {
    const resp = await apiLogin({ username, password })
    token.value = resp.token
    user.value = resp.user
    localStorage.setItem('token', resp.token)
    localStorage.setItem('user', JSON.stringify(resp.user))
  }

  async function register(username: string, password: string) {
    await apiRegister({ username, password })
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return { token, user, isLoggedIn, login, register, logout }
})
