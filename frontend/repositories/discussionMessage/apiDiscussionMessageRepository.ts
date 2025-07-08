import ApiService from '@/services/api.service'

export class ApiDiscussionMessageRepository {
  async list(projectId: string | number, threadId: string | number) {
    const url = `/projects/${projectId}/discussion-threads/${threadId}/messages`
    const response = await ApiService.get(url)
    return response.data
  }

  async create(projectId: string | number, threadId: string | number, message: string) {
    const url = `/projects/${projectId}/discussion-threads/${threadId}/messages`
    const response = await ApiService.post(url, { message })
    return response.data
  }
} 