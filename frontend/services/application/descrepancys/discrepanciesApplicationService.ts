import { ApiDiscrepancieRepository } from '@/repositories/discrepancies/apiDiscrepancieRepository'

export class DiscrepacieApplicationService {
    constructor(private readonly repository: ApiDiscrepancieRepository) {}

    async listDiscrepancie(projectId: string | number, params?: Record<string, any>) {
        return await this.repository.list(projectId, params)
    }

    async postDiscrepancies(projectId: string | number, data: any) {
        return await this.repository.postDiscrepancies(projectId, data)
    }

    async getDiscrepanciesDB(projectId: string | number) {
        return await this.repository.listDB(projectId)
    }

    async updateDiscrepancyStatus(projectId: string | number, question: string) {
        return await this.repository.updateDiscrepancyStatus(projectId, question)
    }
}