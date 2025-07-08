import { ApiDiscussionThreadRepository } from '~/repositories/discussionThread/apiDiscussionThreadRepository'

export class DiscussionThreadApplicationService {
  private readonly repository: ApiDiscussionThreadRepository

  constructor(repository?: ApiDiscussionThreadRepository) {
    this.repository = repository || new ApiDiscussionThreadRepository()
  }

  async list(projectId: string | number, versionId?: string | number) {
    return await this.repository.list(projectId, versionId)
  }

  async create(projectId: string | number, title: string) {
    return await this.repository.create(projectId, title)
  }
} 