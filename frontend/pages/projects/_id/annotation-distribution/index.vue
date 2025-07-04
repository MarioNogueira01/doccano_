<template>
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title>Dataset Entries</v-card-title>
            <v-card-text>
              <v-data-table
                :headers="headers"
                :items="datasetStats.entries"
                :loading="loadingStats"
                :options.sync="options"
                :server-items-length="datasetStats.total"
                class="elevation-1"
              >
                <template #item="{ item: _item }">
                  <tr>
                    <td>{{ _item.id }}</td>
                    <td>{{ _item.text }}</td>
                    <td>
                      <v-chip
                        :color="_item.annotated ? 'success' : 'warning'"
                        small
                      >
                        {{ _item.annotated ? 'Annotated' : 'Pending' }}
                      </v-chip>
                    </td>
                    <td>{{ _item.categoryCount || 0 }}</td>
                    <td>{{ _item.spanCount || 0 }}</td>
                    <td>{{ _item.relationCount || 0 }}</td>
                    <td style="width: 80px">
                      <div style="height: 40px">
                        <bar-chart
                          :chart-data="getChartData(_item)"
                          :options="{
                            responsive: true,
                            maintainAspectRatio: false,
                            legend: {
                              display: false
                            },
                            scales: {
                              x: {
                                display: false,
                                stacked: true,
                                ticks: {
                                  display: false
                                }
                              },
                              y: {
                                display: false,
                                stacked: true
                              }
                            },
                            barPercentage: 1.0,
                            categoryPercentage: 0.9,
                            animation: {
                              duration: 0
                            }
                          }"
                        />
                      </div>
                    </td>
                  </tr>
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </template>
  
  <script>
  import { mapGetters } from 'vuex'
  import BarChart from '~/components/metrics/ChartBar'
  
  export default {
    components: {
      BarChart
    },
  
    layout: 'project',
  
    middleware: ['check-auth', 'auth', 'setCurrentProject'],
  
    validate({ params }) {
      return /^\d+$/.test(params.id)
    },
  
    data() {
      return {
        datasetStats: {
          total: 0,
          annotated: 0,
          unannotated: 0,
          entries: []
        },
        loadingStats: false,
        headers: [
          { text: 'ID', value: 'id', width: '80px' },
          { text: 'Text', value: 'text' },
          { text: 'Status', value: 'status', width: '100px' },
          { text: 'Categories', value: 'categoryCount', width: '100px' },
          { text: 'Spans', value: 'spanCount', width: '100px' },
          { text: 'Relations', value: 'relationCount', width: '100px' },
          { text: 'Label Distribution', value: 'distribution', width: '100px' }
        ],
        options: {
          sortBy: ['id'],
          sortDesc: [false],
          page: 1,
          itemsPerPage: 10
        },
        labelTypes: {
          categories: [],
          spans: [],
          relations: []
        },
        labelDistribution: {}
      }
    },
  
    computed: {
      ...mapGetters('projects', ['project']),
  
      projectId() {
        return this.$route.params.id
      }
    },
  
    watch: {
      options: {
        handler() {
          this.fetchDatasetStats()
        },
        deep: true
      }
    },
  
    async created() {
      await Promise.all([
        this.fetchDatasetStats(),
        this.fetchLabelTypes(),
        this.fetchLabelDistribution()
      ])
    },
  
    methods: {
      async fetchDatasetStats() {
        this.loadingStats = true
        try {
          const params = new URLSearchParams()
          params.append('page', this.options.page)
          params.append('page_size', this.options.itemsPerPage)
          
          if (this.options.sortBy && this.options.sortBy.length > 0) {
            const sortDirection = this.options.sortDesc[0] ? '-' : ''
            params.append('ordering', `${sortDirection}${this.options.sortBy[0]}`)
          }
  
          const queryString = params.toString()
          const url = queryString ? `?${queryString}` : ''
  
          const stats = await this.$repositories.metrics.fetchDatasetStatistics(
            this.projectId,
            url
          )
          this.datasetStats = stats
          console.log('Dataset stats sample:', stats.entries[0])
        } catch (error) {
          console.error('Error fetching dataset stats:', error)
          this.$toasted.error('Failed to load dataset statistics')
        } finally {
          this.loadingStats = false
        }
      },
  
      async fetchLabelTypes() {
        try {
          const [categories, spans, relations] = await Promise.all([
            this.$services.categoryType.list(this.projectId),
            this.$services.spanType.list(this.projectId),
            this.$services.relationType.list(this.projectId)
          ])
          
          console.log('Fetched label types:', {
            categories,
            spans,
            relations
          })
  
          this.labelTypes = {
            categories,
            spans,
            relations
          }
        } catch (error) {
          console.error('Error fetching label types:', error)
        }
      },
  
      async fetchLabelDistribution() {
        try {
          const [categoryDist, spanDist, relationDist] = await Promise.all([
            this.$repositories.metrics.fetchCategoryDistribution(this.projectId),
            this.$repositories.metrics.fetchSpanDistribution(this.projectId),
            this.$repositories.metrics.fetchRelationDistribution(this.projectId)
          ])
  
          console.log('Fetched distributions:', {
            categories: categoryDist,
            spans: spanDist,
            relations: relationDist
          })
  
          this.labelDistribution = {
            categories: categoryDist,
            spans: spanDist,
            relations: relationDist
          }
        } catch (error) {
          console.error('Error fetching label distribution:', error)
        }
      },
  
      getChartData(_item) {
        const labels = []
        const data = []
        const colors = ['#4CAF50', '#2196F3', '#FFC107', '#9C27B0', '#FF5722', '#795548']
        
        // Check if we have manual labels for this document - these are the detailed annotations
        if (!_item.labels || _item.labels.length === 0) {
          // If no manual labels, create a simplified representation based on counts
          if (_item.categoryCount > 0) {
            // Since we know from logs we have category types, use them
            if (this.labelTypes.categories && this.labelTypes.categories.length > 0) {
              this.labelTypes.categories.forEach(cat => {
                labels.push(cat.text)
                // We don't know exact distribution, so use even distribution
                data.push(Math.ceil(_item.categoryCount / this.labelTypes.categories.length))
              })
            } else {
              labels.push('Categories')
              data.push(_item.categoryCount)
            }
          } else {
            // No category data - show default
            return {
              labels: ['No Labels'],
              datasets: [{
                backgroundColor: ['#E0E0E0'],
                data: [1],
                barThickness: 20
              }]
            }
          }
        } else {
          // We have detailed label information - process it
          const labelCounts = {
            category: {},
            span: {},
            relation: {}
          }
          
          _item.labels.forEach(label => {
            const type = label.type || 'unknown'
            const id = label.label || 'unknown'
            
            if (!labelCounts[type]) {
              labelCounts[type] = {}
            }
            
            if (!labelCounts[type][id]) {
              labelCounts[type][id] = 0
            }
            
            labelCounts[type][id]++
          })
          
          // Try categories first
          let hasData = false
          if (this.labelTypes.categories && this.labelTypes.categories.length > 0) {
            Object.entries(labelCounts.category).forEach(([labelId, count]) => {
              const categoryType = this.labelTypes.categories.find(
                cat => cat.id.toString() === labelId.toString()
              )
              
              if (categoryType) {
                labels.push(categoryType.text)
                data.push(count)
                hasData = true
              }
            })
          }
          
          // If still no data, show placeholder
          if (!hasData) {
            return {
              labels: ['No Labels'],
              datasets: [{
                backgroundColor: ['#E0E0E0'],
                data: [1],
                barThickness: 20
              }]
            }
          }
        }
        
        return {
          labels,
          datasets: [{
            backgroundColor: colors.slice(0, labels.length),
            data,
            barThickness: 20
          }]
        }
      }
    }
  }
  </script>
  
  <style scoped>
  .v-card {
    margin-bottom: 1rem;
  }
  
  /* Make the chart container more visible */
  :deep(.chart-container) {
    height: 40px !important;
    width: 100% !important; 
    margin: 0 auto;
    background-color: #f9f9f9;
    border-radius: 3px;
    overflow: visible !important;
  }
  
  /* Make bars clearly visible */
  :deep(.chart-container canvas) {
    height: 40px !important;
    min-height: 40px !important;
    min-width: 60px !important;
  }
  </style>
