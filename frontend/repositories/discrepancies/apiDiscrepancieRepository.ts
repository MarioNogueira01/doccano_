import ApiService from '@/services/api.service'


export class ApiDiscrepancieRepository {


    async list(projectId: string | number, params?: Record<string, any>) {
        const url = `/projects/${projectId}/discrepacies`
        const response = await ApiService.get(url, { params })
        return response.data
    }

    async postDiscrepancies(projectId: string | number, data: any) {
        const url = `/projects/${projectId}/discrepancies/postdiscrepancies`
        console.log('Posting discrepancies:', data)

        const response = await ApiService.post(url, data)
        return response.data
    }

    async listDB(projectId: string | number) {
        const url = `/projects/${projectId}/discrepancies`
        const response = await ApiService.get(url)
        return response.data
    }

    async updateDiscrepancyStatus(projectId: string | number, question: string) {
        const url = `/projects/${projectId}/discrepancies/${encodeURIComponent(question)}/update-status`
        const response = await ApiService.patch(url)
        return response.data
    }
}