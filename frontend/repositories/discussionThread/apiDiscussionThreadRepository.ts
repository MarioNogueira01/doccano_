import ApiService from '@/services/api.service'

export class ApiDiscussionThreadRepository {
  async list(projectId: string | number, versionId?: string | number) {
    const url = `/projects/${projectId}/discussion-threads`
    const response = await ApiService.get(url, {
      params: versionId ? { version_id: versionId } : undefined,
    })
    return response.data
  }

  async create(projectId: string | number, title: string) {
    const url = `/projects/${projectId}/discussion-threads`
    const response = await ApiService.post(url, { title })
    return response.data
  }
} 