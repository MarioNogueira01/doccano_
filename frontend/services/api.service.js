import axios from 'axios'
import { API_URL } from '../constants'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

class ApiService {
  constructor() {
    this.axios = axios.create({
      baseURL: API_URL,
      withCredentials: true,
      paramsSerializer: (params) => {
        const parts = []
        for (const key in params) {
          if (Object.prototype.hasOwnProperty.call(params, key)) {
            const value = params[key]
            if (Array.isArray(value)) {
              value.forEach((item) => {
                parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(item)}`)
              })
            } else {
              parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
            }
          }
        }
        return parts.join("&")
      }
    })
    this.axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // No Nuxt, o store é injetado no contexto da aplicação
          // O logout será tratado pelo middleware de autenticação
          window.location.href = '/login'
        }
        // Erro 503 será tratado por um interceptor global (plugins/db-down.js). Se
        // este módulo for usado isoladamente fora do Nuxt ainda queremos
        // propagar o erro, por isso não mostramos UI aqui.
        return Promise.reject(error)
      }
    )
  }

  request(method, url, data = {}, config = {}) {
    return this.axios({
      method,
      url,
      data,
      ...config
    })
  }

  get(url, config = {}) {
    return this.request('get', url, {}, config)
  }

  post(url, data = {}, config = {}) {
    return this.request('post', url, data, config)
  }

  put(url, data = {}, config = {}) {
    return this.request('put', url, data, config)
  }

  patch(url, data = {}, config = {}) {
    return this.request('patch', url, data, config)
  }

  delete(url, dataOrConfig = {}, config = {}) {
    // Para manter compatibilidade com chamadas existentes, verificamos se o segundo
    // argumento parece ser um objeto de configuração (já contém a chave `data` ou
    // outras chaves típicas de config). Caso afirmativo, delegamos tal qual era
    // antes. Caso contrário, consideramos que o segundo argumento contém o corpo
    // da requisição e passamos opcionalmente um terceiro argumento de config.
    if (
      dataOrConfig &&
      typeof dataOrConfig === 'object' &&
      !Array.isArray(dataOrConfig) &&
      (
        Object.prototype.hasOwnProperty.call(dataOrConfig, 'data') ||
        Object.prototype.hasOwnProperty.call(dataOrConfig, 'params') ||
        Object.prototype.hasOwnProperty.call(dataOrConfig, 'headers') ||
        Object.prototype.hasOwnProperty.call(dataOrConfig, 'timeout')
      )
    ) {
      // Mantém o comportamento antigo: dados são fornecidos dentro de config.data
      return this.request('delete', url, {}, dataOrConfig)
    }

    // Novo comportamento: segundo argumento é o corpo, terceiro é o config opcional
    return this.request('delete', url, dataOrConfig, config)
  }
}

export default new ApiService()
