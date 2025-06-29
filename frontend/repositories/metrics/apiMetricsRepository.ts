import ApiService from '@/services/api.service'
import { Distribution, MyProgress, Progress } from '~/domain/models/metrics/metrics'

export class APIMetricsRepository {
  constructor(private readonly request = ApiService) {}

  async fetchCategoryDistribution(projectId: string): Promise<Distribution> {
    const url = `/projects/${projectId}/metrics/category-distribution`
    const response = await this.request.get(url)
    return response.data
  }

  async fetchSpanDistribution(projectId: string): Promise<Distribution> {
    const url = `/projects/${projectId}/metrics/span-distribution`
    const response = await this.request.get(url)
    return response.data
  }

  async fetchRelationDistribution(projectId: string): Promise<Distribution> {
    const url = `/projects/${projectId}/metrics/relation-distribution`
    const response = await this.request.get(url)
    return response.data
  }

  async fetchMemberProgress(projectId: string): Promise<Progress> {
    const url = `/projects/${projectId}/metrics/member-progress`
    const response = await this.request.get(url)
    return response.data
  }

  async fetchMyProgress(projectId: string): Promise<MyProgress> {
    const url = `/projects/${projectId}/metrics/progress`
    const response = await this.request.get(url)
    return response.data
  }
  
  async fetchDatasetStatistics(projectId: string, queryParams: string = '') {
  // Make sure we're not adding an extra question mark
    const url = `/projects/${projectId}/metrics/dataset${queryParams}`;
    console.log('Requesting URL:', url);
    const response = await this.request.get(url);
    return response.data;
  }

  /**
   * Obtém o relatório (PDF) de dataset para o projecto.
   * @param projectId ID do projecto
   * @param queryParams string de query (ex: ?version_id=3)
   */
  async fetchDatasetReport(projectId: string, queryParams: string = '') {
    const url = `/projects/${projectId}/metrics/dataset-report${queryParams}`
    // Important: definir responseType blob para receber o PDF
    const response = await this.request.get(url, { responseType: 'blob' })
    return response.data // blob
  }
}
