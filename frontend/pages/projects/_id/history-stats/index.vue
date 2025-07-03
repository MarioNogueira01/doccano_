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
            <!-- Filtro Dataset -->
            <v-select
              v-model="selectedDataset"
              :items="datasetOptions"
              item-text="text"
              item-value="value"
              label="Dataset"
              dense
              hide-details
              clearable
              style="max-width:200px"
              class="mr-4"
            />

            <!-- Filtro Acordo -->
            <v-select
              v-model="selectedAgreement"
              :items="agreementOptions"
              label="Agreement"
              dense
              hide-details
              clearable
              style="max-width:160px"
              class="mr-4"
            />
            <v-btn color="primary" class="mr-2" @click.prevent="generateReport">
              Generate Report
            </v-btn>
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
            <v-expansion-panels flat>
              <v-expansion-panel>
                <v-expansion-panel-header>
                  Perspective
                  <template #actions>
                    <v-icon color="primary">mdi-filter-variant</v-icon>
                  </template>
                </v-expansion-panel-header>
                <v-expansion-panel-content>
                  <v-container>
                    <v-row v-for="group in perspectiveGroups" :key="group.id">
                      <v-col cols="12">
                        <h3>{{ group.name }}</h3>
                        <v-row v-for="question in group.questions" :key="question.id">
                          <v-col cols="12">
                            <v-select
                              v-if="question.data_type === 'string' && question.options.length > 0"
                              v-model="selectedPerspectiveAnswers[question.id]"
                              :items="question.options.map(String)"
                              :label="question.question"
                              multiple
                              chips
                              deletable-chips
                              clearable
                            />
                            <v-select
                              v-else-if="question.data_type === 'boolean'"
                              v-model="selectedPerspectiveAnswers[question.id]"
                              :items="['Yes', 'No']"
                              :label="question.question"
                              multiple
                              chips
                              deletable-chips
                              clearable
                            />
                            <v-text-field
                              v-else-if="question.data_type === 'int'"
                              v-model="selectedPerspectiveAnswers[question.id]"
                              :label="question.question"
                              type="number"
                              clearable
                              placeholder="Enter a number"
                            />
                            <v-text-field
                              v-else
                              v-model="selectedPerspectiveAnswers[question.id]"
                              :label="question.question"
                              clearable
                              placeholder="Enter text"
                            />
                          </v-col>
                        </v-row>
                      </v-col>
                    </v-row>
                  </v-container>
                  <v-card-actions>
                    <v-spacer />
                    <v-btn text @click="clearPerspectiveFilters">Limpar Filtros</v-btn>
                  </v-card-actions>
                </v-expansion-panel-content>
              </v-expansion-panel>
            </v-expansion-panels>

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
      ],
      perspectiveGroups: [],
      selectedPerspectiveAnswers: {},
      // Dataset & Agreement filtros
      datasetOptions: [{ text: 'All Datasets', value: null }],
      selectedDataset: null,
      agreementOptions: [
        { text: 'All', value: null },
        { text: 'Agreement', value: 'agreement' },
        { text: 'Disagreement', value: 'disagreement' }
      ],
      selectedAgreement: null,
      discrepancyIds: new Set()
    }
  },
  computed: {
    versionOptions () {
      return this.versions.map(v => ({ text: `v${v.version}`, value: v.version }))
    }
  },
  mounted () {
    this.loadVersions()
    this.loadPerspectiveGroups()
    this.loadDatasets()
    this.loadDiscrepancies()
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
    async loadPerspectiveGroups () {
      try {
        const response = await this.$services.perspective.listPerspectiveGroups(
          this.$route.params.id
        ) // eslint-disable-line max-len
        this.perspectiveGroups = response.results || response.data?.results || []
      } catch (e) {
        console.error('Failed to load perspective groups', e)
      }
    },
    async loadDatasets () {
      try {
        const data = await this.$repositories.stats.datasets(this.$route.params.id)
        this.datasetOptions = [{ text: 'All Datasets', value: null }, ...data]
      } catch (e) {
        console.error('Erro ao carregar datasets', e)
      }
    },
    async loadDiscrepancies () {
      try {
        const resp = await this.$repositories.discrepancy.list(this.$route.params.id)
        const list = resp.discrepancies || resp || []
        this.discrepancyIds = new Set(list.filter(d => d.is_discrepancy).map(d => d.id))
      } catch (e) {
        console.error('Erro ao buscar discrepâncias', e)
        this.discrepancyIds = new Set()
      }
    },
    clearPerspectiveFilters () {
      this.selectedPerspectiveAnswers = {}
    },
    generateReport () {
      this.fetchStats()
    },
    fetchStats () {
      const params = new URLSearchParams()
      params.append('page', '1')
      params.append('page_size', '100')
      if (this.selectedVersionId) {
        params.append('version_id', this.selectedVersionId)
      }
      if (this.selectedDataset !== null) {
        params.append('dataset', this.selectedDataset)
      }
      // Construir objeto apenas com respostas preenchidas
      const activePerspectiveFilters = Object.fromEntries(
        Object.entries(this.selectedPerspectiveAnswers)
          .filter(([_, v]) => {
            if (Array.isArray(v)) { return v.length > 0 }
            return v !== null && v !== undefined && v !== ''
          })
      )
      if (Object.keys(activePerspectiveFilters).length > 0) {
        params.append('perspective_filters', JSON.stringify(activePerspectiveFilters))
      }
      const url = params.toString() ? `?${params.toString()}` : ''
      this.$repositories.metrics.fetchDatasetStatistics(this.$route.params.id, url)
        .then((data) => {
          if (!data || !data.entries) {
            this.stats = []
            return
          }
          const mapped = data.entries.map((e) => {
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
          // Marcar acordo/disacordo baseado em discrepâncias
          mapped.forEach(m => {
            m.agreement = this.discrepancyIds.has(m.id) ? 'disagreement' : 'agreement'
          })

          // Filtrar por acordo se necessário
          this.stats = this.selectedAgreement
            ? mapped.filter(m => m.agreement === this.selectedAgreement)
            : mapped
        })
        .catch((err) => {
          console.error('Erro ao buscar estatísticas:', err)
          this.stats = []
        })
    },
    exportCSV () {
      try {
        const delimiter = ','
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
        // eslint-disable-next-line new-cap
        const doc = new JsPDF({ orientation: 'p', unit: 'mm', format: 'a4' })

        const pageWidth = doc.internal.pageSize.getWidth()
        const pageHeight = doc.internal.pageSize.getHeight()
        const margin = 18

        // Cabeçalho (barra azul)
        const drawHeader = () => {
          doc.setFillColor(63, 81, 181)
          doc.rect(0, 0, pageWidth, 20, 'F')
          doc.setFontSize(16)
          doc.setTextColor(255, 255, 255)
          doc.setFont(undefined, 'bold')
          doc.text('History Statistics', pageWidth / 2, 13, { align: 'center' })

          // Sub-título com versão
          doc.setFontSize(9)
          const versionTxt = this.selectedVersionId ? `Version: v${this.selectedVersionId}` : 'All versions'
          doc.text(versionTxt, margin, 17)
          doc.setTextColor(0)
        }

        drawHeader()

        const addFooter = (pageNum, totalPages) => {
          doc.setFontSize(8)
          doc.setTextColor(150)
          doc.text(`Página ${pageNum} / ${totalPages}`, pageWidth / 2, pageHeight - 5, { align: 'center' })
          doc.setTextColor(0)
        }

        // Preparar dados da tabela sem informação repetida
        const tableBody = this.stats.map(item => {
          const total = item.votes.reduce((a, b) => a + b, 0) || 1
          const dist = item.labels.map((label, idx) => {
            const perc = ((item.votes[idx] / total) * 100).toFixed(1)
            return `${label} (${perc}%)`
          }).join(', ')
          return [
            String(item.id),
            item.text.substring(0, 60) + (item.text.length > 60 ? '...' : ''),
            item.annotated ? 'Annotated' : 'Pending',
            dist
          ]
        })

        doc.autoTable({
          head: [['ID', 'Text', 'Status', 'Label Distribution']],
          body: tableBody,
          startY: 25, // imediatamente após o cabeçalho
          margin: { left: margin, right: margin },
          theme: 'grid',
          styles: { fontSize: 9 },
          headStyles: { fillColor: [63, 81, 181], halign: 'center', valign: 'middle', textColor: 255 },
          bodyStyles: { halign: 'center' },
          didDrawPage: (data) => {
            if (data.pageNumber > 1) {
              drawHeader()
            }
          }
        })

        // Adicionar rodapé em todas as páginas
        const totalPages = doc.getNumberOfPages()
        for (let i = 1; i <= totalPages; i++) {
          doc.setPage(i)
          addFooter(i, totalPages)
        }

        doc.save(`history_stats_${new Date().toISOString()}.pdf`)
      } catch (e) {
        console.error('Falha ao exportar PDF', e)
        this.$toasted?.error('Não foi possível exportar o PDF')
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