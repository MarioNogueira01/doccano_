import { ApiDiscrepancieRepository } from '@/repositories/discrepancies/apiDiscrepancieRepository'

export class DiscrepacieApplicationService {
    constructor(private readonly repository: ApiDiscrepancieRepository) {}

    async listDiscrepancie(projectId: string | number) {
        return await this.repository.list(projectId)
      }

    async postDiscrepancies(projectId: string | number, data: any) {
        return await this.repository.postDiscrepancies(projectId, data)
    }

    async getDiscrepanciesDB(projectId: string | number) {
        return await this.repository.listDB(projectId)
        
    }
}