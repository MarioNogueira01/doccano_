<template>
  <v-card>
    <v-card-title class="align-center flex-wrap">
      <h2 class="text-h6 mb-4 mb-md-0 me-md-4">Relatório de Anotações</h2>

      <!-- Select Dataset -->
      <v-select
        v-model="selectedDataset"
        :items="datasetOptions"
        item-text="text"
        item-value="value"
        label="Dataset"
        dense
        hide-details
        class="me-2"
        style="max-width: 200px"
      />

      <!-- Filtro de Labels -->
      <v-select
        v-model="selectedLabels"
        :items="labelOptions"
        label="Labels"
        multiple
        chips
        deletable-chips
        clearable
        dense
        hide-details
        class="me-2"
        style="max-width: 300px"
      />

      <!-- Filtro de Acordo -->
      <v-select
        v-model="selectedAgreement"
        :items="agreementOptions"
        label="Acordo"
        dense
        hide-details
        clearable
        class="me-2"
        style="max-width: 200px"
      />

      <!-- Button / dialog for filtering by Perspective answers -->
      <v-dialog v-model="perspectiveFilterDialog" max-width="600px">
        <template #activator="{ on, attrs }">
          <v-btn color="primary" dark class="me-2" v-bind="attrs" v-on="on">
            Filtrar por Perspectiva
          </v-btn>
        </template>
        <v-card>
          <v-card-title>Filtro de Perspectivas</v-card-title>
          <v-card-text>
            <v-container>
              <v-row v-for="group in perspectiveGroups" :key="group.id">
                <v-col cols="12">
                  <h3>{{ group.name }}</h3>
                  <v-row v-for="question in group.questions" :key="question.id">
                    <v-col cols="12">
                      <v-select
                        v-if="question.data_type === 'string' && question.options.length > 0"
                        v-model="selectedPerspectiveAnswers[question.id]"
                        :items="question.options"
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
                        clearable
                      />
                      <v-text-field
                        v-else
                        v-model="selectedPerspectiveAnswers[question.id]"
                        :label="question.question"
                        type="number"
                        clearable
                      />
                    </v-col>
                  </v-row>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn color="primary" text @click="applyPerspectiveFilters">Aplicar</v-btn>
            <v-btn text @click="clearPerspectiveFilters">Limpar</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <v-spacer />

      <!-- Botão para Gerar Relatório -->
      <v-btn
        color="primary"
        class="me-2"
        @click="generateReport"
      >
        Gerar Relatório
      </v-btn>

      <!-- Export buttons -->
      <v-btn color="primary" outlined class="me-2" @click="exportCSV">
        Exportar CSV
      </v-btn>
      <v-btn color="primary" outlined @click="exportPDF">
        Exportar PDF
      </v-btn>
    </v-card-title>

    <v-divider />

    <v-card-text>
      <v-data-table
        :headers="tableHeaders"
        :items="tableData"
        class="elevation-1"
        :search="search"
      >
        <template #top>
          <v-text-field
            v-model="search"
            label="Pesquisar"
            class="mx-4"
          />
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: 'HistoryStats',
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],
  data () {
    return {
      stats: [],
      progress: 100,
      datasetOptions: [{ text: 'Todos os Datasets', value: null }],
      selectedDataset: null,
      labelOptions: [],
      selectedLabels: [],
      agreementOptions: [
        { text: 'Todos', value: null },
        { text: 'Com Acordo', value: 'agreement' },
        { text: 'Sem Acordo', value: 'disagreement' }
      ],
      selectedAgreement: null,
      perspectiveFilterDialog: false,
      perspectiveGroups: [],
      selectedPerspectiveAnswers: {},
      search: '',
      tableHeaders: [
        { text: 'Dataset', value: 'dataset' },
        { text: 'Label', value: 'label' },
        { text: 'Nº de Votos', value: 'votes' },
        { text: 'Acordo', value: 'agreement' }
      ]
    }
  },
  computed: {
    projectId () { return this.$route.params.id },
    tableData() {
      const aggregation = {}

      this.stats.forEach(s => {
        const datasetName = s.dataset
        s.labels.forEach((label, idx) => {
          const agreementPercentage = s.agreement ? s.agreement[idx] : null

          // Filtro de Acordo
          if (this.selectedAgreement) {
            const hasAgreement = agreementPercentage !== null && agreementPercentage >= 70
            if (this.selectedAgreement === 'agreement' && !hasAgreement) return
            if (this.selectedAgreement === 'disagreement' && hasAgreement) return
          }

          // Aplica o filtro de labels aqui
          if (this.selectedLabels.length > 0 && !this.selectedLabels.includes(label)) {
            return // Pula esta label se não estiver selecionada
          }

          const key = `${datasetName}-${label}`
          if (!aggregation[key]) {
            aggregation[key] = {
              dataset: datasetName,
              label,
              votes: 0,
              agreement: agreementPercentage
            }
          }
          aggregation[key].votes += s.votes[idx]
        })
      })
      
      const tableRows = Object.values(aggregation)
      return tableRows.map(row => ({
        ...row,
        agreement: row.agreement !== null ? (row.agreement >= 70 ? 'Acordo' : 'Desacordo') : 'N/A'
      }))
    }
  },
  watch: {
    // Bloco watch removido
  },
  async mounted () {
    // Apenas carrega as opções dos filtros, não os dados da tabela
    try {
      const remoteDatasets = await this.$repositories.stats.datasets(this.projectId)
      this.datasetOptions = [{ text: 'Todos os Datasets', value: null }, ...remoteDatasets]
    } catch (e) { /* ignore */ }

    try {
      const labels = await this.$repositories.label.list(this.projectId)
      this.labelOptions = labels.map(label => label.text)
    } catch (e) { console.error('Failed to load labels', e) }

    try {
      const response = await this.$services.perspective.listPerspectiveGroups(this.projectId)
      this.perspectiveGroups = response.results || response.data?.results || []
    } catch (e) { console.error('Failed to load perspective groups', e) }
  },
  methods: {
    // onDatasetChange removido
    generateReport() {
      this.fetchStats();
    },
    applyPerspectiveFilters () {
      this.perspectiveFilterDialog = false
      // Já não chama a busca de dados
    },
    clearPerspectiveFilters () {
      this.selectedPerspectiveAnswers = {}
      this.perspectiveFilterDialog = false
      // Já não chama a busca de dados
    },
    buildParams () {
      const params = {}
      if (this.selectedDataset) {
        params.dataset = this.selectedDataset
      }
      if (this.progress !== null && this.progress !== 100) params.progress = this.progress

      if (Object.keys(this.selectedPerspectiveAnswers).length > 0) {
        params.perspective_filters = JSON.stringify(this.selectedPerspectiveAnswers)
      }
      return params
    },
    async fetchStats () {
      const baseParams = this.buildParams()
      delete baseParams.dataset

      if (this.selectedDataset === null) {
        const allStats = []
        const datasetsToFetch = this.datasetOptions
          .filter(d => d.value !== null)
          .map(d => d.value)

        for (const datasetId of datasetsToFetch) {
          const params = { ...baseParams, dataset: datasetId }
          const statsForDataset = await this.$repositories.stats.labelVotes(this.projectId, params)
          const statsWithDatasetName = statsForDataset.map(s => ({ ...s, dataset: datasetId }))
          allStats.push(...statsWithDatasetName)
        }
        this.stats = allStats
      } else {
        const params = { ...baseParams, dataset: this.selectedDataset }
        const statsForDataset = await this.$repositories.stats.labelVotes(this.projectId, params)
        this.stats = statsForDataset.map(s => ({ ...s, dataset: this.selectedDataset }))
      }
    },
    exportCSV () {
      const delimiter = ';'
      const rows = [
        ['Dataset', 'Label', 'Nº de Votos', 'Acordo']
      ]

      this.tableData.forEach(item => {
        rows.push([item.dataset, item.label, item.votes, item.agreement])
      })

      const csvContent = '\uFEFF' +
        rows
          .map(r => r.map(item => {
            const field = String(item)
            const needsQuotes = field.includes(delimiter) || field.includes('"') || field.includes('\n')
            const escaped = field.replace(/"/g, '""')
            return needsQuotes ? `"${escaped}"` : escaped
          }).join(delimiter))
          .join('\r\n')

      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `hist_stats_${new Date().toISOString()}.csv`)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    },
    async loadJsPDF () {
      if (window.jspdf && window.jspdf.jsPDF) {
        if (!window.jspdf.jsPDF.API.autoTable) {
          await new Promise((resolve, reject) => {
            const script = document.createElement('script')
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.5.29/jspdf.plugin.autotable.min.js'
            script.onload = resolve
            script.onerror = reject
            document.body.appendChild(script)
          })
        }
        return window.jspdf.jsPDF
      }
      await new Promise((resolve, reject) => {
        const script = document.createElement('script')
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js'
        script.onload = resolve
        script.onerror = reject
        document.body.appendChild(script)
      })
      await new Promise((resolve, reject) => {
        const script = document.createElement('script')
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.5.29/jspdf.plugin.autotable.min.js'
        script.onload = resolve
        script.onerror = reject
        document.body.appendChild(script)
      })
      return window.jspdf.jsPDF
    },
    async exportPDF () {
      try {
        const jsPDF = await this.loadJsPDF()
        // eslint-disable-next-line new-cap
        const doc = new jsPDF({ orientation: 'p', unit: 'mm', format: 'a4' })

        const pageWidth = doc.internal.pageSize.getWidth()
        const pageHeight = doc.internal.pageSize.getHeight()
        const margin = 18

        doc.setFillColor(63, 81, 181)
        doc.rect(0, 0, pageWidth, 20, 'F')
        doc.setFontSize(16)
        doc.setTextColor(255, 255, 255)
        doc.setFont(undefined, 'bold')
        doc.text('Relatório de Anotações', pageWidth / 2, 13, { align: 'center' })

        doc.setTextColor(0, 0, 0)

        const addFooter = (pageNum, totalPages) => {
          doc.setFontSize(8)
          doc.setTextColor(150)
          doc.text(`Página ${pageNum} / ${totalPages}`, pageWidth / 2, pageHeight - 5, { align: 'center' })
          doc.setTextColor(0)
        }

        const tableBody = this.tableData.map(item => [item.dataset, item.label, 
        item.votes, item.agreement])
        doc.autoTable({
          head: [['Dataset', 'Label', 'Nº de Votos', 'Acordo']],
          body: tableBody,
          startY: 28,
          margin: { left: margin, right: margin },
          theme: 'grid',
          headStyles: { fillColor: [63, 81, 181], halign: 'center', valign: 'middle', textColor: 255 },
          bodyStyles: { halign: 'center' },
          styles: { fontSize: 9 },
          didDrawPage: (d) => {
            if (d.pageNumber > 1) {
              doc.setFillColor(63, 81, 181)
              doc.rect(0, 0, pageWidth, 20, 'F')
              doc.setFontSize(16)
              doc.setTextColor(255)
              doc.setFont(undefined, 'bold')
              doc.text('Relatório de Anotações', pageWidth / 2, 13, { align: 'center' })
              doc.setTextColor(0)
            }
          }
        })

        const totalPages = doc.getNumberOfPages()
        for (let i = 1; i <= totalPages; i++) {
          doc.setPage(i)
          addFooter(i, totalPages)
        }

        doc.save(`hist_stats_${new Date().toISOString()}.pdf`)
      } catch (e) {
        console.error('Falha ao exportar PDF', e)
        this.$toast?.error?.('Não foi possível exportar o PDF')
      }
    }
  }
}
</script>

<style scoped>
</style>