<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex align-center flex-wrap">
            <span class="text-h6 mr-4">History Statistics</span>
            <v-select
              v-model="selectedVersionId"
              :items="versionOptions"
              label="Version"
              dense
              hide-details
              style="max-width:120px"
              class="mr-4"
              @change="fetchStats"
            />
            <v-spacer></v-spacer>
            <!-- Export buttons (placeholder) -->
            <v-btn color="primary" outlined class="mr-2" @click="exportCSV">
              Export CSV
            </v-btn>
            <v-btn color="primary" outlined @click="exportPDF">
              Export PDF
            </v-btn>
          </v-card-title>

          <v-divider />

          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="stats"
              class="elevation-1"
            >
              <!-- eslint-disable-next-line vue/valid-v-slot -->
              <template #item.status="{ item }">
                <v-chip :color="item.annotated ? 'success' : 'warning'" small>
                  {{ item.annotated ? 'Annotated' : 'Pending' }}
                </v-chip>
              </template>
              <!-- eslint-disable-next-line vue/valid-v-slot -->
              <template #item.chart="{ item }">
                <div>
                  <div
                    v-for="(label, idx) in item.labels"
                    :key="label"
                    class="mb-1 d-flex align-center"
                  >
                    <!-- Label -->
                    <span style="width:80px">{{ label }}</span>

                    <!-- Barra de progresso -->
                    <v-progress-linear
                      :value="getPercentage(item, idx)"
                      color="primary"
                      height="14"
                      rounded
                      class="flex-grow-1 mx-2"
                      background-opacity="0.15"
                    />

                    <!-- Percentagem -->
                    <span style="width:40px;text-align:right;">
                      {{ getPercentage(item, idx).toFixed(1) }}%
                    </span>
                  </div>
                </div>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],
  data () {
    return {
      stats: [],
      versions: [],
      selectedVersionId: null,
      headers: [
        { text: 'ID', value: 'id' },
        { text: 'Text', value: 'text' },
        { text: 'Status', value: 'status' },
        { text: 'Label Distribution', value: 'chart', sortable: false }
      ]
    }
  },
  computed: {
    versionOptions () {
      return this.versions.map(v => ({ text: `v${v.version}`, value: v.version }))
    }
  },
  mounted () {
    this.loadVersions()
  },
  methods: {
    async loadVersions () {
      try {
        const res = await this.$services.project.listVersions(this.$route.params.id)
        const list = Array.isArray(res) ? res : (res.versions || [])
        this.versions = list
        if (list.length) {
          this.selectedVersionId = list[0].version
        }
        this.fetchStats()
      } catch (e) {
        console.error('Erro ao carregar versões', e)
        this.fetchStats()
      }
    },
    fetchStats () {
      const params = new URLSearchParams()
      params.append('page', '1')
      params.append('page_size', '100')
      if (this.selectedVersionId) {
        params.append('version_id', this.selectedVersionId)
      }
      const url = params.toString() ? `?${params.toString()}` : ''
      this.$repositories.metrics.fetchDatasetStatistics(this.$route.params.id, url)
        .then((data) => {
          if (!data || !data.entries) {
            this.stats = []
            return
          }
          this.stats = data.entries.map((e) => {
            const labels = Object.keys(e.labelDistribution || {})
            const votesArr = labels.map((l) => e.labelDistribution[l])
            return {
              id: e.id,
              text: e.text,
              annotated: e.annotated,
              labels,
              votes: votesArr.length ? votesArr : [0],
            }
          })
        })
        .catch((err) => {
          console.error('Erro ao buscar estatísticas:', err)
          this.stats = []
        })
    },
    exportCSV () {
      try {
        const delimiter = ';'
        // Cabeçalho CSV
        const rows = [
          ['ID', 'Text', 'Status', 'Label', 'Percentage']
        ]

        // Para cada exemplo e respectiva distribuição de labels
        this.stats.forEach((item) => {
          const { id, text, annotated, labels, votes } = item
          const total = votes.reduce((a, b) => a + b, 0) || 1
          labels.forEach((label, idx) => {
            const percentage = ((votes[idx] / total) * 100).toFixed(1)
            rows.push([
              id,
              text.replace(/\n/g, ' ').substring(0, 200),
              annotated ? 'Annotated' : 'Pending',
              label,
              percentage + '%'
            ])
          })
        })

        const csvContent = '\uFEFF' + rows.map(r => r.map(field => {
          const f = String(field)
          const needsQuotes = f.includes(delimiter) || f.includes('"') || f.includes('\n')
          const escaped = f.replace(/"/g, '""')
          return needsQuotes ? `"${escaped}"` : escaped
        }).join(delimiter)).join('\r\n')

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `history_stats_${new Date().toISOString()}.csv`)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        this.$toasted?.success('CSV exportado!')
      } catch (err) {
        console.error('Erro exportando CSV:', err)
        this.$toasted?.error('Falha ao exportar CSV')
      }
    },
    async exportPDF () {
      try {
        const JsPDF = await this.loadJsPDF()
        const doc = new JsPDF({ orientation: 'p', unit: 'mm', format: 'a4' })
        const margin = 15
        const pageWidth = doc.internal.pageSize.getWidth()

        // Título
        doc.setFontSize(18)
        doc.text('History Statistics', pageWidth / 2, 20, { align: 'center' })

        // Informação da versão
        const versionText = this.selectedVersionId ? `Version: v${this.selectedVersionId}` : 'All versions'
        doc.setFontSize(12)
        doc.text(versionText, margin, 30)

        // Montar dados para a tabela
        const tableHead = [['ID', 'Text', 'Status', 'Label', '%']]
        const tableBody = []

        this.stats.forEach((item) => {
          const total = item.votes.reduce((a, b) => a + b, 0) || 1
          item.labels.forEach((label, idx) => {
            tableBody.push([
              String(item.id),
              item.text.substring(0, 60) + (item.text.length > 60 ? '...' : ''),
              item.annotated ? 'Annotated' : 'Pending',
              label,
              ((item.votes[idx] / total) * 100).toFixed(1) + '%'
            ])
          })
        })

        // @ts-ignore autoTable disponible no runtime
        doc.autoTable({
          startY: 40,
          head: tableHead,
          body: tableBody,
          margin: { left: margin, right: margin },
          theme: 'grid',
          styles: { fontSize: 9 },
          headStyles: { fillColor: [63, 81, 181], textColor: 255 },
        })

        // Abrir em nova aba
        const pdfBlob = doc.output('blob')
        const url = URL.createObjectURL(pdfBlob)
        window.open(url, '_blank')
        this.$toasted?.success('PDF aberto em nova aba')
      } catch (e) {
        console.error('Erro exportando PDF', e)
        this.$toasted?.error('Falha ao exportar PDF')
      }
    },
    async loadJsPDF () {
      // Se já carregado, reutiliza
      if (window.jspdf && window.jspdf.jsPDF) {
        if (!window.jspdf.jsPDF.API.autoTable) {
          await this.loadAutoTable()
        }
        return window.jspdf.jsPDF
      }
      // Carrega jsPDF
      await new Promise((resolve, reject) => {
        const script = document.createElement('script')
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js'
        script.onload = resolve
        script.onerror = reject
        document.body.appendChild(script)
      })
      await this.loadAutoTable()
      return window.jspdf.jsPDF
    },
    loadAutoTable () {
      return new Promise((resolve, reject) => {
        const script = document.createElement('script')
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.5.29/jspdf.plugin.autotable.min.js'
        script.onload = resolve
        script.onerror = reject
        document.body.appendChild(script)
      })
    },
    getPercentage (item, idx) {
      const totalVotes = item.votes.reduce((a, b) => a + b, 0)
      return (item.votes[idx] / totalVotes) * 100
    }
  }
}
</script>

<style scoped>
/* Nenhum estilo extra, o visual será herdado do tema principal */
</style> 