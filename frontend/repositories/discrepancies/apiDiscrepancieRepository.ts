import ApiService from '@/services/api.service'


export class ApiDiscrepancieRepository {


    async list(projectId: string | number, params?: { threshold?: number }) {
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
}