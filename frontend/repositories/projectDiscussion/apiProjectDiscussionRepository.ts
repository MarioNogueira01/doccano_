import ApiService from '@/services/api.service'

export class ApiProjectDiscussionRepository {
  async list(projectId: string | number, versionId?: string | number) {
    const url = `/projects/${projectId}/chat`
    const response = await ApiService.get(url, {
      params: versionId ? { version_id: versionId } : undefined,
    })
    return response.data
  }

  async create(projectId: string | number, message: string) {
    const url = `/projects/${projectId}/chat`
    const response = await ApiService.post(url, { message })
    return response.data
  }
} 