import { ApiProjectDiscussionRepository } from '~/repositories/projectDiscussion/apiProjectDiscussionRepository'

export class ProjectDiscussionApplicationService {
  private readonly repository: ApiProjectDiscussionRepository

  constructor(repository?: ApiProjectDiscussionRepository) {
    this.repository = repository || new ApiProjectDiscussionRepository()
  }

  async list(projectId: string | number, versionId?: string | number) {
    return await this.repository.list(projectId, versionId)
  }

  async create(projectId: string | number, message: string) {
    return await this.repository.create(projectId, message)
  }
} 