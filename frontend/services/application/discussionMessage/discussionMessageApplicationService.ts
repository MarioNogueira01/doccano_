import { ApiDiscussionMessageRepository } from '~/repositories/discussionMessage/apiDiscussionMessageRepository'

export class DiscussionMessageApplicationService {
  private readonly repository: ApiDiscussionMessageRepository

  constructor(repository?: ApiDiscussionMessageRepository) {
    this.repository = repository || new ApiDiscussionMessageRepository()
  }

  async list(projectId: string | number, threadId: string | number) {
    return await this.repository.list(projectId, threadId)
  }

  async create(projectId: string | number, threadId: string | number, message: string) {
    return await this.repository.create(projectId, threadId, message)
  }
} 